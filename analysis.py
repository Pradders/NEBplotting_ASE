#Data analysis
#When defining each of the functions, where possible or necessary, default values are set, unless a new input is allocated in the main file

import math #Mathematical functions
from inputs import manual_key_energies, manual_ts_image, manual_image_energies, manual_reaction_enthalpy

#Read energy data from NEB.dat
def read_neb_data(path):

    #Check that the NEB data file exists
    if not path:
        return None

    #Initialise NEB data
    neb_data = {}

    #Open the NEB data file
    with open(path, "r") as f:

        #Read each line
        for line_number, line in enumerate(f, start=1):

            #Ignore blank lines
            if not line.strip():
                continue

            #Split the line into columns
            columns = line.split()

            #Ignore lines that do not contain five columns. Typical neb.dat files contain 5 columns.
            if len(columns) < 5:
                continue

            #Collect image number and energy
            try:
                image_number = int(columns[0]) #Typical neb.dat files contain a column of the image numbers...
            except ValueError:
                raise ValueError(f"Invalid image number in {path}, line {line_number}: '{columns[0]}'.")
            try:
                energy = float(columns[2]) #...and one of all energies.
            except ValueError:
                raise ValueError(f"Invalid energy in {path}, line {line_number}: '{columns[2]}'.")

            # Check that the energy is finite
            if not math.isfinite(energy):
                raise ValueError(f"Non-finite energy in {path}, line {line_number}: '{columns[2]}'.")

            #Store the energy against the image number
            neb_data[image_number] = energy

    #Check that data was found
    if not neb_data:
        return None

    return neb_data

#Find the reaction enthalpy
def find_reaction_enthalpy(neb_data):

    if neb_data is not None:

        if len(neb_data) < 2:
            raise ValueError("Insufficient NEB energy data: at least one NEB image and one final enthalpy entry are required.")

        #The final NEB data entry contains the reaction enthalpy
        return neb_data[max(neb_data)]

    #Ask manually when no NEB data file is available
    return manual_reaction_enthalpy()

#Find the highest-energy NEB image. This will be useful in the case where the energy labelled on the figure is undesired.
def find_ts_image(neb_data, image_numbers, transition=""):

    #Show the system currently being processed
    print("\nFinding transition-state image...")

    if transition:
        print(f"System: {transition}.") #Print the system to be viewed

    if neb_data is not None:
        #Check that there is at least one NEB image and one final enthalpy entry
        if len(neb_data) < 2:
            raise ValueError("Insufficient NEB energy data: at least one NEB image and one final enthalpy entry are required.")

        #Find the highest-energy NEB image, excluding the final enthalpy entry
        ts_image = max(list(neb_data)[:-1], key=neb_data.get)

    else:
        #Show the available NEB images
        print(f"Available images: {image_numbers}.")

        #No NEB data was found, so ask the user to select the TS image
        ts_image = manual_ts_image(image_numbers)

    #Check that the identified TS image is an available structure
    if ts_image not in image_numbers:
        raise ValueError(f"TS image {ts_image} from the energy data is not available among the NEB structures for {transition}: {image_numbers}.")

    return ts_image

#Find the highest-energy NEB image and its energy
def find_ts_energies(neb_data,image_numbers,transition=""):

    #Show the system currently being processed
    print("\nProcessing NEB energies...")

    if transition:
        print(f"System: {transition}.") #Print the system

    if neb_data is not None:

        #Check that there is at least one NEB image and one final enthalpy entry
        if len(neb_data) < 2:
            raise ValueError("Insufficient NEB energy data: at least one NEB image and one final enthalpy entry are required.")

        #Find the highest-energy NEB image. Store this just in case.
        ts_image = max(list(neb_data)[:-1], key=neb_data.get)

        #Check that the identified TS image is an available structure
        if ts_image not in image_numbers:
            raise ValueError(
                f"TS image {ts_image} from the energy data is not available among the NEB structures for {transition}: {image_numbers}.")

        #Collect the TS energy
        ts_energy = neb_data[ts_image]

        #Collect the final data point as the reaction enthalpy
        enthalpy = neb_data[max(neb_data)]

    else:
        #Show the available NEB images
        print(f"Available images: {image_numbers}.")

        #No NEB data was found and so ask for the values manually
        ts_image, ts_energy, enthalpy = manual_key_energies(image_numbers)
        
    return ts_image, ts_energy, enthalpy

#Collect the energy associated with each NEB image
def find_image_energies(neb_data, image_numbers):

    if neb_data is None:
        #No NEB data was found, so ask for the image energies manually
        return manual_image_energies(image_numbers)

    #Check that there is at least one NEB image and one final enthalpy entry
    if len(neb_data) < 2:
        raise ValueError("No NEB structures are available for energy analysis.")

    #The final data point represents reaction enthalpy rather than an NEB image
    neb_image_data = dict(list(neb_data.items())[:-1])
    enthalpy = neb_data[max(neb_data)] #Collect that last data point

    image_energies = {}

    for image_number in image_numbers:

        #Initial energy is always defined as zero
        if image_number == image_numbers[0]:
            image_energies[image_number] = 0.0

        #The final structure uses the reaction enthalpy separately
        elif image_number == image_numbers[-1]:
            continue

        #Use the NEB energy for all other available images
        elif image_number in neb_image_data:
            image_energies[image_number] = neb_image_data[image_number]

        else:
            raise ValueError(f"Energy data for NEB image {image_number} is missing.")

    return image_energies, enthalpy