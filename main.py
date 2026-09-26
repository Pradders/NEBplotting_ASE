#All functions are located within external files. Many of them reference each other.
#Only three are run independently and should be called within this main file (see below)
from io_utils import find_transition #Collect file locations (POSCAR, CONTCAR, ACF.dat) for subsequent call
from plotting import plot_structure #Plot Initial/Final structures
from inputs import choose_neb_display, choose_energy_display, choose_energy_mode
import os #Operating system

#Define the main function to run imported functions
def main(base,repeat=(1,1,1),save_dir="NEB_plots",views=None,element_colors=None,layout="horizontal",
         labels=None,styles=None,reference_folder=None,reference_symbols=("Ni",)):

    #Choose which NEB structures will be displayed
    display = choose_neb_display()

    #Choose whether energy information will be displayed
    add_energies = choose_energy_display()

    #Choose which energy information will be displayed
    if add_energies and display == "ini_all_fin":
        energy_mode = choose_energy_mode()
    else:
        energy_mode = "key"

    #Collect file locations for all NEB systems
    structure_files = find_transition(base)

    #Process each NEB system
    for res in structure_files:

        parts = res["transition"].split(os.sep)
        transition_name = "_".join(parts)
        print(f"\nProcessing: {transition_name}")

        try: #Output the name of the transition here to enable the user to know which system has been processed
            plot_structure(res,repeat,save_dir,views,element_colors,layout,labels,styles,display,
                           add_energies,energy_mode,reference_folder,reference_symbols)
            
        except Exception as e: #In case the file name cannot be found, pass an error message
            print(f"Error processing {res['transition']}: {e}")
            continue

#Entry point/switch to run function
if __name__ == "__main__":
    base = os.getcwd()   # start from script location

    # Optional reference structure used to keep the substrate representation consistent across different systems.
    # Use reference_folder = None to analyse structures without an external reference.
    # Else, direct the variable to the folder containing the relevant CONTCAR/POSCAR file.
    reference_folder = os.path.join(base,"Reference") #Folder containing reference CONTCAR/POSCAR
    #reference_folder = None

    reference_symbols = ("Ni",) #Elements belonging to the reference structure

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
    "ts": "Transition",
    "final": "Final"}

    #Font styles
    styles = {
    "heading": {
        "fontname": "Times New Roman",
        "fontsize": 24,
        "fontweight": "bold"}
    }

    main(base, repeat, save_dir, views, element_colors, layout, labels, styles, reference_folder, reference_symbols) #Start main function