# -*- coding: utf-8 -*-
"""
Created on Tue Jan 10 16:46:58 2023

@author: rooij091

This code calls menuplanningmodel.
"""
import pandas as pd
import numpy as np
from mpm_build import menuplanning
from mpm_excelwriter import sol_toexcel
import sys
sys.path.insert(0, r'C:\Users\rooij091\OneDrive - Wageningen University & Research\05. PhD project\Paper 1; reducing householdfood waste by meal plans\Data\DRVs')
from preprocessing_ps import preprocessing_ps

# ----------------------------------------------------------------------------
# Initialize the problem data
# ----------------------------------------------------------------------------
n_days = 5 # for how many days do you want to make a planning?
n_persons = 4
dev = 0.1 #allow for x% deviation of the DRVs
optimize_over="Waste_grams" #Carbon_waste, Total_carbon, Total_cost, Waste_grams
drv_settings="modelgezin_gemiddeld"

settings = {"n_days":n_days, "n_persons": n_persons, "dev": dev, "optimize_over": optimize_over}


# ----------------------------------------------------------------------------
# Import files
# ----------------------------------------------------------------------------
ing_recipes = pd.read_excel (r'C:\Users\rooij091\OneDrive - Wageningen University & Research\05. PhD project\Paper 1; reducing householdfood waste by meal plans\Data\Recipe data\recipe_standardised_df.xlsx', sheet_name='Sheet1', index_col=0)
ing_recipes_ps = pd.read_pickle(r'C:\Users\rooij091\OneDrive - Wageningen University & Research\05. PhD project\Paper 1; reducing householdfood waste by meal plans\Data\DRVs\ing_recipes_ps.pkl')
fcd = pd.read_excel (r'C:\Users\rooij091\OneDrive - Wageningen University & Research\05. PhD project\Paper 1; reducing householdfood waste by meal plans\Data\Food Composition Database\FCD - Model input.xlsx', sheet_name='Sheet1', index_col=0)
#moeder - drv = pd.read_excel (r'C:\Users\rooij091\OneDrive - Wageningen University & Research\05. PhD project\Paper 1; reducing householdfood waste by meal plans\Data\DRVs\DRVs - Model input.xlsx', sheet_name='Vrouw 31-39 jaar oud, gemiddeld', index_col=0)
drv = pd.read_excel (r'C:\Users\rooij091\OneDrive - Wageningen University & Research\05. PhD project\Paper 1; reducing householdfood waste by meal plans\Data\DRVs\DRVs - Model input.xlsx', sheet_name='modelgezin_gemiddeld', index_col=0)
ing_LCA = pd.read_excel (r'C:\Users\rooij091\OneDrive - Wageningen University & Research\05. PhD project\Paper 1; reducing householdfood waste by meal plans\Data\LCA data\20201111_LCA Food database_extrapolaties_milieudatabase_2020_V2.1.xlsx', sheet_name='LCA database inclusief extrapol', index_col=0)
ing_packs = pd.read_excel (r'C:\Users\rooij091\OneDrive - Wageningen University & Research\05. PhD project\Paper 1; reducing householdfood waste by meal plans\Data\Package data\package_info_standardised_2023-01-18.xlsx', sheet_name='Sheet1', index_col=0)
nevo_exceptions = pd.read_excel (r'C:\Users\rooij091\OneDrive - Wageningen University & Research\05. PhD project\Paper 1; reducing householdfood waste by meal plans\Data\Recipe data\NEVO_synonyms_exceptions.xlsx', sheet_name='Sheet1', index_col=0)

# =============================================================================
# Prepare data
# =============================================================================

#The following line uses a custom adjusted portion size file as input!!
#ing_recipes_ps = preprocessing_ps(ing_recipes, fcd, drv, drv_settings, n_persons)
ing_recipes_hoofd = ing_recipes_ps.loc[:, ing_recipes.loc['mealmoment'] == 'hoofdgerecht'] #subset of dishes that are a main meal


drv = drv.replace("-",np.nan)
drv = drv.loc[["Eiwit (g)","Calcium (mg)","IJzer (mg)", "Zink (mg)", "RAE (Vit A) (µg)",
              "Vit B1  (mg)", "Vit B2 (mg)", "Folaat equiv (µg)", "Vit B12 (µg)"],:]

excep_codes = nevo_exceptions[nevo_exceptions["Account_pack_size"]==0]

imported_data = {"ing_recipes_hoofd": ing_recipes_hoofd, "ing_recipes_full": ing_recipes,
                 "ing_LCA": ing_LCA, "ing_packs": ing_packs, "fcd": fcd, 
                 "drv":drv, "excep_codes": excep_codes}

# =============================================================================
# Run model
# =============================================================================
var_result_dict, obj_result_dict, times = menuplanning(settings, imported_data)

# =============================================================================
# Write results to excel
# =============================================================================
sol_toexcel(settings, imported_data, obj_result_dict, var_result_dict, times)

# =============================================================================
# Store results locally
# =============================================================================
planning_recipes = var_result_dict["Planning_recipes"]
planning_ingredients = var_result_dict["Planning_ingredients"]
stock_planning = var_result_dict["Stock_planning"]
purchase_planning = var_result_dict["Purchase_planning"]
purchase_costs = var_result_dict["Purchase_costs"]
wast_ingrams = obj_result_dict["Waste_grams"]

# =============================================================================
# Result analyses
# =============================================================================
perishables = ing_packs.loc[ing_packs["Shelf_stable"]==0]
perish_set = [i for i in perishables["nevocode"].unique()]
perish_stock = stock_planning[stock_planning.index.isin(perish_set)]