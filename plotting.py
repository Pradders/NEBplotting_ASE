#Plotting functions
#When defining each of the functions, where possible or necessary, default values are set, unless a new input is allocated in the main file

#Use to collect, visualise atomic structures
from ase.visualize.plot import plot_atoms
#Use to write temporary files
from ase.io import write

#Plot atoms
import matplotlib.pyplot as plt #Plot adsorption surfaces
import numpy as np
import os #Operating system

#Import external functions
from atoms import load_atoms
from inputs import process_structures
from colors import get_atom_colors
from layouts import create_axes, iter_axes
from check import check_consistency, check_reference_structure
from analysis import read_neb_data, find_ts_image, find_ts_energies, find_image_energies, find_reaction_enthalpy
from io_utils import get_reference_structure

# Default labels
DEFAULT_LABELS = {
    "initial": "Initial",
    "ts": "Transition",
    "final": "Final",
}

# Default styles
DEFAULT_STYLES = {
    "heading": {
        "fontname": "Times New Roman",
        "fontsize": 24,
        "fontweight": "bold"
    }
}

#Create a temporary file to check images
def view_cleanup(atoms, filename="temp_view.png", pause=True):

    #Write structure to temporary image
    write(filename, atoms,format="png",rotation="0x,0y,0z",show_unit_cell=1)

    #Display image
    img = plt.imread(filename)
    plt.figure()
    plt.imshow(img)
    plt.axis("off")
    plt.show(block=False)

    #Pause for inspection
    if pause:
        input("Press Enter to close the figure...")

    #Close figure
    plt.close()

    #Delete temp file
    try:
        os.remove(filename)
    except OSError:
        pass

#Split selected images and labels into groups for separate figures
def split_images(selected_images, selected_labels, max_images):

    #Check that the maximum number of images is valid
    if max_images < 1:
        raise ValueError("max_images must be at least 1")

    #Split images and labels into matching groups
    image_groups = []
    label_groups = []

    for i in range(0, len(selected_images), max_images): #
        image_groups.append(selected_images[i:i + max_images])
        label_groups.append(selected_labels[i:i + max_images])

    return image_groups, label_groups

#Prepare a visual copy of an NEB image so that the selected reference atoms use the same periodic representation as the reference structure.
def prepare_visual_structure(atoms,reference_atoms,reference_symbols):

    visual_reference = reference_atoms.copy()

    #Get fractional coordinates inside the unit cell.
    current_scaled = atoms.get_scaled_positions(wrap=False)
    reference_scaled = reference_atoms.get_scaled_positions(wrap=True)

    cell = atoms.get_cell()

    #Keep track of the occurrence number of each element.
    #This allows the reference structure to contain more than one type of substrate atom.
    reference_indices = {}
    current_indices = {}

    for symbol in reference_symbols:

        reference_indices[symbol] = [
            i for i, atom_symbol
            in enumerate(reference_atoms.get_chemical_symbols())
            if atom_symbol == symbol
        ]

        current_indices[symbol] = [
            i for i, atom_symbol
            in enumerate(atoms.get_chemical_symbols())
            if atom_symbol == symbol
        ]

    # Find one common periodic translation for the whole structure.
    best_shift = np.zeros(3)
    best_distance = np.inf

    for x_shift in (-1, 0, 1):

        for y_shift in (-1, 0, 1):

            total_distance = 0.0

            for symbol in reference_symbols:

                for reference_index, current_index in zip(
                    reference_indices[symbol],
                    current_indices[symbol]
                ):

                    # Current atom with a common periodic translation.
                    candidate = current_scaled[current_index].copy()
                    candidate[0] += x_shift
                    candidate[1] += y_shift

                    # Difference from the corresponding reference atom.
                    difference = candidate - reference_scaled[reference_index]

                    # Convert to Cartesian distance.
                    distance = np.linalg.norm(difference @ cell)

                    total_distance += distance**2

            # Keep the common translation giving the smallest total distance for all reference atoms.
            if total_distance < best_distance:

                best_distance = total_distance
                best_shift = np.array([x_shift, y_shift, 0.0])

    # Apply the SAME periodic translation to the entire structure.
    reference_scaled += best_shift
    visual_reference.set_cell(cell)
    visual_reference.set_scaled_positions(reference_scaled)

    # Collect only the atoms that are NOT part of the reference substrate.
    non_reference_indices = [
        i for i, symbol in enumerate(atoms.get_chemical_symbols())
        if symbol not in reference_symbols]

    visual_adsorbates = atoms[non_reference_indices]

    # Combine reference substrate with the non-reference atoms.
    visual_atoms = visual_reference + visual_adsorbates

    return visual_atoms

#Plot all configurations
def plot_structure(res,repeat=(1,1,1),save_dir="NEB_plots",views=None,element_colors=None,layout="horizontal",
                   labels=None,styles=None,display="ini_fin",add_energies=False,energy_mode="key",reference_folder=None,
                   reference_symbols=None,max_images=10):
 
    #Set views to default if not given
    if views is None:
        views = [('0x,0y,0z')]

    #Check the energy display mode
    if energy_mode not in ["key", "all"]:
        raise ValueError("energy_mode must be either 'key' or 'all'")

    #Check labels. Use default if invalid or not passed.
    try:
        labels["initial"]
        labels["ts"]
        labels["final"]
    except (TypeError, KeyError):
        labels = DEFAULT_LABELS

    #Check styles. Use default if invalid or not passed.
    try:
        styles["heading"]
    except (TypeError, KeyError):
        styles = DEFAULT_STYLES

    check_consistency(res) #Check atomic and elemental consistency between atomic files

    #Load the reference structure if a reference folder was provided
    if reference_folder is not None:
        reference_atoms = get_reference_structure(reference_folder, repeat)
    else:
        reference_atoms = None

    #Read all NEB configurations
    neb_structures = {}

    for image_number, path in res["neb_structures"].items():
        #Load the atomic structure
        atoms = load_atoms(path,repeat)
        #Use the supplied reference structure if available
        if reference_atoms is not None:
            check_reference_structure(atoms,reference_atoms,reference_symbols)
        #Otherwise use the first NEB image as the reference
        elif image_number == min(res["neb_structures"]):
            reference_indices = [i for i, symbol in enumerate(atoms.get_chemical_symbols()) if symbol in reference_symbols]
            reference_atoms = atoms[reference_indices].copy()
        #Prepare the visual structure
        visual_atoms = prepare_visual_structure(atoms,reference_atoms,reference_symbols)
        #Store the prepared structure
        neb_structures[image_number] = visual_atoms

    #Apply the desired shifts to the NEB structures
    neb_structures = process_structures(neb_structures)

    #Check that at least one structure was found
    if not neb_structures:
        raise ValueError(f"No NEB structures found for {res['transition']}")

    #Collect the available image numbers
    image_numbers = sorted(neb_structures)

    #Initialise NEB data and energy information
    neb_data = None
    ts_image = None
    ts_energy = None
    enthalpy = None
    image_energies = None

    #Read NEB data when TS or energy information is required
    if display == "ini_ts_fin" or add_energies:
        neb_data = read_neb_data(res["neb_file"])

    #Find the TS image when it is needed for display
    if display == "ini_ts_fin":

        #When energies are not requested, only the TS image is required
        if not add_energies:
            ts_image = find_ts_image(neb_data,image_numbers,res["transition"])

    #Collect energy information when requested
    if add_energies:

        #Initial / Final only needs the reaction enthalpy
        if display == "ini_fin":
            enthalpy = find_reaction_enthalpy(neb_data)

        #Initial / TS / Final needs the TS information
        elif display == "ini_ts_fin":
            ts_image, ts_energy, enthalpy = find_ts_energies(neb_data,image_numbers,res["transition"])

        elif display == "ini_all_fin":

            if energy_mode == "all":
                #Collect the energy for every NEB image
                image_energies, enthalpy = find_image_energies(neb_data,image_numbers)

                #Find the TS from the highest-energy NEB image
                ts_image = max(image_energies,key=image_energies.get)

                #Collect the corresponding TS energy
                ts_energy = image_energies[ts_image]

            else:
                #Collect the TS energy and reaction enthalpy
                ts_image, ts_energy, enthalpy = find_ts_energies(neb_data,image_numbers,res["transition"])

    #Select which structures should be displayed
    if display == "ini_fin": #only initial and final image
        #Initial = lowest numbered image
        selected_images = [image_numbers[0], image_numbers[-1]]
        selected_labels = [labels["initial"], labels["final"]]
    elif display == "ini_ts_fin": #include ts image        
        #Use the TS image identified by find_energies()
        selected_images = [image_numbers[0], ts_image, image_numbers[-1]]
        selected_labels = [labels["initial"], labels["ts"], labels["final"]]
    elif display == "ini_all_fin": #Display every available NEB image
        selected_images = image_numbers
        #Use the image number as the label for each NEB image
        selected_labels = [str(image_number) for image_number in selected_images]
        #Replace the first and last labels with Initial and Final
        selected_labels[0] = labels["initial"]
        selected_labels[-1] = labels["final"]
        #Replace the TS image label if the TS image has been identified
        if ts_image is not None and ts_image in selected_images:
            ts_position = selected_images.index(ts_image)
            selected_labels[ts_position] = labels["ts"]
    else:
        raise ValueError(f"Unknown NEB display mode: {display}")

    #Split the selected images into separate figures
    image_groups, label_groups = split_images(selected_images,selected_labels,max_images)

    # Element colors, as set in main file
    atom_colors = get_atom_colors(neb_structures[image_numbers[0]],element_colors)

    #Different rotations of images
    n_rot = len(views)

    # Make save directory
    os.makedirs(save_dir, exist_ok=True)

    #Use directory name to name image and remove undesirable separators
    parts = res["transition"].split(os.sep)

    #Build folder
    base_folder = os.path.join(save_dir,parts[0])
    #Use *parts if separating further
    os.makedirs(base_folder, exist_ok=True)

    #Plot according to desired layout
    for group_number, (image_group, label_group) in enumerate(zip(image_groups, label_groups),start=1):

        #Number of structures to display
        n_structures = len(image_group)

        fig, axes = create_axes(layout, n_rot, n_structures) #Figure arrangement

        #Plot according to selected layout
        for i,rotation in enumerate(views):

            for j,image_number in enumerate(image_group): #In case of multiple rotations

                #Get the current atomic structure
                atoms = neb_structures[image_number]

                if layout == "horizontal": #Horizonal array of figures

                    #Select the current axis
                    ax = axes[i,j]

                elif layout == "vertical": #Vertical array of figures
                
                    #Select the current axis
                    ax = axes[j,i]

                #Plot the atomic structure
                plot_atoms(atoms, ax, rotation=rotation, show_unit_cell=0, colors=atom_colors)

                #Add the appropriate label
                ax.set_title(label_group[j], **styles["heading"])

                #Add the corresponding energy below the structure
                if add_energies:

                    #Show the complete NEB energy profile
                    if energy_mode == "all":
                        if image_number in image_energies:
                            energy = image_energies[image_number]
                        #Use the reaction enthalpy for the final image
                        elif image_number == image_numbers[-1]:
                            energy = enthalpy
                        else:
                            energy = None

                    else:
                        #Initial energy is always zero
                        if image_number == image_numbers[0]:
                            energy = 0.0
                        #Use the TS energy
                        elif image_number == ts_image:
                            energy = ts_energy
                        #Use the reaction enthalpy for the final image
                        elif image_number == image_numbers[-1]:
                            energy = enthalpy
                        else:
                            energy = None

                    #Add energy in this format
                    if energy is not None:
                        ax.text(0.5, -0.05,f"{energy:.2f} eV",transform=ax.transAxes,ha="center",va="top",**DEFAULT_STYLES["heading"])

        #Remove borders and tick marks
        for ax in iter_axes(axes):
            #ax.set_xticks([]) #Tick marks, uncheck if border should remain
            #ax.set_yticks([])
            ax.set_axis_off()

        if len(image_groups) == 1: #Use the original filename if only one figure is created
            #Filename
            filename = "_".join(parts) + ".png"
        else: #Add a figure number in case of splitting
            filename = "_".join(parts) + f"_{group_number}.png"

        #Save file to desired directory
        save_path = os.path.join(base_folder, filename)

        #Save and close figures
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.close(fig)

    #Display figures if desired
    #plt.show()