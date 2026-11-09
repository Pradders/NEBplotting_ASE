#User inputs

import math #Mathematical functions
from geometry import build_shift, apply_shift #Atomic shifting functions
import os #Operating system

_current_mode = None #Global variable in selecting mode of imaging

#Obtain integers for certain prompts. If not an integer, then repeat.
def get_int(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Invalid input. Please enter an integer (e.g., -1, 0, 1).")

# Obtain a floating number. If not a float, then repeat.
def get_float(prompt):

    while True:
        try:
            value = float(input(prompt))

            if math.isfinite(value): #Check that the floating value is valid
                return value

            print("Invalid input. Please enter a finite number.")

        except ValueError:
            print("Invalid input. Please enter a number.")

#Check if there is a reference folder and if the user wants to apply a reference structure
def get_reference_settings(reference_symbols, reference_folder="Reference"):
    while True: #If the conditions are not met, then restart the loop
        reference_mode = input(
            "Select reference mode:\n"
            "1: No reference\n"
            "2: Use first NEB image as reference\n"
            "3: Use external reference folder\n"
            "Enter 1, 2, or 3: "
        ).strip()

        if reference_mode == "1": #No reference structure to be applied
            return None, None

        elif reference_mode == "2": #Apply only specific common elements of the first NEB image 
            if reference_symbols is None or len(reference_symbols) == 0:
                print("Reference symbols must be specified for mode 2.")
                continue
            return None, reference_symbols

        elif reference_mode == "3": #Use the surface specified in a reference folder
            if reference_symbols is None or len(reference_symbols) == 0:
                print("Reference symbols must be specified for mode 3.")
                continue

            if not reference_folder or not os.path.isdir(reference_folder): #Check that the folder exists in the first place, or otherwise the loop restarts
                print(f"Reference folder not found: {reference_folder}.")
                continue

            return reference_folder, reference_symbols

        else:
            print("Invalid selection. Enter 1, 2, or 3.")

#Choose which structures to display
def choose_neb_display():

    #Keep looping to obtain a correct response
    while True:
        print("\nSelect NEB structure display:")
        print("1: Initial / Final")
        print("2: Initial / TS / Final")
        print("3: Initial / All NEB images / Final")

        #Which display method?
        mode = get_int("Enter display mode (1/2/3): ")

        #Ask if correct, otherwise restart loop
        if mode not in (1, 2, 3):
            print("Invalid display mode, try again.\n")
            continue
        if not confirm(f"Confirm display mode {mode}?"):
            continue
        #Else carry on as normal
        if mode == 1:
            return "ini_fin"
        elif mode == 2:
            return "ini_ts_fin"
        elif mode == 3:
            return "ini_all_fin"

#Manually enter key energy information (TS, enthalpy) for the NEB calculation
def manual_key_energies(image_numbers):

    if not image_numbers:
        raise ValueError("No NEB image numbers are available.")

    while True:
        #Ask for the TS image number
        ts_image = get_int("Enter TS image number: ")
        #Check that the selected image exists
        if ts_image in image_numbers:
            break
        print("Invalid image number. Please select an available NEB image.")

    #Ask for the TS energy
    ts_energy = get_float("Enter TS energy: ")
    #Ask for the reaction enthalpy
    enthalpy = get_float("Enter reaction enthalpy: ")

    return ts_image, ts_energy, enthalpy

#Ask the user to select the transition-state image number
def manual_ts_image(image_numbers):
    
    if not image_numbers:
        raise ValueError("No NEB image numbers are available.")

    while True:
        ts_image = get_int("Enter TS image number: ")

        if ts_image in image_numbers:
            return ts_image

        print("Invalid image number. Please select an available NEB image.")

#Ask the user to enter the energy for every NEB image. The first image is assigned as 0 eV.
def manual_image_energies(image_numbers):

    if not image_numbers:
        raise ValueError("No NEB image numbers are available.")

    image_energies = {}

    for image_number in image_numbers:
        if image_number == image_numbers[0]: #Keep here to avoid asking
            image_energies[image_number] = 0.0
            continue

        #The final image uses the reaction enthalpy separately
        if image_number == image_numbers[-1]:
            continue

        energy = get_float(f"Enter energy for image {image_number} (Image {image_numbers[0]} = 0 eV): ")
        image_energies[image_number] = energy

    #Ask for the reaction enthalpy separately
    enthalpy = get_float("Enter reaction enthalpy (final image): ")

    return image_energies, enthalpy

#Ask the user to enter only the reaction enthalpy
def manual_reaction_enthalpy():

    return get_float("Enter reaction enthalpy: ")

#Choose how shifts will be applied
def choose_shift_mode():

    global _current_mode #Global variable

    if _current_mode is not None: #Return the previously selected mode if one has already been chosen
        return _current_mode

    #Choose a shift method
    while True:
        print("\nSelect shift mode")
        print("1: MANUAL shift for EACH image") #Mode 1: manual shift for each individual image
        print("2: SAME shift for ALL images in EACH SYSTEM") #Mode 2: same shift within each individual system
        print("3: NO shift to ANY image") #Mode 3: no applied shift to any individual image

        #Which method? Select an integer among 1, 2, and 3.
        mode = get_int("Enter mode (1/2/3): ")
        #Ask if correct, else restart loop
        if mode not in (1, 2, 3):
            print("Invalid shift mode, try again.\n")
            continue
        if not confirm(f"Confirm shift mode {mode}?"):
            continue
        _current_mode = mode #Keep selected method constant throughout program
        return mode

#Choose which energy information to add to the figures
def choose_energy_mode():

    #Keep looping to obtain a correct response
    while True:

        print("\nSelect energy information.")
        print("1: KEY energies (Initial / TS / Final).")
        print("2: ALL energies (every NEB image).")

        #Ask for the desired option
        mode = get_int("Enter option (1/2): ")

        #Check the selection
        if mode not in (1, 2):
            continue
        if not confirm(f"Confirm energy mode {mode}?"):
            print("Invalid energy option, try again.\n")
            continue
        if mode == 1:
            return "key"
        elif mode == 2:
            return "all"

#Choose whether to add energy information to the figures
def choose_energy_display():

    #Keep looping to obtain a correct response
    while True:

        print("\nAdd energy information to figures?")
        print("1: YES")
        print("2: NO")

        #Ask for the desired option
        mode = get_int("Enter option (1/2): ")

        #Check the selection
        if mode not in (1, 2):
            print("Invalid energy display option, try again.\n")
            continue
        if not confirm(f"Confirm mode {mode}?"):
            continue
        if mode == 1:
            return True
        elif mode == 2:
            return False

#Used to accept a result
def confirm(prompt="Accept this result/outcome?"):
    while True:
        ans = input(f"{prompt} (y/n): ").strip().lower()
        if ans in ("y", "n"):
            return ans == "y"
        print("Please enter 'y' or 'n'.")

#Depending on the mode selected, apply the appropriate shifting method
def process_structures(neb_structures):

    from plotting import view_cleanup #Create a temporary figure(s)

    if not neb_structures:
        raise ValueError("No NEB structures are available for processing.")

    mode = choose_shift_mode() #Which mode?

    if mode == 1: #Mode 1: manual shift for each individual image

        test_structures = {} #Initialise

        for image_number, atoms in neb_structures.items(): #Loop through each NEB image
            while True:
                shift = build_shift(atoms,get_int) #Prepare shift to this individual image
                test = apply_shift(atoms,shift) #Apply shift to this individual image
                view_cleanup(test) #Check images temporarily if they look OK, especially after input shift constant factor

                if confirm(): #Accept result or not
                    test_structures[image_number] = test #Collect data
                    break

        return test_structures #Return shifted results

    elif mode == 2: #Mode 2: same shift for all images in each system

        while True:
            #Find the first image
            first_image = neb_structures[min(neb_structures)]
                            
            shift = build_shift(first_image,get_int) #Prepare shift

            #Apply the same shift to every image
            test_structures = {image_number: apply_shift(atoms, shift) for image_number, atoms in neb_structures.items()}
                
            #Check images temporarily if they look OK, especially after input shift constant factor
            for atoms in test_structures.values():
                view_cleanup(atoms)
                
            if confirm(): #Accept result or not
                return test_structures #Return shifted results
    
    elif mode == 3: #Mode 3: no applied shift to any individual image

        return neb_structures #Leave input unchanged