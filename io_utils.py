#For data acquisition

import numpy as np #Mathematical calculations
import json #JS file
import os #Operating system
from atoms import load_atoms

#Collect CONTCAR folder location first, failing that POSCAR folder location, or failing that raise an error
def get_structure(folder, files):
    if "CONTCAR" in files:
        return os.path.join(folder, "CONTCAR")
    elif "POSCAR" in files:
        return os.path.join(folder, "POSCAR")
    else:
        raise FileNotFoundError(f"No CONTCAR or POSCAR in {folder}")

#Find an NEB data file in the transition folder
def get_neb_file(folder, files, neb_filenames=("neb.dat", "NEB.dat")):

    for filename in neb_filenames:

        if filename in files:
            return os.path.join(folder, filename)

    return None #In case of an improper filename

#Find and load a reference structure. CONTCAR is preferred over POSCAR, but either valid file is usable.
def get_reference_structure(folder,repeat=(1,1,1)):

    for filename in ("CONTCAR", "POSCAR"):
        path = os.path.join(folder, filename)
        if os.path.isfile(path):
            try:
                return load_atoms(path,repeat)
            except Exception:
                print(f"Could not load reference structure: {path}")

    #Return None if neither structure could be loaded.
    return None

#Find initial and final folders for comparisons
def find_transition(base=os.getcwd(),neb_filenames=("neb.dat", "NEB.dat")):
    
    structure_files = [] #Initialise array

    for root, dirs, files in os.walk(base): #Walk from base directory, i.e., where the python file is

        neb_structures = {} #Collect all structures here

        #Check each folder in the directories
        for folder in dirs:

            # Check for numbered NEB image folders
            if folder.isdigit():

                image_number = int(folder) #Check if the folder is a number in the first place
                image_dir = os.path.join(root, folder) #Create a new directory to collect the CONTCAR/POSCAR file to be visualised

                try:
                    image_files = os.listdir(image_dir) #List all files in the image directory
                    image_struct = get_structure(image_dir, image_files) #Check if CONTCAR or POSCAR are present
                    neb_structures[image_number] = image_struct #Update the neb_structures array with the new directory to the CONTCAR/POSCAR file
                except FileNotFoundError:
                    pass #Ignore if neither file can be found

        if neb_structures:
            transition = os.path.relpath(root, base) #List the transition

            neb_structures = dict(sorted(neb_structures.items())) #Sort NEB images by image number

            #Look for an NEB data file in the same folder as the image folders
            neb_file = get_neb_file(root,files,neb_filenames)

            structure_files.append({#Append key names and directories
                "transition": transition,
                "neb_structures": neb_structures,
                "neb_file": neb_file})

    return structure_files #Output the file locations