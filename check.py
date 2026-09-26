#Used to confirm certain consistencies in data
from collections import Counter #Counting function
from ase.io import read #Use to collect, visualise atomic structures

#Check length consistency of all NEB structures
def check_consistency(item):

    #Collect the NEB structures
    neb_structures = item["neb_structures"]

    #Sort the image numbers
    image_numbers = sorted(neb_structures)

    #Use the first image as the reference structure
    reference_number = image_numbers[0]
    reference_atoms = read(neb_structures[reference_number])

    #Check every other NEB image against the reference
    for image_number in image_numbers[1:]:
        #Read the current structure
        atoms = read(neb_structures[image_number])
        #Check that the structures contain the same number of atoms
        if len(atoms) != len(reference_atoms):
            raise ValueError(f"Atom count mismatch in {item['transition']}: "
                             f"image {reference_number}={len(reference_atoms)}, "
                             f"image {image_number}={len(atoms)}")

        #Check element ordering consistency
        for i, (a_reference, a_current) in enumerate(zip(reference_atoms, atoms)):
            if a_reference.symbol != a_current.symbol:
                raise ValueError(f"Element mismatch at index {i} in "
                                 f"{item['transition']}: "
                                 f"image {reference_number}={a_reference.symbol}, "
                                 f"image {image_number}={a_current.symbol}" )

#Check that the reference structure contains the requested elements and that the number of reference atoms matches the NEB structure.
def check_reference_structure(atoms,reference_atoms,reference_symbols):

    #Check that reference symbols were provided.
    if not reference_symbols:
        raise ValueError("Reference_symbols must contain at least one element symbol.")

    #Check that every requested reference element exists in the reference structure.
    reference_counts = Counter(reference_atoms.get_chemical_symbols())

    for symbol in reference_symbols:

        if reference_counts[symbol] == 0:
            raise ValueError(
                f"Reference structure does not contain the requested element '{symbol}'."
            )

    #Check that the NEB structure contains the same number of reference atoms as the supplied reference structure.
    atoms_counts = Counter(atoms.get_chemical_symbols())

    for symbol in reference_symbols: #Provide data about the missing elements

        if atoms_counts[symbol] != reference_counts[symbol]:
            raise ValueError(
                f"Reference mismatch for '{symbol}': "
                f"reference contains {reference_counts[symbol]} atoms, "
                f"but the NEB structure contains {atoms_counts[symbol]}."
            )