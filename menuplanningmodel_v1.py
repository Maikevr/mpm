# -*- coding: utf-8 -*-
"""
Created on Thu Jul 21 12:01:38 2022

@author: rooij091
"""

import numpy as np
import gurobipy as gp
from gurobipy import GRB

import pandas as pd

# ----------------------------------------------------------------------------
# Import files
# ----------------------------------------------------------------------------
ingredients_recipes = pd.read_excel (r'Menu_planning_model_data_v1.xlsx', sheet_name='ingredients_recipes_1pers', skiprows=2, index_col=0)
#print (ingredients_recipes)

ingredients_LCA = pd.read_excel (r'Menu_planning_model_data_v1.xlsx', sheet_name='ingredients_LCA', skiprows=4, index_col=0)
#print (ingredients_LCA)

ingredients_packing = pd.read_excel (r'Menu_planning_model_data_v1.xlsx', sheet_name='ingredients_packing', skiprows=4, index_col=0)
#print (ingredients_packing)

ingredients_shelfstable = pd.read_excel (r'Menu_planning_model_data_v1.xlsx', sheet_name='ingredients_shelfstable', skiprows=2, index_col=0, index=['shelfstable','notes'])
#print (ingredients_shelfstable)

carbon_recipe_ing = ingredients_recipes.mul(ingredients_LCA['Global warming kg CO2 eq'], axis=0)
#carbon_recipe = carbon_recipe_ing.sum()


# ----------------------------------------------------------------------------
# Initialize the problem data
# ----------------------------------------------------------------------------
number_days = 5 # for how many days do you want to make a planning?
number_persons = 4

packages = () #make sure that the price/package size data per ingredient is in a dictionairy with lists.
package_dict = {}
for i, row in ingredients_packing.iterrows():
    #print(i)
    if i not in package_dict:
        package_dict[i] = [[row[0],row[1],row[2]]] # [grams in package, package price, kg price]
    else:
        package_dict[i] += [[row[0],row[1],row[2]]]

recipes = ingredients_recipes.keys()
days = [str(x) for x in range(0, number_days+1)]
ingredients = ingredients_LCA.index.values
packagesize = range(70)

# ----------------------------------------------------------------------------
# Build the model
# ----------------------------------------------------------------------------

def build_diet_model(optimize_over, name='diet', **kwargs): #let user decide with which variable to run this function
    # Model
    m = gp.Model("diet")
    
# =============================================================================
#     # Decision variables
# =============================================================================
    y = m.addVars(recipes, days, vtype=GRB.BINARY,name="y") #if recipe r is planned on day d or not
    x = m.addVars(ingredients, days, vtype=GRB.CONTINUOUS,name="x") #grams of ingredients i planned on day d
    stock = m.addVars(ingredients, days, vtype=GRB.CONTINUOUS,name="stock") #stock of ingredients i on day d
    buy = m.addVars(ingredients,packagesize, vtype=GRB.INTEGER,name="buy") #number of packages of size s to buy for ingerdients i (Only on )
    purchasecost_ing = m.addVars(ingredients, vtype=GRB.CONTINUOUS,name="purchasecost_ing")
    
# =============================================================================
#     Constraints
# =============================================================================
    # One recipe planned per day
    for d in days[1:]: #for all days except the first (purchase day)
        m.addConstr((gp.quicksum(y[r,d] for r in recipes) == 1), "One recipe per day")
        
    # Not twice the same recipe
    for r in recipes:
        m.addConstr((gp.quicksum(y[r,d] for d in days) <= 1), "Not twice the same recipe") 
        
    #constraint to add packages bought to stock
    for i in ingredients:
        m.addConstr(stock[i,'0']== (gp.quicksum(buy[i,p]*package_dict[i][p][0] for p in range(len(package_dict[i])))), "buy packing size for recipe") #welke packing size dan #[0] is package size in grams
    
    #constraint to compute ingredients used for cooking per day  
    #constraint to make sure that ingredients used for a day is substracted from ingredients on stock
    for di in range(len(days)):
        if di != 0:
            for i in ingredients: #kan dit mooier dan met 3 loops?
                used = number_persons*gp.quicksum(ingredients_recipes.at[i,r]*y[r,str(di)] for r in recipes)
                m.addConstr(x[i,str(di)] == used, "ingredients used for cooking per day")
                m.addConstr(stock[i,str(di)] == stock[i,str(di-1)]-used, "stock equation")
                
    #constraint to compute total cost of the groceries per ingredient
    for i in ingredients:
        if ingredients_shelfstable['Shelf stable?'][i] == 0:
            m.addConstr(purchasecost_ing[i] == (gp.quicksum(buy[i,p]*package_dict[i][p][1] for p in range(len(package_dict[i])))), "purchase cost of package sizes bought per ingredient") #[1] is package price
        else:
            #m.addConstr(purchasecost_ing[i] == ((gp.quicksum(buy[i,p]*package_dict[i][p][0]*package_dict[i][p][2] for p in range(len(package_dict[i]))))/(gp.quicksum(buy[i,p]*package_dict[i][p][0] for p in range(len(package_dict[i]))))), "purchase cost of package sizes bought per ingredient") #[1] is package price
            #m.addConstr(purchasecost_ing[i] == ((gp.quicksum(buy[i,p]*package_dict[i][p][0]*package_dict[i][p][2] for p in range(len(package_dict[i])))*, "purchase cost of package sizes bought per ingredient")
            #m.addConstr(purchasecost_ing[i] == (gp.quicksum(ingredients_recipes.at[i,r]*y[r,d]for d in days[1:] for r in recipes)/1000*package_dict[i][-1][2]))       
            m.addConstr(purchasecost_ing[i] == (gp.quicksum(x[i,d]for d in days[1:])/1000*package_dict[i][-1][2]))       

    #m.computeIIS() #used if infeasible to check which constraints are infeasible
    #m.write('mymodel.ilp')

      
# =============================================================================
#     Objective funcition    
# =============================================================================
    # Minimize carbon footprint !MAKE THIS ONE MORE CLEAR!
    total_carbon = 1000* gp.quicksum(stock[i,'0']/1000*ingredients_LCA['Global warming kg CO2 eq'][i] for i in ingredients if ingredients_shelfstable['Shelf stable?'][i]==0)  \
                + 1000* gp.quicksum(ingredients_recipes.at[i,r]*y[r,d]/1000*ingredients_LCA['Global warming kg CO2 eq'][i] for d in days[1:] for r in recipes for i in ingredients if ingredients_shelfstable['Shelf stable?'][i]==1) #so impact of perishable items bought plus impact of shelf-stable items used
    
    # Minimize waste in grams
    last_day = days[-1]
    
    # Ik denk dat dit nu hetzelfde werkt
    waste_ingrams = gp.quicksum(stock[i,last_day] for i in ingredients if ingredients_shelfstable['Shelf stable?'][i]==0 )
    # waste_ingrams = 0
    # #print('test  '+str(waste_ingrams))
    # for i in ingredients:
    #     if ingredients_shelfstable['Shelf stable?'][i] == 0:
    #         waste_ingrams += stock[i,last_day]

    # Minimize waste in carbon footprint #Berekend kg CO2 en doet het dan keer 1000 om gram CO2 te bepalen
    carbon_waste = 1000*gp.quicksum(stock[i,last_day]/1000*ingredients_LCA['Global warming kg CO2 eq'][i] for i in ingredients if ingredients_shelfstable['Shelf stable?'][i]==0) #computed by computing the environmental impact of the ingredients bought on day 1

    # Minimize total cost of diet
    total_cost = gp.quicksum(purchasecost_ing[i] for i in ingredients)
    
    tiebreaker = 0.000001*total_carbon+0.000001*waste_ingrams+0.000001*carbon_waste+0.0001*total_cost
    
    if optimize_over == 'total carbon':
         m.setObjective(total_carbon+tiebreaker, GRB.MINIMIZE)     #optimize over total_carbon or waste_ingrams or carbon waste
    elif optimize_over =='waste grams':
        m.setObjective(waste_ingrams+tiebreaker, GRB.MINIMIZE)
    elif optimize_over =='waste carbon':
        m.setObjective(carbon_waste+tiebreaker, GRB.MINIMIZE)
    elif optimize_over =='total cost':
        m.setObjective(total_cost+tiebreaker, GRB.MINIMIZE)
   
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
            print('No solution')
    
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
            for p in range(len(package_dict[i])):
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

    #printSolution() #prints the solution
    
    #get the dataframes of the variables used
    planning_recipes=dfSolution_y() #formulates a dataframe of the solution
    planning_ingredients=dfSolution_x() #formulates a dataframe of the solution
    stock_planning = dfSolution_stock()
    purchase_planning = dfSolution_buy()
    purchase_costs = dfSolution_purchasecost()
    
    #get the values of the LinExpr used
    tot_carbon = total_carbon.getValue()
    wast_ingrams= waste_ingrams.getValue()
    carbon_waste = carbon_waste.getValue()
    
    objectivevalue = m.ObjVal
    
    return objectivevalue, planning_recipes, planning_ingredients, stock_planning, purchase_planning, wast_ingrams, carbon_waste, tot_carbon, purchase_costs
    
    #stop deze hele lijst in een dictionary om terug te gooien.

        
if __name__ == '__main__':
    #optimize_over = total_carbon #input('total_carbon, waste_ingrams, carbon_waste')
    optimize_over = input("Do you want to optimise on 'total carbon', 'waste grams', 'waste carbon', 'total cost'?\n")
    objectivevalue, planning_recipes, planning_ingredients, stock_planning, purchase_planning, waste_ingrams, carbon_waste, total_carbon, purchase_costs =build_diet_model(optimize_over)
    
    #last_day = days[-1]
    #ste grawaste_ingrams = stock_planning[last_day].sum()
    #print(purchase_costs)
    
    #Printing solution values to console
    print('\n------------------------------------')
    print('Optimized for: '+optimize_over)
    print('Planning formulated for: ' + days[-1] + ' days and for: ' + str(number_persons) + ' persons')
    print('Waste in grams is = '+ str(round(waste_ingrams,2)) + ' grams')
    print('Waste in co2 is = '+ str(round(carbon_waste,2)) + ' grams co2')
    print('Total co2 is = '+ str(round(total_carbon,2)) + ' grams co2')
    print('Total cost is = '+ str(round(purchase_costs['cost in euros'].sum(),2)) + ' euros')
    
    print('\nObjective function (obj+tiebreaker) = '+ str(round(objectivevalue,2)))
    #carbon_waste = stock
    
