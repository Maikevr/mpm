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
import time
start = time.time()
testperish = 0
for i,p in zip(ing_packs["nevocode"],ing_packs["Package (g)"]):
    index = indexpack(i,p)
    if ing_packs.loc[indexpack(i,p),"Shelf_stable"]==0:
        #print(index)
        #print(purchase_planning.loc[index,"buy"], ing_packs.loc[index,"Package (g)"], ing_LCA['GHGE_kg_CO2eq_per_kg'][i])
        testperish += purchase_planning.loc[index,"buy"]*ing_packs.loc[index,"Package (g)"]*ing_LCA['GHGE_kg_CO2eq_per_kg'][i] 
print(testperish)
print(time.time()-start)
  

# =============================================================================
# #Dit stuk heeft nog niet gewerkt, duurt veel te lang    
# =============================================================================
import time
start = time.time()
print(start)
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
print(time.time()-start)
        

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


# =============================================================================
# Try to add portion size constraints by using bigM constraints.     
# =============================================================================
"""Didn't work because it runs out of memory. Must be a faster way""""
    # 2.4 constraint to compute ingredients used for cooking per day  
    # 2.4.1 constraint to make sure that ingredients used for a day is substracted from ingredients on stock
    for d in range(len(days)):
        if d != 0:
            for i in ingredients: #kan dit mooier dan met 3 loops?
                #used = (n_persons+ps[str(d)])*gp.quicksum(ing_recipes.loc[i,r]*y[r,str(d)] for r in recipes)
                #m.addConstr(used == used*ps[str(d)])
                
                #FIXME
                for r in recipes:
                    if np.isnan(ing_recipes.loc[i,r]):
                        a = 0
                    else:
                        a = ing_recipes.loc[i,r]
                    m.addConstr(usedi[r, str(d), i] == (n_persons+ps[str(d)])*a)
                    m.addConstr(usedi[r, str(d), i] <= y[r,str(d)]*2000)
                used = gp.quicksum(usedi[r, str(d), i] for r in recipes)
                #FIXME
                
                m.addConstr(x[i,str(d)] == used, "ingredients used for cooking per day")
                if i in excep_codes.index.values: #to make sure that for e.g. cooked couscous not too much raw couscous is bought
                    conversion = excep_codes.loc[i,"Conversion_factor"]
                    m.addConstr(stock[i,str(d)] == stock[i,str(d-1)]-used/conversion, "stock equation (exceptions)")
                else:
                    m.addConstr(stock[i,str(d)] == stock[i,str(d-1)]-used, "stock equation")
                    
                
"""Also tried this: becomes quadratic though, and takes a long time to solve"""
used = (n_persons+ps[str(d)])*gp.quicksum(ing_recipes.loc[i,r]*y[r,str(d)] for r in recipes)
