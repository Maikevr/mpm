# -*- coding: utf-8 -*-
"""
Created on Tue Jul  4 16:56:13 2023

@author: rooij091
"""
import pandas as pd

def recipetype(recipe_id, ing_recipes_ps, fcd):
    #Select the recipe to check. maybe implement this to save time
    rec_i = ing_recipes_ps.loc[:,recipe_id]
    
    #for each productgroup, sum the number of grams of this group in the recipe
    vis_i = ing_recipes_ps.loc[ing_recipes_ps['nevoproductgroep'] == "Vis",recipe_id]
    visgr=0
    for g in vis_i:
        print("g: "+str(g))
        if g>0:
            visgr+=g
            
    vlees_i = ing_recipes_ps.loc[(ing_recipes_ps['nevoproductgroep'] == "Vlees en gevogelte")
                                 | (ing_recipes_ps['nevoproductgroep'] == "Vleeswaren"),recipe_id]
    vleesgr=0
    for g in vlees_i:
        if g>0:
            vleesgr+=g

    #Label the recipe. Double labels are not yet possible
    if visgr > 0:
        recipetype = 1 #"vis"
    elif vleesgr > 0:
        recipetype = 2 #"vlees"
    else:
        recipetype = 3 #"vega"
    
    ing_recipes_ps = ing_recipes_ps.drop("nevoproductgroep", axis=1)
    return recipetype
    

def recipetypelist(ing_recipes_ps, fcd):
    ing_recipes_ps.insert(len(ing_recipes_ps.columns), column="nevoproductgroep", value=fcd["nevoproductgroep"]) #return ingredient labels
    typelst = []
    for recipe_id in ing_recipes_ps.columns[0:-1]:
        a = recipetype(recipe_id, ing_recipes_ps, fcd)
        typelst += [a]
    recipetypelist = pd.DataFrame({"recipe_id":ing_recipes_ps.columns[0:-1], "type":typelst})
    recipetypelist = recipetypelist.set_index('recipe_id')
    ing_recipes_ps = ing_recipes_ps.drop("nevoproductgroep", axis=1, inplace=True)
    return recipetypelist

    
if __name__ == "__main__":
    inpath = r"Model_input\22-03-2023\\"
    fcd = pd.read_excel(inpath+'FCD - Model input.xlsx', sheet_name='Sheet1', index_col=0)
    ir = pd.read_pickle(inpath+'ing_recipes_ps_netto.pkl') #Already made preprocessing portion step. Used instead of ing_recipes.
    ing_recipes = ir.loc[:, ir.loc['mealmoment'] == 'hoofdgerecht'].copy(deep=True) #subset of dishes that are a main meal

    test = recipetype(7, ing_recipes, fcd)
    
    test = recipetypelist(ing_recipes, fcd)
    test.to_pickle(inpath+'recipetype.pkl')
    