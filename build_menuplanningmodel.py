# -*- coding: utf-8 -*-
"""
Created on Tue Jan 10 16:55:56 2023

@author: rooij091
"""

import gurobipy as gp
from gurobipy import GRB
import pandas as pd
import time



def menuplanning(n_days, n_persons, ing_recipes, ing_LCA, ing_packs, name='menuplanning'): #let user decide with which variable to run this function
    start_time = time.time()
    # Model
    m = gp.Model("menuplanning")
    
    # =============================================================================
    #     Initializations of data
    # =============================================================================
    days = [str(x) for x in range(0, n_days+1)]
    recipes = ing_recipes.columns[1:]
    ingredients = ing_recipes.index.values[2:]
    packagesize = range(5001)
    
    # =============================================================================
    #     Decision variables
    # =============================================================================
    y = m.addVars(recipes, days, vtype=GRB.BINARY,name="y") #if recipe r is planned on day d or not
    x = m.addVars(ingredients, days, vtype=GRB.CONTINUOUS,name="x") #grams of ingredients i planned on day d
    stock = m.addVars(ingredients, days, vtype=GRB.CONTINUOUS,name="stock") #stock of ingredients i on day d
    #ik wil alleen een buy i,p aanmaken als deze bestaat. dus voor elke i zijn er maar een paar p's
    buy = m.addVars(ingredients,packagesize, vtype=GRB.INTEGER,name="buy") #number of packages of size s to buy for ingerdients i (Only on )
    purchasecost_ing = m.addVars(ingredients, vtype=GRB.CONTINUOUS,name="purchasecost_ing")
    
    # =============================================================================
    #     Constraints
    # =============================================================================
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
    
    # 2.4 constraint to compute ingredients used for cooking per day  
    # 2.4.1 constraint to make sure that ingredients used for a day is substracted from ingredients on stock
    for di in range(len(days)):
        if di != 0:
            for i in ingredients: #kan dit mooier dan met 3 loops?
                used = n_persons*gp.quicksum(ing_recipes.loc[i,r]*y[r,str(di)] for r in recipes)
                m.addConstr(x[i,str(di)] == used, "ingredients used for cooking per day")
                m.addConstr(stock[i,str(di)] == stock[i,str(di-1)]-used, "stock equation")
       
    # 2.4.2 constraint to compute total cost of the groceries per ingredient
    for i in ingredients:
        nevoset = ing_packs.loc[ing_packs['nevocode'] == i]
        m.addConstr(purchasecost_ing[i] == (gp.quicksum(buy[i,p]*eur for p, eur in zip(nevoset["Package (g)"],nevoset["Package price (€/unit)"]))), "purchase cost of package sizes bought per ingredient") #   

    
    
    # =============================================================================
    #     Objective funcition    
    # =============================================================================
    # Minimize carbon footprint !MAKE THIS ONE MORE CLEAR!
    total_carbon = gp.quicksum(stock[i,'0']/1000 * ing_LCA['GHGE_kg_CO2eq_per_kg'][i] for i in ingredients[:-2]) #skip overig  
    
    # Minimize waste in grams
    last_day = days[-1]
    waste_ingrams = gp.quicksum(stock[i,last_day] for i in ingredients)
    
    # Minimize waste in carbon footprint #Berekend kg CO2
    carbon_waste = gp.quicksum(stock[i,last_day]/1000*ing_LCA['GHGE_kg_CO2eq_per_kg'][i] for i in ingredients[:-2 ]) #computed by computing the environmental impact of the ingredients bought on day 1

    # Minimize total cost of diet
    total_cost = gp.quicksum(purchasecost_ing[i] for i in ingredients)
    
    m.setObjective(waste_ingrams, GRB.MINIMIZE)
    m.optimize()
    
    # =============================================================================
    #    Print solutions/ solution to dataframe 
    # =============================================================================
    
    def printSolution():
        if m.status == GRB.OPTIMAL:
            print('\nTotal carbon footprint of recipes for %s days:: %g g CO2 eq' % (days[-1], m.ObjVal))
            for r in recipes:
                for d in days:
                    print("Recipe %s on day %s: %g" % (r, d, y[r,d].X))       
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
        return planning
    
    def dfSolution_x():
        result_dict = {}
        for i in ingredients:
            result_dict[i]={}
            for d in days:
                result_dict[i][d]=x[i,d].X
        planning_ingredients =pd.DataFrame(result_dict)
        planning_ingredients =planning_ingredients.transpose()
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
        return purchase_costs
    
    def dfSolution_stock():
        result_dict = {}
        for i in ingredients:
            result_dict[i]={}
            for d in days:
                result_dict[i][d]=stock[i,d].X
        stock_planning =pd.DataFrame(result_dict)
        stock_planning =stock_planning.transpose()
        return stock_planning

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
    purchase_costs = dfSolution_purchasecost()
    
    var_result_dict = {"Planning_recipes":planning_recipes,"Planning_ingredients":planning_ingredients, "Stock_planning":stock_planning, 'Purchase_planning':purchase_planning, "Purchase_costs":purchase_costs}
    
    #get the values of the LinExpr used
    tot_carbon = total_carbon.getValue()
    wast_ingrams= waste_ingrams.getValue()
    carbon_waste = carbon_waste.getValue()
    tot_cost = total_cost.getValue()
    
    obj_result_dict = {"Total_carbon":tot_carbon ,"Waste_in_grams":wast_ingrams,"Carbon_waste": carbon_waste, "Total_cost":tot_cost}
    
    objectivevalue = m.ObjVal
    
    print("Model status = ",m.status)
    print("--- %s seconds ---" % (time.time() - start_time))
    return var_result_dict, obj_result_dict