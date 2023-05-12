import pandas as pd
import tkinter as tk
from tkinter import ttk

class ArmorOptimizer(tk.Tk):
    def __init__(self, armor_frame, stat_cols):
        super().__init__()

        # Define class variables
        self.armor_frame = armor_frame
        self.stat_cols = stat_cols
        self.armor_data_dict = self.armor_frame.to_dict('index') # For indexing armor variables
        self.armor_types = self.armor_frame['ArmorType'].unique().tolist() # Unique armor types
        self.armor_data = self.generate_armor_data() # Generate list of armor types for each class
        self.name_to_idx = dict(zip(self.armor_frame['Name'], self.armor_frame.index)) # For mapping selected names to idx
        
        # Define title
        self.title("Armor Optimizer")
        
        # Generate sections
        self.sections = [] # For storing section objects - will pass to relevant sections
        for _ in range(3):
            frame = ttk.Frame(self, padding="10 10 10 10", relief="groove")
            frame.grid(sticky="ew")
            self.sections.append(frame)

        # Generate section relative to fixing armor pieces
        self.armor_mapper = { # Dictionary for mapping armor types to dropdown name
            'Helms':'Select Helm',
            'ChestArmor':'Select Chest',
            'Gauntlets':'Select Gauntlet',
            'LegArmor':'Slect Legs'
        }
        self.armor_var_dict = self.create_armor_section(self.sections[0])

        # Generate section for selecting stats
        self.stat_var_dict = self.create_stat_section(self.sections[1])

        # Generate input value section
        self.input_var_dict = self.create_input_section(self.sections[2])

        # Generate buttons
        self.create_button_section()

    '''
    Creates a dropdown for each armor type and populates the first section of GUI. Returns armor_var_dict 
    which is a dictionary of tkinter string vars used for each armor menu (reset function will set these back
    to default, "")
    '''
    def create_armor_section(self, frame):
        ttk.Label(frame, text="Fix Armor Pieces (Optional)").grid(row=0, column=0, columnspan=4)
        armor_var_dict = {} # For storing variables
        for i, item in enumerate(self.armor_mapper.items()): # Iterate through armor types
            # Note: i is index, item[0] is the key from self.armor_mapper, item[1] is the label we will use
            # i=0 Helms, i=1 ChestArmor, i=2 Gauntlets, i=3 LegArmor
            armor_var = tk.StringVar("") # Var for storing selected choice
            ttk.Label(frame, text=item[1]).grid(row=i+1, column=0)
            armor_items = self.armor_frame.loc[self.armor_frame['ArmorType'] == item[0]]['Name'].tolist() # Get armor items
            dropdown = ttk.OptionMenu(frame, armor_var, "", *armor_items)
            dropdown.grid(row=i+1, column=1)
            dropdown.config(width=20)  # Adjust the width here
            armor_var_dict[item[0]] = armor_var # Add armor var for armor type to dictionary
            
        return armor_var_dict

    '''
    Creates a dropdow for maximizing/constraint stat and populates the second section of GUI. Returns stat_var_dict 
    which is a dictionary of tkinter string vars and default values used for each option menu (reset function will 
    set these back to default)
    '''
    def create_stat_section(self, frame):
        ttk.Label(frame, text="Stat Selection").grid(row=0, column=0, columnspan=2)
        stat_labels = ["Stat to Maximize", "Constraint Stat"] # Stat labels
        dflt_stats = ['Poi', 'Wgt'] # Default stats for each column
        stat_var_dict = {} # For storing variables/defaults
        for i, label in enumerate(stat_labels):
            stat_var = tk.StringVar("") # Var for storing selected choice
            ttk.Label(frame, text=label).grid(row=i+1, column=0)
            dropdown = ttk.OptionMenu(frame, stat_var, dflt_stats[i], *self.stat_cols)
            dropdown.grid(row=i+1, column=1)
            dropdown.config(width=20)  # Adjust the width here
            stat_var_dict[stat_labels[i]] = {
                'var':stat_var, 'dflt':dflt_stats[i]
            }
            
        return stat_var_dict

    '''
    Creates a double input for maximizing/constraint stat and populates the third section of GUI. Returns input_var_dict
    which is a dictionary of tkinter double vars used for each input (reset function will set these back to 0.0)
    '''
    def create_input_section(self, frame):
        ttk.Label(frame, text="Input Values").grid(row=0, column=0, columnspan=2)
        self.input_vars = [tk.DoubleVar(value=0.0) for _ in range(2)]
        input_labels = ["Target Value", "Constraint Value"] # Target/Constraint
        input_var_dict = {} # For storing input var objects
        for i, label in enumerate(input_labels):
            input_var = tk.DoubleVar(0.0) # Input value for either target or constraint
            ttk.Label(frame, text=label).grid(row=i+1, column=0, padx=10)
            ttk.Entry(frame, textvariable=input_var).grid(row=i+1, column=1)
            input_var_dict[label] = input_var # Add to dict
            
        return input_var_dict

    # Creates button sections
    def create_button_section(self):
        frame = ttk.Frame(self, padding="10 10 10 10")
        frame.grid(sticky="ew")
        ttk.Button(frame, text="Optimize", command=self.run_optimizer).grid(row=0, column=0)
        ttk.Button(frame, text="Reset", command=self.reset_values).grid(row=0, column=1)

    # Generates armor type to index dictionary
    def generate_armor_data(self):
        armor_dict = {}
        for armor in self.armor_types: # Iterate through armor types
            armor_dict[armor] = armor_data.loc[armor_data['ArmorType'] == armor].index.tolist() # Get items for each class
            
        return armor_dict # Armor to index dictionary
        
    # Resets variables being used to defaults
    def reset_values(self):
        # Reset armor var values
        for v in self.armor_var_dict.values():
            v.set("")
            
        # Reset stat vars
        for item in self.stat_var_dict.values():
            item['var'].set(item['dflt']) # Set var back to default
        
        # Reset input vars
        for var in self.input_var_dict.values():
            var.set(0.0)
       
    # Runs optimizer
    def run_optimizer(self):
        pass

# Load in data to pass to app
armor_data = pd.read_csv('./EldenRing_Armor_Data.txt', sep='|')
start_col_idx = armor_data.columns.get_loc('Name') + 1
end_col_idx = armor_data.columns.get_loc('Wgt') + 1
stat_cols = armor_data.columns[start_col_idx:end_col_idx].tolist()

# Generate app            
app = ArmorOptimizer(armor_data, stat_cols)
app.mainloop()