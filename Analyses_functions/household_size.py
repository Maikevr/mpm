# -*- coding: utf-8 -*-
"""
Created on Fri Mar 31 14:41:06 2023

@author: rooij091
"""
import pandas as pd
import matplotlib.pyplot as plt

def household_size(raw_output):
    #extract desired data from raw model output
    run_id = raw_output["run_id"]
    total_carbon = [raw_output["obj_result_dict"][i]["Total_carbon"] for i in range(len(run_id))]
    total_waste = [raw_output["obj_result_dict"][i]["Waste_grams"] for i in range(len(run_id))]
    total_time = [raw_output["times"][i]["total_time"] for i in range(len(run_id))]
    pers = [raw_output["settings"][i]["n_persons"] for i in range(len(run_id))]
    
    #make a df of desired info
    ll = [run_id, pers, total_carbon, total_waste, total_time]
    ll = [list(i) for i in zip(*ll)] #transpose list
    household_size_df = pd.DataFrame(ll, columns=["run_id","n_pers","Tot_carbon","Tot_waste","Comp_time"])
    
    #make graphs
    household_size_df.plot(kind = 'scatter', x='n_pers', y='Tot_waste')
    plt.xlabel("Household size (# persons)")
    plt.ylabel("Waste (g)")
    plt.title("Total waste for each household size")
    
    #make graphs
    household_size_df.plot(kind = 'scatter', x='n_pers', y='Tot_carbon')
    plt.xlabel("Household size (# persons)")
    plt.ylabel("Carbon (g)")
    plt.title("Total carbon for each household size") 
    
    household_size_df.to_excel("Model results outputs/"+str(run_id[0])+"_Household_size.xlsx")
    return household_size_df
    
