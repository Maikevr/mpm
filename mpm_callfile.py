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
sys.path.insert(1, r"C:\Users\rooij091\OneDrive - Wageningen University & Research\05. PhD project\Paper 1; reducing householdfood waste by meal plans\1. Data\DRVs\\")
from Recipecheck import recipe_nutrientcontent
from preprocessing_ps import preprocessing_ps
from Analyses_functions.stepwise_reduction import stepwise_reduction_waste, stepwise_reduction_carbon
from Analyses_functions.household_size import household_size
from Analyses_functions.all_obj_table import all_obj_table
# ----------------------------------------------------------------------------
# Import files
# ----------------------------------------------------------------------------

#Input data date: 22-03-2022. Change path if other input folder is desired
inpath = r"C:\Users\rooij091\OneDrive - Wageningen University & Research\05. PhD project\Paper 1; reducing householdfood waste by meal plans\2. Model input\22-03-2023\\"

ing_recipes = pd.read_excel(inpath+'recipe_standardised_df_netto.xlsx', sheet_name='Sheet1', index_col=0)
ing_recipes_ps = pd.read_pickle(inpath+'ing_recipes_ps_netto.pkl') #Already made preprocessing portion step. Used instead of ing_recipes.

#ing_recipes_ps = pd.read_pickle(inpath+'ing_recipes_ps_netto_drv572_dev015.pkl') #Already made preprocessing portion step. Used instead of ing_recipes.


fcd = pd.read_excel(inpath+'FCD - Model input.xlsx', sheet_name='Sheet1', index_col=0)
drv_full = pd.read_excel(inpath+'DRVs - Model input.xlsx', sheet_name='modelgezin_gemiddeld_gap', index_col=0) #TODO
ing_LCA = pd.read_excel(inpath+'20201111_LCA Food database_extrapolaties_milieudatabase_2020_V2.1.xlsx', sheet_name='LCA database inclusief extrapol', index_col=0)
ing_packs = pd.read_excel(inpath+'package_info_standardised_2023-01-18_edible.xlsx', sheet_name='Sheet1', index_col=0)
nevo_exceptions = pd.read_excel(inpath+'NEVO_synonyms_exceptions.xlsx', sheet_name='Sheet1', index_col=0)

#Changing this sheet changes the experiment done
run_settings = pd.read_excel(r'run_settings.xlsx', sheet_name='Stepwise_reduction_waste', index_col=0)  #TODO

# =============================================================================
# Prepare data
# =============================================================================

#The following line uses a custom adjusted portion size file as input!!
#ing_recipes_ps = preprocessing_ps(ing_recipes, fcd, drv, drv_settings, n_persons)
ing_recipes_hoofd = ing_recipes_ps.loc[:, ing_recipes_ps.loc['mealmoment'] == 'hoofdgerecht'] #subset of dishes that are a main meal
ing_recipes_hoofd.insert(0, column="nevonaam", value=ing_recipes["nevonaam"]) #return ingredient labels

drv = drv_full.replace("-",np.nan)
# drv = drv.loc[["Eiwit (g)","Calcium (mg)","IJzer (mg)", "Zink (mg)", "RAE (Vit A) (µg)",
#             "Vit B1  (mg)", "Vit B2 (mg)", "Folaat equiv (µg)", "Vit B12 (µg)"],:]
drv = drv.loc[["kcal (kcal)", "Calcium (mg)","IJzer (mg)", "Zink (mg)", "RAE (Vit A) (µg)",
              "Vit B1  (mg)", "Vit B2 (mg)", "Folaat equiv (µg)", "Vit B12 (µg)", "Vit C (mg)"],:]


excep_codes = nevo_exceptions[nevo_exceptions["Account_pack_size"]==0]

imported_data = {"ing_recipes_hoofd": ing_recipes_hoofd,
                 "ing_LCA": ing_LCA, "ing_packs": ing_packs, "fcd": fcd, 
                 "drv":drv, "excep_codes": excep_codes}


# ----------------------------------------------------------------------------
# Model settings and run
# ----------------------------------------------------------------------------
manual_run = False

if manual_run:
    n_days = 5 # for how many days do you want to make a planning?
    n_persons = 4
    dev = 0.0 #allow for x% deviation of the DRVs
    optimize_over="Waste_grams" #Carbon_waste, Total_carbon, Total_cost, Waste_grams, Total_landuse
    drv_settings="modelgezin_gemiddeld_gap"
    tvar1 = 9999
    
    settings = {"n_days":n_days, "n_persons": n_persons, "dev": dev, 
                "optimize_over": optimize_over, "tvar1": tvar1}

    #RUN MODEL
    var_result_dict, obj_result_dict, times = menuplanning(settings, imported_data)
    
    #WRITE RESULTS TO EXCEL
    sol_toexcel(settings, imported_data, obj_result_dict, var_result_dict, times)

else: #series run as specified in run_settings
    #onderscheid maken tussen experiment en 'gewone' run
    listlists= []
    raw_output = {"run_id":[], "settings":[],"obj_result_dict":[], "times": []}
    for run, row in run_settings.iterrows():
        settings = {"n_days":row["n_days"], "n_persons": row["n_persons"], 
                    "dev": row["dev"], "optimize_over": row["optimize_over"],
                    "DRVs":row["DRVs"], "tvar1":row["tvar1"]}
        
        ##delete this part eventually
        if False: #this part is "true" if custom preprocessing is used #TODO
            ing_recipes_ps = preprocessing_ps(ing_recipes, fcd, drv_full, settings["DRVs"], settings["n_persons"])
            ing_recipes_hoofd = ing_recipes_ps.loc[:, ing_recipes_ps.loc['mealmoment'] == 'hoofdgerecht'] #subset of dishes that are a main meal
            ing_recipes_hoofd.insert(0, column="nevonaam", value=ing_recipes["nevonaam"]) #return ingredient labels
            imported_data = {"ing_recipes_hoofd": ing_recipes_hoofd,
                 "ing_LCA": ing_LCA, "ing_packs": ing_packs, "fcd": fcd, 
                 "drv":drv, "excep_codes": excep_codes}
         ##delete this part
            
        with open('run_id.txt') as count_file:
            run_id = int(count_file.read())

        try:
            #RUN MODEL
            var_result_dict, obj_result_dict, times = menuplanning(settings, imported_data)
            
            #WRITE RESULTS TO EXCEL
            sol_toexcel(settings, imported_data, obj_result_dict, var_result_dict, times)
            
            #ANALYSES #misschien obj_result_dict maken
            raw_output["run_id"] += [run_id]
            raw_output["settings"] += [settings]
            raw_output["obj_result_dict"] += [obj_result_dict]
            raw_output["times"] += [times]
            
            listlists += [[str(run_id), row["tvar1"], obj_result_dict["Total_carbon"], obj_result_dict["Waste_grams"], times["total_time"]]]
        except: #AttributeError: !!Oppassen dat er niet een andere error is!!
            listlists += [[str(run_id),row["tvar1"],"infeasible","infeasible","infeasible"]] #hoe hier mee om gaan in stepwise reduction?
    all_obj_df = all_obj_table(raw_output) #TODO
    #household_size_df = household_size(raw_output)
    stepwise_reduction_df_waste = stepwise_reduction_waste(listlists) #also makes plots
    #stepwise_reduction_df_carbon = stepwise_reduction_carbon(listlists)

# =============================================================================
# Result analyses
# =============================================================================
# perishables = ing_packs.loc[ing_packs["Shelf_stable"]==0]
# perish_set = [i for i in perishables["nevocode"].unique()]
# perish_stock = stock_planning[stock_planning.index.isin(perish_set)]