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
        pack = purchase_planning_ing_packs.loc[i,"Package (g)"]
        amount = purchase_planning.loc[nevo,pack]
        groceries += [abs(amount)]
    purchase_planning_ing_packs["buy"]=groceries
    return purchase_planning_ing_packs