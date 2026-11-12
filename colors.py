#Use this file to access functions that alter colors

#Import functions for coloring
from ase.data.colors import jmol_colors
from ase.data import atomic_numbers, chemical_symbols
from matplotlib.colors import is_color_like

#Collect atom colors
def get_atom_colors(atoms,element_colors=None):

    # Validate user-defined colours, if provided
    if element_colors is not None:

        # Check each supplied element and its corresponding colour
        for symbol, colour in element_colors.items():

            # Check that the supplied element symbol is valid
            if symbol not in chemical_symbols[1:]:
                raise ValueError(f"Invalid chemical element symbol in element_colors: '{symbol}'.")

            # Check that the supplied colour is valid
            if not is_color_like(colour):
                raise ValueError(f"Invalid colour for element '{symbol}': {colour}.")

    #Initialise color array/dictionary
    colors = {}
    #Check each atom in the structure to collect elements
    for i, atom in enumerate(atoms):
        #Use user-defined colors (highest priority)
        if element_colors is not None and atom.symbol in element_colors:
            colors[i] = element_colors[atom.symbol]
        #Fallback to Jmol defaults if necessary
        else:
            colors[i] = jmol_colors[atomic_numbers[atom.symbol]]

    #print(colors) #Print color list if desired
    
    return colors #Output colors