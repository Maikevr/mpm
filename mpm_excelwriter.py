# -*- coding: utf-8 -*-
"""
Created on Mon Feb  6 15:15:07 2023

@author: rooij091

Write model outputs to excel.
"""
from datetime import datetime
from datetime import date
import pandas as pd

def sol_toexcel(settings, imported_data, obj_result_dict, var_result_dict, times):
    # =============================================================================
    #     Unpack data
    # =============================================================================
    n_days = settings["n_days"]
    n_persons = settings["n_persons"]
    dev = settings["dev"]
    optimize_over = settings["optimize_over"]
    
    ing_recipes = imported_data["ing_recipes_hoofd"]
    drv = imported_data["drv"]
    
    
    # =============================================================================
    #     Initialisation
    # =============================================================================
    with open('run_id.txt') as count_file:
        run_id = int(count_file.read())
    filename = str(run_id)+'_'+optimize_over+'_'+str(date.today())+'.xlsx'
    path = "Model results outputs/"+filename
    writer = pd.ExcelWriter(path,engine='xlsxwriter') #makes it possible to add pandas 
    workbook = writer.book
    
    bold_format = workbook.add_format({'bold':True, 'align':'left'})
    highlight_format = workbook.add_format({'bg_color':'#D8E4BC'})
    percent_format = workbook.add_format({'num_format':'0.0%'})
    
    # =============================================================================
    #     overview page
    # =============================================================================
    overview = workbook.add_worksheet("Overview") #manual sheet, without andas
    overview.set_column(0,0,30)
    
    #unique run number
    overview.write('A1', "Unique model run ID:")
    overview.write('B1', run_id)
    with open('run_id.txt', 'w') as count_file:
        count_file.write(str(run_id+1))
    
    #date and time of model run/writing
    overview.write('A2', "Date and time of model run:")
    overview.write("B2", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    #objective
    overview.write('A3', "Objective:")
    overview.write("B3", optimize_over, bold_format)
    
    #number days and persons
    overview.write("A5", "Number of days run for:")
    overview.write("B5", n_days)
    overview.write("A6", "Number of persons run for:")
    overview.write("B6", n_persons)
    overview.write("A7", "Deviation allowed from the DRVs")
    overview.write("B7", dev, percent_format)
    
    #objectives, highlight current objective
    overview.write("A9", "Total", bold_format)
    row = 9
    col = 0
    for key in obj_result_dict:
        overview.write(row, col, key)
        if key == optimize_over:
            overview.write(row, col+1, round(obj_result_dict[key],2), highlight_format)
        else:
            overview.write(row, col+1, round(obj_result_dict[key],2))
        row+=1
    
    overview.set_column(3,3,30)
    overview.write("D9", "Per day per person", bold_format)
    row = 9
    col = 3
    for key in obj_result_dict:
        overview.write(row, col, key)
        if key == optimize_over:
            overview.write(row, col+1, round(obj_result_dict[key]/(n_days*n_persons), 2), highlight_format)
        else:
            overview.write(row, col+1, round(obj_result_dict[key]/(n_days*n_persons),2))
        row+=1
    
    #vvv
    overview.write("A16", "Meals included", bold_format)
    vvvsol = var_result_dict["vvvsol"]
    overview.write("A17", "# of times fish:")
    overview.write("B17", vvvsol[1]["# fish:"])
    overview.write("A18", "# of times meat:")
    overview.write("B18", vvvsol[1]["# meat:"])
    overview.write("A19", "# of times vegetarian:")
    overview.write("B19", vvvsol[1]["# vegetarian:"])
    
    #init time and total time
    overview.write('A21', "Model initialization time:")
    overview.write("B21", round(times["init_time"]))
    overview.write('A22', "Model total time:")
    overview.write("B22", round(times["total_time"]))


    overview.write('A24', "Notes below are added manually:", bold_format)

    # =============================================================================
    #     var sheets
    # =============================================================================
    inpath = r"Model_input\22-03-2023\\"
    urls = pd.read_csv(inpath+"recipe_urls 14-10-2022.csv")
    urls = urls.set_index("titles")
    #Planning recipes
    planning_sheet = workbook.add_worksheet("Planning_recipes") 
    planning_sheet.write(0,0, 'Recipes planned on:', bold_format)
    planning_recipes = var_result_dict["Planning_recipes"]
    index_not = planning_recipes[(round(planning_recipes)!=1).all(1)].index
    planning_recipes = planning_recipes.drop(index_not)
    row = 1
    col = 0
    for day in planning_recipes.iloc[:,1:]:
        planning_sheet.write(row, col, "Day "+str(day))
        recipe_idx = planning_recipes[round(planning_recipes[day])==1].index[0] 
        recipe = ing_recipes.loc['recipe_id',recipe_idx].strip(".txt")
        planning_sheet.write(row, col+1, recipe)
        planning_sheet.set_column(1,1,50)
        try:
            url = urls.loc[recipe,'urls']
            planning_sheet.write(row, col+2, url)
        except:
            planning_sheet.write(row, col+2, "URL not found")
        row+=1
    
    #NIA 
    NIA = var_result_dict["NIA"]
    NIA.columns = ["Day "+str(d) for d in range(n_days+1)]
    NIA.to_excel(writer, sheet_name="NIA",startrow=0)
    NIAsheet = writer.sheets["NIA"]
    NIAsheet.set_column(0,0,20)
    #highlight rows in DRV
    j = 2 #starts at 1 because first row is column headers, and j is not zero indexed
    for i in NIA.index.values:
        if i in drv.index.values:
            frange = 'B'+str(j)+':I'+str(j)
            NIAsheet.conditional_format(frange, {'type': 'cell',
                                       'criteria' : '>', 
                                       'value' : -99999999999,
                                       'format' : highlight_format})
        j+=1
    
    #NIA per person
    NIApp = round(var_result_dict["NIA"]/n_persons,2)
    NIApp.columns = ["Day "+str(d) for d in range(n_days+1)]
    NIApp.to_excel(writer, sheet_name="NIA_pp",startrow=0)
    NIAppsheet = writer.sheets["NIA_pp"]
    NIAppsheet.set_column(0,0,20)
    #highlight rows in DRV
    j = 2 #starts at 1 because first row is column headers, and j is not zero indexed
    for i in NIApp.index.values:
        if i in drv.index.values:
            frange = 'B'+str(j)+':I'+str(j)
            NIAppsheet.conditional_format(frange, {'type': 'cell',
                                       'criteria' : '>', 
                                       'value' : -99999999999,
                                       'format' : highlight_format})
        j+=1
    
    #Planning ingredients
    planning_ingredients = round(var_result_dict["Planning_ingredients"])
    if ing_recipes.index[2:].equals(planning_ingredients.index) and len(planning_ingredients.columns) < n_days+2:
        planning_ingredients.insert(0, "new", ing_recipes.iloc[2:,0])
        planning_ingredients.columns = ['nevonaam']+["Day "+str(d) for d in range(n_days+1)]
    planning_ingredients.to_excel(writer, sheet_name="Planning_ingredients",startrow=0,startcol=0)   
    pi_sheet = writer.sheets["Planning_ingredients"]
    pi_sheet.set_column(1,1,30)   
    pi_sheet.autofilter('A1:H1')
    
    #Stock planning
    stock_planning = round(var_result_dict["Stock_planning"])
    if ing_recipes.index[2:].equals(stock_planning.index) and len(stock_planning.columns) < n_days+2: #insert nevonames and don't insert twice
        stock_planning.insert(0, "nevonaam", ing_recipes.iloc[2:,0])
        stock_planning.columns = ['nevonaam']+["Day "+str(d) for d in range(n_days+1)]
    stock_planning = stock_planning.sort_values(["Day "+str(n_days)], ascending=[False]) #presort
    stock_planning.to_excel(writer, sheet_name="Stock_planning",startrow=0,startcol=0)
    sp_sheet = writer.sheets["Stock_planning"]
    sp_sheet.set_column(1,1,30)   
    sp_sheet.autofilter('A1:H1')
    
    #Purchase planning
    purchase_planning = var_result_dict["Purchase_planning"]
    purchase_planning = purchase_planning.sort_values(['buy'], ascending=[False])
    purchase_planning.to_excel(writer, sheet_name="Purchase_planning",startrow=0,startcol=0)
    pp_sheet = writer.sheets["Purchase_planning"]
    pp_sheet.set_column(2,2,30)
    pp_sheet.set_column(3,3,20)
    pp_sheet.set_column(5,5,30)
    pp_sheet.set_column(6,11,10)
    pp_sheet.set_row(0, None, bold_format) 
    pp_sheet.autofilter('A1:K1')
    
    #Purchase costs
    purchase_costs = var_result_dict["Purchase_costs"]
    if ing_recipes.index[2:].equals(purchase_costs.index) and len(purchase_costs.columns) < 2: #insert nevonames and don't insert twice
        purchase_costs.insert(0, "nevonaam", ing_recipes.iloc[2:,0])
        purchase_costs.columns = ['nevonaam']+['Cost (€)']
    purchase_costs = purchase_costs.sort_values(['Cost (€)'], ascending=[False]) #presort
    purchase_costs.to_excel(writer, sheet_name="Purchase_costs",startrow=0,startcol=0)
    pc_sheet = writer.sheets["Purchase_costs"]
    pc_sheet.set_column(1,1,30) 
    pc_sheet.set_column(2,2,15)
    pc_sheet.autofilter('A1:C1')
    
    workbook.close()
    print ('done')
    
if __name__ == '__main__': 
    sol_toexcel(settings, imported_data, obj_result_dict, var_result_dict, times)