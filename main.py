#All functions are located within external files. Many of them reference each other.
#Only three are run independently and should be called within this main file (see below)
from io_utils import find_transition #Collect file locations (POSCAR, CONTCAR, ACF.dat) for subsequent call
from plotting import plot_structure #Plot Initial/Final structures
import os #Operating system

#Define the main function to run imported functions
def main(base, INITIAL=("ini",), FINAL=("fin",), repeat=(1,1,1), save_dir="NEB_plots",views=None,element_colors=None,layout="horizontal",labels=None,styles=None):
    structure_files = find_transition(base,INITIAL,FINAL)
    for res in structure_files:
        try: #Output the name of the transition here to enable the user to know which system has been processed
            parts = res["transition"].split(os.sep)
            transition_name = "_".join(parts)
            print(f"\nProcessing: {transition_name}")
        except Exception as e: #In case the file name cannot be found, pass an error message
            print(f"Error processing {res['transition']}: {e}")
            continue
        plot_structure(res,repeat,save_dir,views,element_colors,layout,labels,styles)

#Entry point/switch to run function
if __name__ == "__main__":
    base = os.getcwd()   # start from script location

    INITIAL = ("ini","initial","is") #Default is to store key files of each transition in "ini" (initial state) and "fin" (final state).
    #If there are alternative names, then please include them manually
    FINAL = ("fin","final","fs")
    repeat = (1,1,1) #In case of adsorbate atoms extending over the unit cell, this will increase the size of periodicity
    save_dir="NEB_plots" #Save folder

    views = [ #Different rotations to view atomic/surface configurations
    ('0x,0y,0z'),     # top
    #('-90x,0y,0z'),    # side
    #('-90x,-90y,0z'), # front
    ] #Choose one of ('0x,0y,0z') #top, ('90x,0y,0z') #side, ('-90x,-90y,0z') #front, or add other rotations as desired

    element_colors = { #Define desired colors for atoms in POSCAR/CONTCAR if desired
        "Ni": "lightgray",
        "C": "black",
        #"O": "red", #O is already red by default
        #"H": "white", #H is already white by default
        }
    
    layout = "horizontal" #also "vertical"
    #"horizontal" arranges all images horizontally, "vertical" arranges all images vertically

    #Different labels
    labels = {
    "initial": "Initial",
    "final": "Final"}

    #Font styles
    styles = {
    "heading": {
        "fontname": "Times New Roman",
        "fontsize": 24,
        "fontweight": "bold"}
    }

    main(base, INITIAL, FINAL, repeat, save_dir, views, element_colors, layout, labels, styles) #Start main function