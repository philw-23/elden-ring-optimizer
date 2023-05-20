import pandas as pd
import tkinter as tk
import tkinter.messagebox
import os
from tkinter import ttk
from pulp import *

class ArmorOptimizer(tk.Tk):
    def __init__(self, armor_frame, stat_cols, num_sols):
        super().__init__()

        # Define class variables
        self.armor_frame = armor_frame # Data to use
        self.stat_cols = stat_cols # Stat columns
        self.num_sols = num_sols # Number of solutions
        self.armor_data_dict = self.armor_frame.to_dict('index') # For indexing armor variables
        self.armor_types = self.armor_frame['ArmorType'].unique().tolist() # Unique armor types
        self.armor_dict = self.generate_armor_data() # Generate list of armor types for each class
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
            armor_var = tk.StringVar(value="") # Var for storing selected choice
            ttk.Label(frame, text=item[1]).grid(row=i+1, column=0)
            armor_items = self.armor_frame.loc[self.armor_frame['ArmorType'] == item[0]]['Name'].tolist() # Get armor items
            dropdown = ttk.Combobox(frame, values=armor_items)
            dropdown.grid(row=i+1, column=1)
            dropdown.config(width=20)  # Adjust the width here
            armor_var_dict[item[0]] = dropdown # Add combobox for armor type to dictionary
            
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
            stat_var = tk.StringVar(value="") # Var for storing selected choice
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
            input_var = tk.DoubleVar(value=0.0) # Input value for either target or constraint
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
               
    # Function for generating new window to show results - takes in dataframe of results
    def display_results(self, result_set):
        # Display results (following tutorial from here: https://www.youtube.com/watch?v=PgLjwl6Br0k)
        results_win = tk.Toplevel() # New window
        results_win.geometry('1250x400')
        style = ttk.Style() # For generating custom style
        style.configure("res_style.Treeview", highlightthickness=0, bd=0, font=('Calibri', 10)) # Modify the font of the body
        style.configure("res_style.Treeview.Heading", highlightthickness=0, bd=0, font=('Calibri', 10)) # Modify header
        res_tree = ttk.Treeview(results_win, style='res_style.Treeview')
        res_tree.place(relheight=1, relwidth=1) # set the height and width of the widget to 100% of its container.
        scroll_y = tk.Scrollbar(results_win, orient="vertical", command=res_tree.yview) # command means update the yaxis view of the widget
        scroll_x = tk.Scrollbar(results_win, orient="horizontal", command=res_tree.xview) # command means update the xaxis view of the widget
        res_tree.configure(xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set) # assign the scrollbars to the Treeview Widget
        scroll_x.pack(side="bottom", fill="x") # make the scrollbar fill the x axis of the Treeview widget
        scroll_y.pack(side="right", fill="y") # make the scrollbar fill the y axis of the Treeview widget
        res_tree['column'] = list(result_set.columns) # Columns to insert
        res_tree["show"] = "headings"
        for column in res_tree["columns"]:
            if column in self.stat_cols:
                width = 0 # Only one pixel needed for stat cols
            elif any(result_set[column].str.contains('Altered')): # More pixels for wider column cases
                 width = 155
            else:
                width = 90
            res_tree.column(column, anchor='w', width=width, stretch=True)
            res_tree.heading(column, anchor='w', text=column) # let the column heading = column name

        rows = result_set.to_numpy().tolist() # turns the dataframe into a list of lists
        for row in rows:
            res_tree.insert("", "end", values=row) # inserts each list into the treeview. For parameters see https://docs.python.org/3/library/tkinter.ttk.html#tkinter.ttk.Treeview.insert
            
        return
    
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
        # Get necessary values
        constraint_stat = self.stat_var_dict['Constraint Stat']['var'].get()
        stat_to_max = self.stat_var_dict['Stat to Maximize']['var'].get()
        constraint_value = float(self.input_var_dict['Constraint Value'].get())
        target_stat = float(self.input_var_dict['Target Value'].get())
        if constraint_value == 0.0: # Cannot solve with no constraint
            tkinter.messagebox.showinfo('Error', 'Constraint Value input cannot be 0')
            return
    
        # Define PuLP model
        armor_prob = LpProblem("ArmorOptimizer", LpMaximize) # Model
        solver = getSolver('PULP_CBC_CMD')
        armor_items = LpVariable.dicts('ArmorTypes', [(i, armor_type) for armor_type in self.armor_types
                                                     for i in self.armor_dict[armor_type]], cat='Binary') # Decision variables
        armor_prob += lpSum([self.armor_data_dict[i][stat_to_max] * armor_items[i, armor] 
                             for armor in self.armor_types for i in self.armor_dict[armor]]) # Cost function
        armor_prob += lpSum([self.armor_data_dict[i][constraint_stat] * armor_items[i, armor] 
                             for armor in self.armor_types for i in self.armor_dict[armor]]) <= constraint_value, "Stat constraint"
        for armor in self.armor_types: # Constraint to only select 1 from each class
            armor_prob += lpSum([armor_items[(i, armor)] 
                                 for i in self.armor_dict[armor]]) == 1, 'One item from %s category' % armor
        
        # Target value constraint
        if target_stat != 0.0:
            armor_prob += lpSum([self.armor_data_dict[i][stat_to_max] * armor_items[i, armor] 
                             for armor in self.armor_types for i in self.armor_dict[armor]]) >= target_stat, 'Target constraint'
        
        # Generate constraints for any selected armor pieces
        for armor_type, var in self.armor_var_dict.items():
            var_val = var.get() # Get current variable value
            if var_val != '': # Check for non-default values
                armor_idx = self.name_to_idx[var_val] # Get index for adding constraint
                armor_items[(armor_idx, armor_type)].setInitialValue(1) # Restrict to use this armor piece
                armor_items[(armor_idx, armor_type)].fixValue()
        
        # Iterate for multiple solutions
        all_solution_sets = []
        for k in range(0, self.num_sols): # Iterate a set number of times
            armor_prob.solve(solver) # Solve solution
            if armor_prob.status == 1: # Solution found
                sol_dict = {} # For storing solution info
                sol_idxs = [] # For storing selected values - add constraint later
                for armor in self.armor_types:
                    for i in self.armor_dict[armor]:
                        if armor_items[(i,armor)].varValue == 1:
                            sol_dict[armor] = self.armor_data_dict[i]['Name']
                            for stat in stat_cols:
                                try: # Key exists (after first armor piece)
                                    sol_dict[stat] += self.armor_data_dict[i][stat]
                                except: # Key doesn't exist (first armor piece)
                                    sol_dict[stat] = self.armor_data_dict[i][stat]
                            sol_idxs.append((i, armor)) # Add indexes for building constraint against repeat solution
                armor_prob += lpSum([armor_items[sol] for sol in sol_idxs]) <= 3, 'Solution %d constraint' % k
                all_solution_sets.append(sol_dict) # Append solution info
            else: # No solution found - end loop
                break
        
        # Get results
        if len(all_solution_sets) > 0: # Solutions found
            result_frame = pd.DataFrame(all_solution_sets)            
            result_frame = result_frame[self.armor_types + self.stat_cols] # Reorganize
            result_frame.sort_values(by=[stat_to_max, constraint_stat], 
                                     ascending=[False, True],
                                     inplace=True) # Sort values
            result_frame = result_frame.round(1)
            self.display_results(result_frame)
            
            
        else: # No solutions
            tkinter.messagebox.showinfo('', 'No solutions meeting constraints found')
            return
        
# Load in data to pass to app
os.chdir(sys._MEIPASS) # Uncomment before packaging with pyinstaller
armor_data = pd.read_csv('./EldenRing_Armor_Data.txt', sep='|')
start_col_idx = armor_data.columns.get_loc('Name') + 1
end_col_idx = armor_data.columns.get_loc('Wgt') + 1
stat_cols = armor_data.columns[start_col_idx:end_col_idx].tolist()

# Generate app            
app = ArmorOptimizer(armor_data, stat_cols, 10)
app.mainloop()