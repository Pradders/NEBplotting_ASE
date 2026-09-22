import numpy as np #Mathematical calculations
from ase.data import covalent_radii, atomic_numbers #Collect atomic data

#Calculate maximum covalent radius based on the elements present
def max_radius(atoms):
    symbols = atoms.get_chemical_symbols()
    radii = [covalent_radii[atomic_numbers[s]] for s in symbols]
    diameter = 2*max(radii) #Use the diameter instead
    return diameter

#Create a vector that indicates the direction of the shift
def build_shift(atoms,get_int):

    from plotting import view_cleanup #Create a temporary figure(s)
    
    shift = np.zeros(3) #Initiate variable with zeroes
    d = max_radius(atoms) #Use the maximum radius/diameter

    #Input a message to subsequently preview the structure
    print("\nPreviewing structure.")
    view_cleanup(atoms)

    #Print a message to present the shift, especially in case of changes to the relative atom
    print(f"\nManual shift using max_radius = {d:.3f} Å")

    #Input shifts to move the system based on the number of Ni atoms. Sign is important here as well. Negative sign means left/down shift. Positive sign means right/up shift.
    nx = get_int("Shift in x (multiples of diameter, N.B. negative = left, positive = right): ")
    ny = get_int("Shift in y (multiples of diameter, N.B. negative = down, positive = up): ")

    #Shifts multiplied here
    shift[0] = nx*d
    shift[1] = ny*d

    return shift #Return shift

#Apply a shift to an atomic structure
def apply_shift(atoms, shift):

    atoms_translate = atoms.copy() #Cannot return atoms without changing variable name, otherwise the original structure will be retained
    atoms_translate.translate(shift) #Shift here
    atoms_translate.wrap() #Wrap back into unit cell

    #Return translated atoms
    return atoms_translate