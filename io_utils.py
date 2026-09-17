#For data acquisition

import numpy as np #Mathematical calculations
import json #JS file
import os #Operating system

#Collect CONTCAR folder location first, failing that POSCAR folder location, or failing that raise an error
def get_structure(folder, files):
    if "CONTCAR" in files:
        return os.path.join(folder, "CONTCAR")
    elif "POSCAR" in files:
        return os.path.join(folder, "POSCAR")
    else:
        raise FileNotFoundError(f"No CONTCAR or POSCAR in {folder}")

#Find initial and final folders for comparisons
def find_transition(base=os.getcwd(),initial=("ini",),final=("fin",)):
    
    structure_files = [] #Initialise array

    #Lower case for consistency
    initial = tuple(i.lower() for i in initial)
    final = tuple(f.lower() for f in final)

    for root, dirs, files in os.walk(base): #Walk from base directory, i.e., where the python file is

        #Find the initial and final states
        ini_name = next((d for d in dirs if d.lower() in initial), None)
        fin_name = next((d for d in dirs if d.lower() in final), None)

        # look for folders containing ini + fin
        if ini_name and fin_name:

            #After finding the initial and final folders, join them alongside their rooted folder directories
            ini_dir = os.path.join(root, ini_name)
            fin_dir = os.path.join(root, fin_name)

            #Collect file names in these directories
            ini_files = os.listdir(ini_dir)
            fin_files = os.listdir(fin_dir)

            #Collect POSCAR/CONTCAR directories
            ini_struct = get_structure(ini_dir, ini_files)
            fin_struct = get_structure(fin_dir, fin_files)

            #Root folder, relative to code location
            transition = os.path.relpath(root, base)

            #Add directories and root folder into a file for easier access
            structure_files.append({
                "transition": transition, 
                "ini_structure": ini_struct, #Initial structure
                "fin_structure": fin_struct, #Final structure
            })

    #Check item lists just in case to ensure that each file was indeed read
    #for item in structure_files:
    #    print(item["transition"])
    #    print("  ini:", item["ini_structure"])
    #    print("  fin:", item["fin_structure"])

    return structure_files #Output the file locations

#If Mode 3, save any constants in a json file to reuse it
def save_json(entry, filename):
    data = {
        "value": entry.tolist() if hasattr(entry, "tolist") else entry
    }
    with open(filename, "w") as f:
        json.dump(data, f)
#If Mode 3, load any constants from the saved json file to reuse it
def load_json(filename):
    try:
        with open(filename, "r") as f:
            return np.array(json.load(f)["value"])
    except FileNotFoundError:
        return None
#If Mode 3, delete the saved json file after each file is looped through
def delete_file(filename):
    try:
        os.remove(filename) #Delete if possible
    except FileNotFoundError:
        pass