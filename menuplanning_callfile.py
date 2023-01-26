# -*- coding: utf-8 -*-
"""
Created on Tue Jan 10 16:46:58 2023

@author: rooij091

This code calls menuplanningmodel.
"""
import pandas as pd
import numpy as np
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
fcd = pd.read_excel (r'C:\Users\rooij091\OneDrive - Wageningen University & Research\05. PhD project\Paper 1; reducing householdfood waste by meal plans\Data\Food Composition Database\FCD - Model input.xlsx', sheet_name='Sheet1', index_col=0)
drv = pd.read_excel (r'C:\Users\rooij091\OneDrive - Wageningen University & Research\05. PhD project\Paper 1; reducing householdfood waste by meal plans\Data\DRVs\DRVs - Model input.xlsx', sheet_name='Vrouw 31-39 jaar oud, gemiddeld', index_col=0)
ing_LCA = pd.read_excel (r'C:\Users\rooij091\OneDrive - Wageningen University & Research\05. PhD project\Paper 1; reducing householdfood waste by meal plans\Data\LCA data\20201111_LCA Food database_extrapolaties_milieudatabase_2020_V2.1.xlsx', sheet_name='LCA database inclusief extrapol', index_col=0)
ing_packs = pd.read_excel (r'C:\Users\rooij091\OneDrive - Wageningen University & Research\05. PhD project\Paper 1; reducing householdfood waste by meal plans\Data\Package data\package_info_standardised_2023-01-18.xlsx', sheet_name='Sheet1', index_col=0)
nevo_exceptions = pd.read_excel (r'C:\Users\rooij091\OneDrive - Wageningen University & Research\05. PhD project\Paper 1; reducing householdfood waste by meal plans\Data\Recipe data\NEVO_synonyms_exceptions.xlsx', sheet_name='Sheet1', index_col=0)
# =============================================================================
# Prepare data
# =============================================================================
ing_recipes_hoofd = ing_recipes.loc[:, ing_recipes.loc['mealmoment'] == 'hoofdgerecht'] #subset of dishes that are a main meal
ing_recipes_hoofd = ing_recipes_hoofd.iloc[:,:] #small subset for tests

drv = drv.replace("-",np.nan)
drv = drv.loc[["Eiwit (g)","Calcium (mg)","IJzer (mg)", "Zink (mg)", "RAE (Vit A) (µg)",
              "Vit B1  (mg)", "Vit B2 (mg)","Vitamine B3 (mg) ", "Vitamine B6 (mg)",
              "Folaat equiv (µg)", "Vit B12 (µg)"],:]

excep_codes = nevo_exceptions[nevo_exceptions["Account_pack_size"]==0]


# =============================================================================
# Run model
# =============================================================================
optimize_over="waste grams" #total carbon, waste carbon, waste grams, total cost
var_result_dict, obj_result_dict = menuplanning(n_days, n_persons, ing_recipes_hoofd, 
                                                ing_LCA, ing_packs, optimize_over, fcd,
                                                drv, excep_codes)

# =============================================================================
# Store results
# =============================================================================
planning_recipes = var_result_dict["Planning_recipes"]
planning_ingredients = var_result_dict["Planning_ingredients"]
stock_planning = var_result_dict["Stock_planning"]
purchase_planning = var_result_dict["Purchase_planning"]
purchase_costs = var_result_dict["Purchase_costs"]
wast_ingrams = obj_result_dict["Waste_in_grams"]

# =============================================================================
# Result analyses
# =============================================================================
perishables = ing_packs.loc[ing_packs["Shelf_stable"]==0]
perish_set = [i for i in perishables["nevocode"].unique()]
perish_stock = stock_planning[stock_planning.index.isin(perish_set)]