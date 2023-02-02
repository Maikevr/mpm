hoi
menuplanningmodel_v1 is een nieuw model hoe ik hem had gemaakt in Juli


Some different versions notes and logs:

13-01-2023 13:00
First try with full dataset: 284 seconds

Total carbon footprint of recipes for 5 days:: 1.55313 g CO2 eq
On day 1 recipe: Barbecuesaus.txt
On day 2 recipe: ijsthee.txt
On day 3 recipe: Gekruide koffie.txt
On day 4 recipe: Appelmoes maken.txt
On day 5 recipe: Spiced thee.txt

13-01-2023 18:00
Made a subset of recipes (only hoofdgerechten). Try to optimize for the number of waste in grams,
computation time increased a lot. I stopped after 1000 seconds.

16-01-2023 17:00
Full dataset optimizing for waste grams. Took 26248 seconds (7.3 hr)!!! Way too long.

Total carbon footprint of recipes for 5 days:: 48.4939 kg CO2 eq
On day 1 recipe: Noedels met zalm en roerbakgroente.txt
On day 2 recipe: Penne met groente, paddenstoelen en noten.txt
On day 3 recipe: Mie met runderreepjes en groente.txt
On day 4 recipe: Groente met roerbakreepjes uit de wok.txt
On day 5 recipe: Geroerbakte bief met peultjes.txt

Carbon_waste
3.355846512864
Total_carbon
48.493882216386524
Total_cost
84.48187999999999
Waste_in_grams
455.0


18-01-2023 12:00
Bezig met shelf_stable implementeren. Let erop dat houdbare producten wel worden
gekocht (buy[i,p]), maar dat alleen de kosten en waste etc worden berekend voor wat 
je daadwerkelijk gebruikt.

#dit wordt straks dus wss "Beter" als ik het ook toevoeg aan de objectives:
Carbon_waste
Total_carbon
Total_cost
Waste_in_grams
14.320605683565303
44.13555190633522
41.33276
5520.0


18-01-2023 15:00
Let op!!! Overig wordt nu dus niet meegenomen


18-01-2023 17:30
Ik heb erin gemaakt dat ie rekening houdt met verpakkingen voor de total carbon, dus onderscheid
tussen perishable en non perishable. Ik denk dat dit de rekening veeeel te lang
maakt voor die paar producten waarin er binnen de verpakkingen onderscheid zit
tussen houdbaar/niet houdbaar. Aan de andere kant zou die wel een belangrijk onderscheid
kunnen worden voor mijn onderzoek.


24-01-2023 12:00
Teruggegaan naar main branch, hier gewoon perishability op itemniveau toegevoegd.


25-01-2023 12:00
DRVs toegevoegd.

comp times with full sets:

cost:
---Initialisation time 11.809893369674683 seconds ---
---Total computation time 219.29781889915466 seconds ---

tot carbon:
---Initialisation time 12.223147869110107 seconds ---
---Total computation time 209.3211534023285 seconds ---

waste carbon:
---Initialisation time 57.00292730331421 seconds ---
---Total computation time 275.98027992248535 seconds ---

waste grams:
---Initialisation time 64.02819657325745 seconds ---
---Total computation time 260.0001382827759 seconds ---



26-01-2023 12:00
Fixed buy bug. Of shelf-stable items, many packages were bought because it was
not penalized. Now I set a maximum to the ones used. Also, only the cheapest packages
are bought for shelf-stable items.

Fixed exceptions bug. For instance for couscous, a lot had to be bought. Because
for the LCA and NIA cooked couscous is accounted, while less raw couscous has to be
bought. I added the conversion factor to the items for which a lot has to be bought.


02-02-2023 10:30
Fixed some recipes. First try with new DRVs without slacks. DRVs for model family.
Model is infeasible.
















