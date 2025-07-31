# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 13:23:28 2023

@author: rooij091
"""
import pandas as pd

def all_obj_table(raw_output):
    #extract desired data from raw model output
    run_id = raw_output["run_id"]
    obj = [raw_output["settings"][i]["optimize_over"] for i in range(len(run_id))]
    n_days = [raw_output["settings"][i]["n_days"] for i in range(len(run_id))]
    n_pers = [raw_output["settings"][i]["n_persons"] for i in range(len(run_id))]
    dev = [raw_output["settings"][i]["dev"] for i in range(len(run_id))]
    
    total_ghge = [raw_output["obj_result_dict"][i]["Total_ghge"] for i in range(len(run_id))]
    total_landuse = [raw_output["obj_result_dict"][i]["Total_landuse"] for i in range(len(run_id))]
    total_waste = [raw_output["obj_result_dict"][i]["Waste_grams"] for i in range(len(run_id))]
    carbon_waste = [raw_output["obj_result_dict"][i]["Carbon_waste"] for i in range(len(run_id))]
    total_cost = [raw_output["obj_result_dict"][i]["Total_cost"] for i in range(len(run_id))]
    
    comp_time = [raw_output["times"][i]["total_time"] for i in range(len(run_id))]
    
    
    #make a df of desired info
    ll = [run_id, obj, n_days, n_pers, dev, total_ghge, total_landuse, total_waste, 
          carbon_waste, total_cost, comp_time]
    ll = [list(i) for i in zip(*ll)] #transpose list
    all_obj_table_df = pd.DataFrame(ll, columns=["run_id","obj","n_days","n_pers",
                                                 "dev", "total_carbon","total_landuse",
                                                 "total_waste","carbon_waste",
                                                 "total_cost","comp_time"])
    

    all_obj_table_df.to_excel("Model results outputs/"+str(run_id[0])+"_All_obj_table.xlsx")

    return all_obj_table_df
    
