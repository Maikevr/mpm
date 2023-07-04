# -*- coding: utf-8 -*-
"""
Created on Thu Jan 12 16:04:39 2023

@author: rooij091

Hoe kan ik zoiets doen? Nested functions worden gebruikt in callfile dus dat gaat nu niet
"""
import pandas as pd
import gurobipy as gp
from gurobipy import GRB

def rewrite_buy(ing_packs, purchase_planning):
    groceries = []
    purchase_planning_ing_packs = ing_packs.copy(deep=True)
    for i,j in purchase_planning_ing_packs.iterrows():
    #for i,j in zip(purchase_planning_ing_packs.nevocode, purchase_planning_ing_packs["Package (g)"]):
        nevo = purchase_planning_ing_packs.loc[i,"nevocode"]
        pack = purchase_planning_ing_packs.loc[i,"pack_net_gr"]
        amount = purchase_planning.loc[nevo,pack]
        groceries += [abs(amount)]
    purchase_planning_ing_packs["buy"]=groceries
    return purchase_planning_ing_packs

#recipe number to recipe
def recipe(r):
    ing_recipes = pd.read_excel (r'C:\Users\rooij091\OneDrive - Wageningen University & Research\05. PhD project\Paper 1; reducing householdfood waste by meal plans\Data\Recipe data\recipe_standardised_df.xlsx', sheet_name='Sheet1', index_col=0)
    recipe_id = ing_recipes.loc["recipe_id",r]
    return recipe_id

#recipe to recipe number
def recipe_id(r):
    inpath = r"C:\Users\rooij091\OneDrive - Wageningen University & Research\05. PhD project\Paper 1; reducing householdfood waste by meal plans\2. Model input\22-03-2023\\"
    ing_recipes = pd.read_excel(inpath+'recipe_standardised_df_netto.xlsx', sheet_name='Sheet1', index_col=0)
    recipe_id=ing_recipes.loc[:,ing_recipes.loc["recipe_id"]==r].columns[0]
    return recipe_id

#nevocode to ingredient
def ingredient(nevocode):
    ing_recipes = pd.read_excel (r'C:\Users\rooij091\OneDrive - Wageningen University & Research\05. PhD project\Paper 1; reducing householdfood waste by meal plans\Data\Recipe data\recipe_standardised_df.xlsx', sheet_name='Sheet1', index_col=0)
    ing_name = ing_recipes.loc[nevocode, "nevonaam"]
    return ing_name

#package size and nevocode to index of package file
def indexpack(nevocode,package): #ing_packs already included
    ing_packs = pd.read_excel (r'C:\Users\rooij091\OneDrive - Wageningen University & Research\05. PhD project\Paper 1; reducing householdfood waste by meal plans\Data\Package data\package_info_standardised_2023-01-18.xlsx', sheet_name='Sheet1', index_col=0)
    index = ing_packs.loc[(ing_packs["nevocode"]==nevocode) & (ing_packs["Package (g)"]==package)].index.values[0]
    return index