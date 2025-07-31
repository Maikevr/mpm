# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import pandas as pd

inpath = r"Model_input\22-03-2023\\"
fig = plt.figure()
ax = fig.add_axes([0,0,1,1])
menucost = pd.read_excel(inpath+"/610_vvv_test_includinglanduse.xlsx", sheet_name='python_data',index_col=0)
threshold = min(menucost["GHGE (g CO2eq)"])

ax = menucost.plot(kind="bar", legend=False)
ax.set_ylabel("GHGE (g CO2eq)")
plt.xticks(rotation=45, ha='right')
plt.axhline(y=threshold,linewidth=1, linestyle='--')
plt.savefig("vvv_ghge.pdf", format="pdf", bbox_inches="tight")
plt.show()