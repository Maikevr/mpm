# -*- coding: utf-8 -*-
"""
Created on Tue Jan 10 16:46:58 2023

@author: rooij091

This code calls menuplanningmodel.
"""
import pandas as pd
from menuplanningmodel_build import menuplanning

# ----------------------------------------------------------------------------
# Initialize the problem data
# ----------------------------------------------------------------------------
n_days = 5 # for how many days do you want to make a planning?
n_persons = 4

# ----------------------------------------------------------------------------
# Import files
# ----------------------------------------------------------------------------
ing_recipes = pd.read_excel (r'C:\Users\rooij091\OneDrive - Wageningen University & Research\05. PhD project\Paper 1; reducing householdfood waste by meal plans\Data\Recipe data\recipe_standardised_df.xlsx', sheet_name='Sheet1', index_col=0)
ing_recipes = ing_recipes.iloc[:, :20]
ing_LCA = pd.read_excel (r'C:\Users\rooij091\OneDrive - Wageningen University & Research\05. PhD project\Paper 1; reducing householdfood waste by meal plans\Data\LCA data\20201111_LCA Food database_extrapolaties_milieudatabase_2020_V2.1.xlsx', sheet_name='LCA database inclusief extrapol', index_col=0)
ing_packs = pd.read_excel (r'C:\Users\rooij091\OneDrive - Wageningen University & Research\05. PhD project\Paper 1; reducing householdfood waste by meal plans\Data\Package data\package_info_standardised_2023-01-06.xlsx', sheet_name='Sheet1', index_col=0)

# =============================================================================
# Run model
# =============================================================================
var_result_dict, obj_result_dict = menuplanning(n_days, n_persons, ing_recipes, ing_LCA, ing_packs)

# =============================================================================
# Store results
# =============================================================================
planning_recipes = var_result_dict["Planning_recipes"]
planning_ingredients = var_result_dict["Planning_ingredients"]
stock_planning = var_result_dict["Stock_planning"]
purchase_planning = var_result_dict["Purchase_planning"]
purchase_costs = var_result_dict["Purchase_costs"]

wast_ingrams = obj_result_dict["Waste_in_grams"]