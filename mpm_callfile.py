# -*- coding: utf-8 -*-
"""
Created on Tue Jan 10 16:46:58 2023

@author: rooij091

This code loads data and calls menuplanningmodel.
"""

import pandas as pd
import numpy as np
from mpm_build import menuplanning
from mpm_excelwriter import sol_toexcel
import sys
#sys.path.insert(1, r"C:\Users\rooij091\OneDrive - Wageningen University & Research\05. PhD project\Paper 1; reducing householdfood waste by meal plans\1. Data\DRVs\\")
# from Recipecheck import recipe_nutrientcontent
# from preprocessing_ps import preprocessing_ps
# from Analyses_functions.stepwise_reduction import stepwise_reduction_waste, stepwise_reduction_carbon
# from Analyses_functions.household_size import household_size
from Analyses_functions.all_obj_table import all_obj_table

# ----------------------------------------------------------------------------
# Import files
# ----------------------------------------------------------------------------
#Input data date: 22-03-2023. Change path if other input folder is desired
#inpath = r"C:\Users\rooij091\OneDrive - Wageningen University & Research\05. PhD project\Paper 1; reducing householdfood waste by meal plans\2. Model input\22-03-2023\\"
inpath = r"Model_input\22-03-2023\\"

ing_recipes = pd.read_excel(inpath+'recipe_standardised_df_netto.xlsx', sheet_name='Sheet1', index_col=0)
ing_recipes_ps = pd.read_pickle(inpath+'ing_recipes_ps_netto.pkl') #Already made preprocessing portion step. Used instead of ing_recipes.

fcd = pd.read_excel(inpath+'FCD - Model input.xlsx', sheet_name='Sheet1', index_col=0)
drv_full = pd.read_excel(inpath+'DRVs - Model input.xlsx', sheet_name='modelgezin_gemiddeld_gap', index_col=0) #TODO
ing_LCA = pd.read_excel(inpath+'20201111_LCA Food database_extrapolaties_milieudatabase_2020_V2.1.xlsx', sheet_name='LCA database inclusief extrapol', index_col=0)
ing_packs = pd.read_excel(inpath+'package_info_standardised_2023-01-18_edible.xlsx', sheet_name='Sheet1', index_col=0)
nevo_exceptions = pd.read_excel(inpath+'NEVO_synonyms_exceptions.xlsx', sheet_name='Sheet1', index_col=0)

#Set up an experiment sheet
#run_settings = pd.read_excel(r'run_settings.xlsx', sheet_name='menus', index_col=0)  #TODO

# =============================================================================
# Prepare data
# =============================================================================
ing_recipes_hoofd = ing_recipes_ps.loc[:, ing_recipes_ps.loc['mealmoment'] == 'hoofdgerecht'] #subset of dishes that are a main meal

ing_recipes_hoofd.insert(0, column="nevonaam", value=ing_recipes["nevonaam"]) #return ingredient labels

drv = drv_full.replace("-",np.nan)
drv = drv.loc[["kcal (kcal)", "Calcium (mg)","IJzer (mg)", "Zink (mg)", "RAE (Vit A) (µg)",
              "Vit B1  (mg)", "Vit B2 (mg)", "Folaat equiv (µg)", "Vit B12 (µg)", "Vit C (mg)"],:]

eaten = []

excep_codes = nevo_exceptions[nevo_exceptions["Account_pack_size"]==0]

imported_data = {"ing_recipes_hoofd": ing_recipes_hoofd,
                 "ing_LCA": ing_LCA, "ing_packs": ing_packs, "fcd": fcd, 
                 "drv":drv, "excep_codes": excep_codes}


# ----------------------------------------------------------------------------
# Model settings and run
# ----------------------------------------------------------------------------
manual_run = True #TODO

if manual_run:
    n_days = 4 # for how many days do you want to make a planning?
    n_persons = 3 # for how many persons?
    dev = 0.1 #allow for x% deviation of the DRVs
    optimize_over="Waste_grams" #Carbon_waste, Total_ghge, Total_cost, Waste_grams, Total_landuse
    drv_settings="modelgezin_gemiddeld_gap"
    tvar1 = 9999
    
    settings = {"n_days":n_days, "n_persons": n_persons, "dev": dev, 
                "optimize_over": optimize_over, "tvar1": tvar1, "eaten": eaten}

    #RUN MODEL
    var_result_dict, obj_result_dict, times = menuplanning(settings, imported_data)
    
    #WRITE RESULTS TO EXCEL
    sol_toexcel(settings, imported_data, obj_result_dict, var_result_dict, times)

else: #series run as specified in run_settings
    listlists= []
    raw_output = {"run_id":[], "settings":[],"obj_result_dict":[], "times": []}
    for run, row in run_settings.iterrows():
        settings = {"n_days":row["n_days"], "n_persons": row["n_persons"], 
                    "dev": row["dev"], "optimize_over": row["optimize_over"],
                    "DRVs":row["DRVs"], "tvar1":row["tvar1"], "tvar2":row["tvar2"], "eaten":eaten}
        
        with open('run_id.txt') as count_file:
            run_id = int(count_file.read())

        #RUN MODEL
        var_result_dict, obj_result_dict, times = menuplanning(settings, imported_data)
        
        #WRITE RESULTS TO EXCEL
        sol_toexcel(settings, imported_data, obj_result_dict, var_result_dict, times)
        
        #ANALYSES #misschien obj_result_dict maken
        raw_output["run_id"] += [run_id]
        raw_output["settings"] += [settings]
        raw_output["obj_result_dict"] += [obj_result_dict]
        raw_output["times"] += [times]
        
        listlists += [[str(run_id), row["tvar1"], obj_result_dict["Total_ghge"], obj_result_dict["Waste_grams"], times["total_time"]]]
    
        eaten += var_result_dict["eaten"] 

    all_obj_df = all_obj_table(raw_output) #TODO
