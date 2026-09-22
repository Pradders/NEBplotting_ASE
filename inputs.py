from geometry import build_shift, apply_shift #Atomic shifting functions
from io_utils import save_json, load_json

_current_mode = None #Global variable in selecting mode of imaging

#Obtain integers for certain prompts. If not an integer, then repeat.
def get_int(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Invalid input. Please enter an integer (e.g., -1, 0, 1).")

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
        if mode in [1, 2, 3]:
            confirm_mode = input(f"Confirm display mode {mode}? (y/n): ").lower()

            if confirm_mode == "y":
                if mode == 1:
                    return "ini_fin"
                elif mode == 2:
                    return "ini_ts_fin"
                elif mode == 3:
                    return "ini_all_fin"

        print("Invalid display mode, try again.\n")

#Manually enter key energy information (TS, enthalpy) for the NEB calculation
def manual_key_energies(image_numbers):

    #TS image number
    while True:
        try:
            #Ask for the TS image number
            ts_image = int(input("Enter TS image number: "))
            #Check that the selected image exists
            if ts_image in image_numbers:
                break
            print("Invalid image number. Please select an available NEB image.")
        except ValueError:
            print("Invalid input. Please enter an integer.")

    #TS energy
    while True:
        try:
            #Ask for the TS energy
            ts_energy = float(input("Enter TS energy: "))
            break
        except ValueError:
            print("Invalid input. Please enter a (floating) number.")

    #Reaction enthalpy
    while True:
        try:
            #Ask for the reaction enthalpy
            enthalpy = float(input("Enter reaction enthalpy: "))
            break
        except ValueError:
            print("Invalid input. Please enter a (floating) number.")

    return ts_image, ts_energy, enthalpy

#Ask the user to select the transition-state image number
def manual_ts_image(image_numbers):

    while True:
        try:
            ts_image = int(input("Enter TS image number: "))

            if ts_image in image_numbers:
                return ts_image

            print("Invalid image number. "
                "Please select an available NEB image.")

        except ValueError:
            print("Invalid input. Please enter an integer.")

#Ask the user to enter the energy for every NEB image
def manual_image_energies(image_numbers):

    image_energies = {}

    for image_number in image_numbers:
        if image_number == image_numbers[0]: #Keep here to avoid asking
            image_energies[image_number] = 0.0
            continue

        #The final image uses the reaction enthalpy separately
        if image_number == image_numbers[-1]:
            continue

        while True:
            try:
                energy = float(input(f"Enter energy for image {image_number} (Image 0 = 0 eV): "))
                image_energies[image_number] = energy
                break

            except ValueError:
                print("Invalid input. Please enter a (floating) number.")

    #Ask for the reaction enthalpy separately
    while True:
        try:
            enthalpy = float(input("Enter reaction enthalpy (final image): "))
            break

        except ValueError:
            print("Invalid input. Please enter a (floating) number.")

    return image_energies, enthalpy

#Ask the user to enter only the reaction enthalpy
def manual_reaction_enthalpy():

    while True:
        try:
            enthalpy = float(input("Enter reaction enthalpy: "))
            return enthalpy

        except ValueError:
            print("Invalid input. Please enter a (floating) number.")

#Choose how shifts will be applied
def choose_shift_mode():

    global _current_mode #Global variable
    if _current_mode is not None: #Return the previously selected mode if one has already been chosen
        return _current_mode

    #Choose a shift method
    while True:
        print("\nSelect shift mode:")
        print("1: MANUAL shift for EACH image") #Mode 1: manual shift for each individual image
        print("2: SAME shift for ALL images in EACH SYSTEM") #Mode 1: same shift within each individual system
        print("3: NO shift to ANY image") #Mode 3: no applied shift to any individual image

        #Which method? Select an integer among 1, 2, and 3.
        mode = get_int("Enter mode (1/2/3): ")
        #Ask if correct, else restart loop
        if mode in [1, 2, 3]:
            confirm_mode = input(f"Confirm mode {mode}? (y/n): ").lower() #Confirmation
            if confirm_mode == "y":
                _current_mode = mode #Keep selected method constant throughout program
                return mode

        print("Invalid mode, try again.\n")

#Choose which energy information to add to the figures
def choose_energy_mode():

    #Keep looping to obtain a correct response
    while True:

        print("\nSelect energy information:")
        print("1: KEY energies (Initial / TS / Final)")
        print("2: ALL energies (every NEB image)")

        #Ask for the desired option
        mode = get_int("Enter option (1/2): ")

        #Check the selection
        if mode in [1, 2]:

            #Ask for confirmation
            confirm_mode = input(f"Confirm option {mode}? (y/n): ").lower()

            if confirm_mode == "y":
                if mode == 1:
                    return "key"
                elif mode == 2:
                    return "all"

        print("Invalid option, try again.\n")

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
        if mode in [1, 2]:

            #Ask for confirmation
            confirm_mode = input(f"Confirm option {mode}? (y/n): ").lower()

            if confirm_mode == "y":

                if mode == 1:
                    return True

                elif mode == 2:
                    return False

        print("Invalid option, try again.\n")

#Used to accept a result
def confirm():
    while True:
        ans = input("Accept this result/outcome? (y/n): ").lower()
        if ans in ["y", "n"]:
            return ans == "y"
        print("Please enter 'y' or 'n'.")

#Depending on the mode selected, apply the appropriate shifting method
def process_structures(neb_structures):

    from plotting import view_cleanup #Create a temporary figure(s)

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

            #Apply this shift to every image
            test_structures = {}

            for image_number, atoms in neb_structures.items():
                test_structures[image_number] = apply_shift(atoms, shift) #apply the desired shift to each image
                
            #Check images temporarily if they look OK, especially after input shift constant factor
            for image_number, atoms in test_structures.items():
                view_cleanup(atoms)
                
            if confirm(): #Accept result or not
                break

        return test_structures #Return shifted results
    
    elif mode == 3: #Mode 3: no applied shift to any individual image

        return neb_structures #Leave input unchanged
