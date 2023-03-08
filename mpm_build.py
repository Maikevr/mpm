# -*- coding: utf-8 -*-
"""
Created on Tue Jan 10 16:55:56 2023

@author: rooij091
"""

import gurobipy as gp
from gurobipy import GRB
import pandas as pd
import numpy as np
import time
from mpm_supporting_functions import rewrite_buy


def menuplanning(settings, imported_data, name='menuplanning'): #let user decide with which variable to run this function
    start_time = time.time()
    # Model
    m = gp.Model("menuplanning")
    m.setParam('MIPFocus',1)
    m.setParam('Heuristics', 0.5)
    m.setParam('TimeLimit', 600)
    m.setParam('MIPGap', 0.25)
    
    # =============================================================================
    #     Unpacking inputs
    # =============================================================================
    n_days = settings["n_days"]
    n_persons = settings["n_persons"]
    dev = settings["dev"]
    optimize_over = settings["optimize_over"]
    
    ing_recipes = imported_data["ing_recipes_hoofd"]
    ing_LCA = imported_data["ing_LCA"]
    ing_packs = imported_data["ing_packs"]
    fcd = imported_data["fcd"]
    drv = imported_data["drv"]
    excep_codes = imported_data["excep_codes"]

    # =============================================================================
    #     Initializations of data
    # =============================================================================
    days = [str(x) for x in range(0, n_days+1)]
    recipes = ing_recipes.columns[1:]
    ingredients = ing_recipes.index.values[2:]
    packagesize = ing_packs["Package (g)"].unique()
    #eventually create a unique index for package ingredients combinations.
    #nutrients = drv.index.values # later aanpassen naar alle nutrients
    nutrients = fcd.columns.values[3:]
    
    # =============================================================================
    #     Decision variables
    # =============================================================================
    y = m.addVars(recipes, days, vtype=GRB.BINARY,name="y") #if recipe r is planned on day d or not
    buy = m.addVars(ingredients,packagesize, vtype=GRB.INTEGER,name="buy") #number of packages of size s to buy for ingerdients i (Only on )
    #z = m.addVars(ingredients,packagesize, vtype=GRB.INTEGER,name="z") #number of packages of size s to buy for ingerdients i (Only on )
    #yb = m.addVars(recipes, days, vtype=GRB.BINARY,name="yb") #if recipe r is planned on day d or not
    #
    
    #supporting variables
    x = m.addVars(ingredients, days, vtype=GRB.CONTINUOUS,name="x") #grams of ingredients i planned on day d
    stock = m.addVars(ingredients, days, vtype=GRB.CONTINUOUS,name="stock") #stock of ingredients i on day d
    #ik wil alleen een buy i,p aanmaken als deze bestaat. dus voor elke i zijn er maar een paar p's
    purchasecost_ing = m.addVars(ingredients, vtype=GRB.CONTINUOUS,name="purchasecost_ing")
    NIA = m.addVars(nutrients, days, vtype=GRB.CONTINUOUS, name="Nutrient Intake Absolute")
    NIAslack = m.addVars(nutrients, days, vtype=GRB.CONTINUOUS, name="Nutrient Intake Absolute slack variable")
    
    # =============================================================================
    #     Constraints
    # =============================================================================
    
    # Relax and fit: y variables
    #step 1: find for first two days
    #for d in days[1:3]:
        #m.addConstrs(y[r,d]-yb[r,d] == 0 for r in recipes)
    #step 2: fix the first two days
    m.addConstr(y[29,'1']==1)
    m.addConstr(y[477,'2']==1)
    
    # 2.1 One recipe planned per day
    for d in days[1:]: #for all days except the first (purchase day)
        m.addConstr((gp.quicksum(y[r,d] for r in recipes) == 1), "One recipe per day")
        
    # 2.2 Not twice the same recipe
    for r in recipes:
        m.addConstr((gp.quicksum(y[r,d] for d in days) <= 1), "Not twice the same recipe") 
        
    # 2.3 Constraint to add packages bought to stock
    for i in ingredients:
        nevoset = ing_packs.loc[ing_packs['nevocode'] == i]
        m.addConstr(stock[i,'0']== (gp.quicksum(buy[i,p]*p for p in nevoset["Package (g)"])), "buy packing size for recipe") #Ik verwacht dat p nu in grammen is
    
    # 2.3 Constraints to allow (very small) deviation to buy[i,p]
        # for p in nevoset["Package (g)"]:
        #     m.addConstr(buy[i,p] <= z[i,p] +0.01)
        #     m.addConstr(buy[i,p] >= z[i,p] -0.01)
    
    # 2.4 constraint to compute ingredients used for cooking per day  
    # 2.4.1 constraint to make sure that ingredients used for a day is substracted from ingredients on stock
    for d in range(len(days)):
        if d != 0:
            for i in ingredients: #kan dit mooier dan met 3 loops?                
                used = n_persons*gp.quicksum(ing_recipes.loc[i,r]*y[r,str(d)] for r in recipes)
                m.addConstr(x[i,str(d)] == used, "ingredients used for cooking per day")
                if i in excep_codes.index.values: #to make sure that for e.g. cooked couscous not too much raw couscous is bought
                    conversion = excep_codes.loc[i,"Conversion_factor"]
                    m.addConstr(stock[i,str(d)] == stock[i,str(d-1)]-used/conversion, "stock equation (exceptions)")
                else:
                    m.addConstr(stock[i,str(d)] == stock[i,str(d-1)]-used, "stock equation")
                
    # 2.4.2 constraint to compute total cost of the groceries per ingredient, change later to allow specific choices per package!!
    for i in ingredients:
        #Perishable items
        perishables = ing_packs.loc[ing_packs["Shelf_stable"]==0]
        nevoset_perishable = perishables.loc[ing_packs["nevocode"]==i]
        if len(nevoset_perishable) != 0:
            m.addConstr(purchasecost_ing[i] == (gp.quicksum(buy[i,p]*eur for p, eur in 
                        zip(nevoset_perishable["Package (g)"],nevoset_perishable["Package price (€/unit)"]))), 
                        "purchase cost of package sizes bought per ingredient, perishable items")
        #Shelf stable items
        stables = ing_packs.loc[ing_packs["Shelf_stable"]==1]
        nevoset_stables = stables.loc[ing_packs["nevocode"]==i]
        if len(nevoset_stables) != 0:
            cheapest = nevoset_stables[["Price (€/kg)"]].idxmin().item()
            packsize = int(nevoset_stables.loc[cheapest,"Package (g)"].item()) #size of the cheapest product
            #Don't buy packages that are not used
            for p in stables["Package (g)"]:
                if p != packsize:
                    m.addConstr(buy[i,p]==0,"Don't buy the more expensive packages")         
            #Don't buy more packages than necessary
            m.addConstr(buy[i,packsize] <= gp.quicksum(x[i,d] for d in days[1:])/packsize+1, "Upper bound for shelfstable packages") #make sure that not too many packages are bought. Right hand side always rounds up to the nearest integer of packaging size because of the plus 1.
            m.addConstr(buy[i,packsize] <= gp.quicksum(x[i,d] for d in days[1:]), "Don't buy if not used") #so if x=0 then buy=0
            #add costs 
            if i in excep_codes.index.values: #to make sure that for e.g. cooked couscous not too much raw couscous is bought
                conversion = excep_codes.loc[i,"Conversion_factor"]   
                m.addConstr(purchasecost_ing[i] == (gp.quicksum(x[i,d]/conversion for d in days[1:])
                                                    /1000*min(nevoset_stables["Price (€/kg)"])),"Purchase cost usage of stable items (exceptions)")
            else:
                m.addConstr(purchasecost_ing[i] == (gp.quicksum(x[i,d] for d in days[1:])
                                                /1000*min(nevoset_stables["Price (€/kg)"])),"Purchase cost usage of stable items")   

    # 2.5 Constraint to add DRVs        
    # compute NIA
    for d in days:
         for j in nutrients:
             m.addConstr(NIA[j,d] == gp.quicksum(x[i,d]*fcd.loc[i,j]/100 for i in ingredients),"Compute nutrient intake")
    
    # 2.5.1 constraint for the weekly nutrients
    for j in nutrients:
        if j in drv.index.values and drv.loc[j, "Daily or weekly nutrient"] == "weekly":
            m.addConstr(gp.quicksum(NIA[j,d]+NIAslack[j,d] for d in days[1:]) 
                        >= drv.loc[j,"ADH"]*n_persons*n_days*(1-dev), "Weekly nutrient constraint lowerbound") #Later adapt this for custom drvs
            if not np.isnan(drv.loc[j,"Bovengrens"]):
                m.addConstr(gp.quicksum(NIA[j,d]-NIAslack[j,d] for d in days[1:]) 
                            <= drv.loc[j,"Bovengrens"]*n_persons*n_days*(1+dev), "Weekly nutrient constraint upperbound")
    
    # 2.5.2 constraint for daily nutrient
    for j in nutrients:
        for d in days[1:]:
            if j in drv.index.values and drv.loc[j, "Daily or weekly nutrient"] == "daily":
                m.addConstr(NIA[j,d]+NIAslack[j,d] >= drv.loc[j,"ADH"]*n_persons*(1-dev), "Daily nutrient constraint lowerbound")
                if not np.isnan(drv.loc[j,"Bovengrens"]):
                    m.addConstr(NIA[j,d]-NIAslack[j,d] <= drv.loc[j,"Bovengrens"]*n_persons*(1+dev), "Daily nutrient constraint upperbound")

    # 2.5.3 enable this code to don't allow slack
    for j in nutrients:
        for d in days[1:]:
            m.addConstr(NIAslack[j,d] == 0, "don't allow slack")

    #==========================================================================
    #     Objective funcition    
    # =============================================================================
    
    perishables = ing_packs.loc[ing_packs["Shelf_stable"]==0]
    stables = ing_packs.loc[ing_packs["Shelf_stable"]==1]
    perish_set = [i for i in perishables["nevocode"].unique()]
    stable_set = [i for i in stables["nevocode"].unique()]
    
    # 1. Minimize carbon footprint
    tot_carbon_perishable = gp.quicksum(stock[i,"0"]*ing_LCA['GHGE_kg_CO2eq_per_kg'][i] 
                                        for i in perish_set)
    
    tot_carbon_stable = gp.quicksum(x[i,d]*ing_LCA['GHGE_kg_CO2eq_per_kg'][i] 
                                    for i in stable_set for d in days[1:])
    
    total_carbon = tot_carbon_perishable+ tot_carbon_stable
    
    
    # 2. Minimize waste in grams
    last_day = days[-1]
    waste_ingrams = gp.quicksum(stock[i,last_day] for i in perish_set)
    
    
    # 3. Minimize waste in carbon footprint 
    carbon_waste = gp.quicksum(stock[i,last_day]*ing_LCA['GHGE_kg_CO2eq_per_kg'][i] for i in perish_set) #computed by computing the environmental impact of the ingredients bought on day 1


    # 4. Minimize total cost of diet
    total_cost = gp.quicksum(purchasecost_ing[i] for i in ingredients)
    
    # =============================================================================
    #     Run the model
    # =============================================================================
    
    tiebreaker = 0.000001*total_carbon+0.000001*waste_ingrams+0.000001*carbon_waste+0.0001*total_cost 
    + 0.00001*gp.quicksum(NIAslack[j,d] for j in nutrients for d in days[1:]) 
    
    if optimize_over == 'Total_carbon':
         m.setObjective(total_carbon+tiebreaker, GRB.MINIMIZE)     #optimize over total_carbon or waste_ingrams or carbon waste
    elif optimize_over =='Waste_grams':
        m.setObjective(waste_ingrams+tiebreaker, GRB.MINIMIZE)
    elif optimize_over =='Carbon_waste':
        m.setObjective(carbon_waste+tiebreaker, GRB.MINIMIZE)
    elif optimize_over =='Total_cost':
        m.setObjective(total_cost+tiebreaker, GRB.MINIMIZE)
        
    init_time = time.time()
    print("---Initialisation time %s seconds ---" % (init_time - start_time))
    
    m.optimize()
    
    # =============================================================================
    #    Print solutions/ solution to dataframe 
    # =============================================================================
    
    def printSolution():
        if m.status == GRB.OPTIMAL:
            print('\nTotal carbon footprint of recipes for %s days:: %g g CO2 eq' % (days[-1], tot_carbon))
            for d in days:
                for r in recipes:
                    if y[r,d].X == 1:
                        recipe_id = ing_recipes.loc["recipe_id",r]
                        print("On day %s recipe: %s" % (d,recipe_id))
                        #print(tot_carbon_perishable)
                        #print(tot_carbon_stable)
        else:
            print('!!!!!!!Not optimal!!!!!!!!')

    def dfSolution_y():
        result_dict = {}
        for r in recipes:
            result_dict[r]={}
            for d in days:
                result_dict[r][d]=y[r,d].X
        planning =pd.DataFrame(result_dict)
        planning=planning.transpose()
        planning.index.name = "Recipe_num"
        return planning
    
    def dfSolution_x():
        result_dict = {}
        for i in ingredients:
            result_dict[i]={}
            for d in days:
                result_dict[i][d]=x[i,d].X
        planning_ingredients =pd.DataFrame(result_dict)
        planning_ingredients =planning_ingredients.transpose()
        planning_ingredients.index.name = 'nevocode'
        return planning_ingredients
    
    def dfSolution_buy():
        result_dict = {}
        for i in ingredients:
            result_dict[i]={}
            nevoset = ing_packs.loc[ing_packs['nevocode'] == i]
            for p in nevoset["Package (g)"]:
                result_dict[i][p]=buy[i,p].X
        purchase_planning =pd.DataFrame(result_dict)
        purchase_planning =purchase_planning.transpose()
        return purchase_planning
    
    def dfSolution_purchasecost():
        result_dict = {}
        for i in ingredients:
            result_dict[i]=purchasecost_ing[i].X
        #print(result_dict)
        purchase_costs =pd.DataFrame(result_dict,index=['cost in euros'])
        purchase_costs =purchase_costs.transpose()
        purchase_costs.index.name = 'nevocode'
        return purchase_costs
    
    def dfSolution_stock():
        result_dict = {}
        for i in ingredients:
            result_dict[i]={}
            for d in days:
                result_dict[i][d]=stock[i,d].X
        stock_planning =pd.DataFrame(result_dict)
        stock_planning =stock_planning.transpose()
        stock_planning.index.name = 'nevocode'
        return stock_planning
    
    def dfSolution_NIA():
        result_dict = {}
        for j in nutrients:
            result_dict[j]={}
            for d in days:
                result_dict[j][d] = round(NIA[j,d].X, 2)
        NIAsol =pd.DataFrame(result_dict)
        NIAsol =NIAsol.transpose()
        return NIAsol
    
    def dfSolution_NIAslack():
        result_dict = {}
        for j in nutrients:
            result_dict[j]={}
            for d in days:
                result_dict[j][d] = NIAslack[j,d].X
        NIAslacksol =pd.DataFrame(result_dict)
        NIAslacksol =NIAslacksol.transpose()
        return NIAslacksol

    
    #This block of code helps if it is not working
    #printSolution() 
    #print(m.status)
    #m.computeIIS()
    #m.write("model.ilp")
  
    #get the dataframes of the variables used
    planning_recipes=dfSolution_y() #formulates a dataframe of the solution
    planning_ingredients=dfSolution_x() #formulates a dataframe of the solution
    stock_planning = dfSolution_stock()
    purchase_planning = dfSolution_buy()
    purchase_planning = rewrite_buy(ing_packs, purchase_planning) #rewrite the info to the dataframe
    purchase_costs = dfSolution_purchasecost()
    NIAsol = dfSolution_NIA()
    NIAslacksol = dfSolution_NIAslack()

    var_result_dict = {"Planning_recipes":planning_recipes,"Planning_ingredients":planning_ingredients, 
                       "Stock_planning":stock_planning, 'Purchase_planning':purchase_planning, 
                       "Purchase_costs":purchase_costs, 'NIA':NIAsol, "NIAslack":NIAslacksol}
    
    #get the values of the LinExpr used
    tot_carbon = total_carbon.getValue()
    wast_ingrams= waste_ingrams.getValue()
    carbon_waste = carbon_waste.getValue()
    tot_cost = total_cost.getValue()
    
    obj_result_dict = {"Total_carbon":tot_carbon ,"Waste_grams":wast_ingrams,"Carbon_waste": carbon_waste, "Total_cost":tot_cost}
    
    objectivevalue = m.ObjVal
    
    printSolution()
    
    print("Model status = ",m.status)
    end_time = time.time()
    times = {"init_time":init_time-start_time,"total_time":end_time-start_time}
    print("---Initialisation time %s seconds ---" % (init_time - start_time))
    print("---Total computation time %s seconds ---" % (end_time - start_time))
    return var_result_dict, obj_result_dict,times