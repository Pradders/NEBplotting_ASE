from ase.io import read #Use to collect, visualise atomic structures

#Check length consistency of initial and final structures
def check_consistency(item):

    #Atoms in each structure
    ini_atoms = read(item["ini_structure"])
    fin_atoms = read(item["fin_structure"])

    # Check that the initial and final systems contain the same number of atoms
    if len(ini_atoms) != len(fin_atoms):
        raise ValueError(
            f"Atom count mismatch in {item['transition']}: "
            f"ini={len(ini_atoms)}, fin={len(fin_atoms)}"
        )
    
    #Check element ordering consistency
    for i, (a_ini, a_fin) in enumerate(zip(ini_atoms, fin_atoms)):
        if a_ini.symbol != a_fin.symbol:
            raise ValueError(
                f"Element mismatch at index {i} in {item['transition']}: "
                f"{a_ini.symbol} (ini) != {a_fin.symbol} (fin)"
            )