# -*- coding: utf-8 -*-
"""
Created on 19-06-2023

"""


import matplotlib.pyplot as plt
import numpy as np
import pandas as pd




def all_obj_plot(filename):
    all_obj_table = pd.read_excel(filename)
    df = all_obj_table.iloc[:5,:]
    
    fig, axes = plt.subplots(nrows=1, ncols=3)
    df.plot.bar(ax=axes[0], x="obj", y="total_carbon", rot=90)
    df.plot.bar(ax=axes[1], x="obj", y="total_waste", rot=90)
    df.plot.bar(ax=axes[2], x="obj", y="total_cost", rot=90)
    
    
    plt.show()
    
def remove_recipe_plot(filename):
    all_obj_table = pd.read_excel(filename, sheet_name="remove_recipes")
    df = all_obj_table.iloc[:5,:]
    
    fig, (ax1, ax2, ax3) = plt.subplots(nrows=1, ncols=3)
    plt.bar(ax=ax1, x=0, height=df.loc[0,"Total_carbon"], rot=90)
    plt.bar(ax=ax1, x=1, height=df.loc[1,"Total_carbon"], rot=90)
    ax1.set_xlabel("Total carbon")
    
    df.plot.bar(ax=ax2, x="removed", y="Waste_grams", rot=90)
    ax2.set_xlabel("Waste grams")
    
    df.plot.bar(ax=ax3, x="removed", y="Total_cost", rot=90)
    ax3.set_xlabel("Total cost")
    

    
    plt.show()
    
if name == __main__:
    filename = "Model results outputs/357_All_obj_table.xlsx"
    all_obj_plot(filename)
    
    
#zoiets wil ik: https://stackoverflow.com/questions/65230006/how-to-create-a-figure-of-subplots-of-grouped-bar-charts-in-python