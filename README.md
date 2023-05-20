# elden-ring-optimizer
This repo contains code to produce a list of armor combinations (Helms, Gauntlets, ChestArmor, LegArmor) maximizing a specific stat while subject to a limiting constraint of another stat. The initial designed use case for this is to maximize the poise stat while being subject to a limiting weight constraint.

The DataScraper.ipynb pulls the armor information data from the Fextralife website using the BeautifulSoup package in python. A DataFrame of all the info is generated and saved out for use in the StatOptimizer.ipynb script. The StatOptimizer script generates a linear programming problem using PuLP with this data, and creates a dataframe showing a desired number of potential solutions. Note that to output multiple potential solutions using PuLP, the model is ran multiple times with a constraint added at the end of each run that prevents the same combination of armor pieces from being selected again.

### Creating Environment and Packaging
This repo includes files for creating an environent with the relevant packages using either conda or pip. For conda, the environment can be created with the following command:

`conda env create -f environment.yml`

For pip, the command is:

`pip install -r requirements.txt`

Once the environment is created, the following pyinstaller command can be used to create the ArmorOptimizerApp executable file. Running DataScraper.ipynb is also a pre-requisite to packaging in order to generate the armor data input file.

`pyinstaller --onefile --add-data="./EldenRing_Armor_Data.txt;." --collect-data pulp ArmorOptimizerApp.py`

The `--collect-data` argument is needed for pulp in order to package the filed needed for the LP solver.