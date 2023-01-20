# -*- coding: utf-8 -*-
"""
Created on Thu Jan 19 09:53:11 2023

@author: rooij091
"""


# =============================================================================
# Check carbon answer
# =============================================================================
#later kan ik hier misschien een soort automatische check van maken. Dat dit automatisch wordt vergeleken met de model uitkomst
perishables = ing_packs.loc[ing_packs["Shelf_stable"]==0]
perish_set = [i for i in perishables["nevocode"].unique()]

n_days = 5
days = [str(x) for x in range(0, n_days+1)]

carbp = 0
carbs = 0
for i,j in stock_planning.iterrows():
    if i < 9998:
        if i in perish_set:
            carbp += stock_planning.loc[i,"0"]*ing_LCA.loc[i,"GHGE_kg_CO2eq_per_kg"]
        else:
            carbs += (stock_planning.loc[i,"0"]-stock_planning.loc[i,days[-1]])*ing_LCA.loc[i,"GHGE_kg_CO2eq_per_kg"]
print(carbp, carbs)
print(carbp+carbs)



# =============================================================================
# #test waarom deze berekening niet werkt
# #solution check total carbon perishable. als dit hetzelfde is als uitkomst werkt het. Hoe kan
# #ik dit sneller maken????
# =============================================================================
testperish = 0
for i,p in zip(ing_packs["nevocode"],ing_packs["Package (g)"]):
    index = indexpack(i,p)
    if ing_packs.loc[indexpack(i,p),"Shelf_stable"]==0:
        #print(index)
        #print(purchase_planning.loc[index,"buy"], ing_packs.loc[index,"Package (g)"], ing_LCA['GHGE_kg_CO2eq_per_kg'][i])
        testperish += purchase_planning.loc[index,"buy"]*ing_packs.loc[index,"Package (g)"]*ing_LCA['GHGE_kg_CO2eq_per_kg'][i] 
print(testperish)

  

# =============================================================================
# #Dit stuk heeft nog niet gewerkt, duurt veel te lang    
# =============================================================================
teststable = 0
stableconsumed = planning_ingredients.sum(axis=1)
for i in ingredients:
    hap = stableconsumed.loc[i]
    for i,p in zip(ing_packs["nevocode"],ing_packs["Package (g)"]):
        index = indexpack(i,p)
        if ing_packs.loc[indexpack(i,p),"Shelf_stable"]==0:
            hap -= purchase_planning.loc[index,"buy"]*ing_packs.loc[index,"Package (g)"]
            #print(hap)
            #print(index)
            #print(purchase_planning.loc[index,"buy"], ing_packs.loc[index,"Package (g)"], ing_LCA['GHGE_kg_CO2eq_per_kg'][i])
    if hap >0:
        print(hap)
        teststable += hap*ing_LCA['GHGE_kg_CO2eq_per_kg'][i]
print(teststable)
        

# =============================================================================
# #dus er is geen een artikel waarvoor ik verschillende houdbaarheids datums heb nu
# =============================================================================
for i in ingredients: 
    nevoset = pack_info_standardised.loc[pack_info_standardised["nevocode"]==i]
    #print(nevoset)
    if not (nevoset['Shelf_stable'] == nevoset['Shelf_stable']).all():
        print(nevocode)
        
        
# =============================================================================
# Set of perishable items i
# =============================================================================
perishables = ing_packs.loc[ing_packs["Shelf_stable"]==0]
perish_set = [i for i in perishables["nevocode"].unique()]

stables = ing_packs.loc[ing_packs["Shelf_stable"]==1]
stable_set = [i for i in stables["nevocode"].unique()]

        
