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

