# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 16:20:26 2023

@author: rooij091
"""
import pandas as pd
import matplotlib.pyplot as plt

def stepwise_reduction_waste(ll):
    stepwise_waste_df = pd.DataFrame(ll, columns=["run_id","Waste_cons","Tot_carbon","Tot_waste","Comp_time"])
    i=stepwise_waste_df[stepwise_waste_df.Tot_carbon=="infeasible"] #make figures without infeasible
    stepwise_waste = stepwise_waste_df.drop(i.index)
    
    stepwise_waste.plot(kind = 'scatter', x='Waste_cons', y='Tot_carbon')
    plt.xlabel("Waste upper limit (g)")
    plt.ylabel("Total carbon (g CO2)")
    plt.title("Total carbon when stepwise reduction of waste")
    
    stepwise_waste.plot(kind = 'scatter', x='Waste_cons', y='Comp_time')
    plt.xlabel("Waste upper limit (g)")
    plt.ylabel("Computation time (s)")
    plt.title("Computation time when stepwise reduction of waste")
    
    stepwise_waste.plot(kind = 'scatter', x='Tot_waste', y='Tot_carbon')
    plt.xlabel("Waste (g)")
    plt.ylabel("Total carbon (g CO2)")
    #plt.title("Trade-off carbon and waste")
    plt.savefig("Trade-off_GHGE_waste.pdf")
    
    stepwise_waste.plot(kind = 'scatter', x='Tot_waste', y='Comp_time')
    plt.xlabel("Waste (g)")
    plt.ylabel("Computation time (s)")
    plt.title("Trade_off carbon and waste - comp time")
    plt.show()
    
    stepwise_waste_df.to_excel("Model results outputs/"+stepwise_waste["run_id"][0]+"_Stepwise_waste.xlsx")
    return stepwise_waste

def stepwise_reduction_carbon(ll):
    stepwise_carbon_df = pd.DataFrame(ll, columns=["run_id","Carbon_cons","Tot_carbon","Tot_waste","Comp_time"])
    i=stepwise_carbon_df[stepwise_carbon_df.Tot_carbon=="infeasible"] #make figures without infeasible
    stepwise_carbon = stepwise_carbon_df.drop(i.index)
    
    stepwise_carbon.plot(kind = 'scatter', x='Carbon_cons', y='Tot_waste')
    plt.xlabel("Carbon upper limit (g CO2)")
    plt.ylabel("Total waste (g)")
    plt.title("Total carbon when stepwise reduction of waste")
    
    stepwise_carbon.plot(kind = 'scatter', x='Carbon_cons', y='Comp_time')
    plt.xlabel("Waste upper limit (g)")
    plt.ylabel("Computation time (s)")
    plt.title("Computation time when stepwise reduction of carbon")
    
    stepwise_carbon.plot(kind = 'scatter', x='Tot_carbon', y='Tot_waste')
    plt.xlabel("Total carbon (g CO2)")
    plt.ylabel("Total waste (g)")
    plt.title("Trade-off carbon and waste")
    
    stepwise_carbon.plot(kind = 'scatter', x='Tot_carbon', y='Comp_time')
    plt.xlabel("Total carbon (g CO2)")
    plt.ylabel("Computation time (s)")
    plt.title("Trade_off waste and carbon - comp time")
    plt.show()
    
    stepwise_carbon_df.to_excel("Model results outputs/"+stepwise_carbon["run_id"][0]+"_Stepwise_carbon.xlsx")
    return stepwise_carbon