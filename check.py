#Used to confirm certain consistencies in data

from collections import Counter #Counting function
from ase.io import read #Use to import atomic structures
from ase.data import chemical_symbols  # ASE chemical symbols
import numpy as np #Numerical analysis

# Check compatibility between two atomic cells
def check_cell_compatibility(atoms, reference_atoms, tolerance=1e-5):

    # Collect the cell matrices
    cell = atoms.get_cell().array
    reference_cell = reference_atoms.get_cell().array

    # Check cell dimensions and orientation
    if not np.allclose(cell, reference_cell, atol=tolerance, rtol=0):
        raise ValueError("Cell mismatch: the structures have incompatible cell dimensions or orientation.")

#Check length consistency of all NEB structures
def check_consistency(item):

    #Collect the NEB structures
    neb_structures = item["neb_structures"]

    if not neb_structures:
        raise ValueError(f"No NEB structures found for {item['transition']}.")

    #Sort the image numbers
    image_numbers = sorted(neb_structures)

    #Use the first image in the NEB list as the reference structure
    reference_number = image_numbers[0]
    reference_atoms = read(neb_structures[reference_number])

    #Check every other NEB image against the reference
    for image_number in image_numbers[1:]:
        #Read the current structure
        atoms = read(neb_structures[image_number])
        #Check that the structures contain the same number of atoms
        if len(atoms) != len(reference_atoms):
            raise ValueError(f"Atom count mismatch in {item['transition']}: image {reference_number}={len(reference_atoms)}, image {image_number}={len(atoms)}.")

        #Check element ordering consistency
        for i, (a_reference, a_current) in enumerate(zip(reference_atoms, atoms)):
            if a_reference.symbol != a_current.symbol:
                raise ValueError(f"Element mismatch at index {i} in {item['transition']}: image {reference_number}={a_reference.symbol}, image {image_number}={a_current.symbol}.")

#Check that the reference structure contains the requested elements and that the number of reference atoms matches the NEB structure.
def check_reference_structure(atoms,reference_atoms,reference_symbols):

    #Check symbols
    if reference_symbols is None or len(reference_symbols) == 0:
        raise ValueError("Reference symbols must contain at least one element symbol.")
    for symbol in reference_symbols:
        if symbol not in chemical_symbols[1:]:
            raise ValueError(f"Invalid chemical element symbol: '{symbol}'.")

    # Check that the cells between the images and the reference structure are equivalent
    check_cell_compatibility(atoms, reference_atoms)     

    #Check that every requested reference element exists in the reference structure.
    reference_counts = Counter(reference_atoms.get_chemical_symbols())
    #Check that the NEB structure contains the same number of reference atoms as the supplied reference structure.
    atoms_counts = Counter(atoms.get_chemical_symbols())

    for symbol in reference_symbols: #Provide data about the missing elements

        if reference_counts[symbol] == 0:
            raise ValueError(f"Reference structure does not contain the requested element '{symbol}'.")

        if atoms_counts[symbol] != reference_counts[symbol]:
            raise ValueError(
                f"Reference atom count mismatch for '{symbol}': reference contains {reference_counts[symbol]} atoms, but the NEB structure contains {atoms_counts[symbol]}.")