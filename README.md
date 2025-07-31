# Meal Planning Model (MPM)

A mixed-integer meal planning model that generates meal plans by combining recipes to reduce household food waste. 
The model considers:
- retail package sizes
- nutrtitional guidelines
- package costs
- environmental impact (carbon footprint and land use)

This model is described in detail in the following publication: 
van Rooijen, M. A., Gerdessen, J. C., Claassen, G. D. H., & de Leeuw, S. L. J. M. (2024). Optimizing household food waste: The impact of meal planning, package sizes, and performance indicators. Resources, Conservation and Recycling, 205, 107559. 

## Requirements
- Python 3.x
- Gurobi Optimizer (license required)

## Main Files

- `mpm_build.py`: Formulates the mixed-integer meal planning model  
- `mpm_callfile.py`: Loads input data, configures settings, and runs the model  
- `mpm_excelwriter.py`: Outputs the optimal meal plan and results to an Excel file
- `Model_input/` – Input data files (e.g., recipes, ingredients, nutritional data)  
- `Model results outputs/` – Generated meal plans and model results  
- `Analysis_functions/` – Functions for analyzing model outputs  
- `run_id.txt` – Run identifier for version tracking    

## Usage

Configure settings in 'mpm_callfile.py' and run "mpm_callfile.py"