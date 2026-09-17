#Use this file to access functions that alter colors

#Import functions for coloring
from ase.data.colors import jmol_colors
from ase.data import atomic_numbers

#Collect atom colors
def get_atom_colors(atoms,element_colors=None):
    #Initialise colour array/dictionary
    colors = {}
    #Go through each atom in the structure to collect elements
    for i, atom in enumerate(atoms):
        # user-defined colors (highest priority)
        if element_colors is not None and atom.symbol in element_colors:
            colors[i] = element_colors[atom.symbol]
        # fallback to Jmol defaults
        else:
            colors[i] = jmol_colors[atomic_numbers[atom.symbol]]

    #print(colors) #Print colour list if desired
    
    return colors #Output colors