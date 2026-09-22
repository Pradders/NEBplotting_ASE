# NEBplotting_ASE

A Python plotting and analysis tool leveraging [ASE](https://wiki.fysik.dtu.dk/ase/) to visualise atomic structures from Nudged Elastic Band (NEB) calculations.
Version 1.0.0 (v1.0.0)

# Overview
This code searches for NEB transition systems and generates figures showing selected structures along the reaction pathway.

The available display modes are:
1. **Initial / Final**
2. **Initial / Transition State / Final**
3. **Initial / All NEB images / Final**

The code can optionally display the relative energy of each NEB image. The atomic structures are read from `CONTCAR` files where available, with `POSCAR` used as a fallback. As adsorbates and surfaces can extend over the unit cell boundaries in the x and y directions, the code allows for the user to shift the structure to prevent this overlap.

## Folder and file access
A transition/reaction system should contain numbered NEB image folders as collected from e.g., VASP. The image directories must remain numbered so that the code can determine the order of the NEB pathway, e.g.,

```text
00
01
02
03
04
```

The lowest numbered image is the **initial structure, reactant, etc.** and the highest numbered image is the **final structure, product, etc.**.

Each numbered folder (i.e., image directory) must contain either CONTCAR or POSCAR, the former of which is preferred, as this tends to represent the relaxed structure.

## NEB energy data
An NEB energy file can be placed in the same directory as the numbered image folders. The program currently recognises **neb.dat** and **NEB.dat**. That is,

```text
00
01
02
03
04
neb.dat/NEB.dat
```

These filenames are defined in the relevant function in **`io_utils.py`**, specifically `find_transition()` through its `neb_filenames` argument/default. That is,

```python
def find_transition(base=os.getcwd(), neb_filenames=("neb.dat", "NEB.dat")):
```

If a different filename is required, it can be changed **in this function** rather than in `main.py`. For example:

```python
neb_filenames=("neb.dat", "NEB.dat", "my_energy_file.dat")
```

An original NEB energy profile might contain electronic energies, while a later analysis may incorporate corrections such as:
* zero-point energy (ZPE)
* entropy
* thermal contributions
* other free-energy corrections

If the corrected energies are written to a new file, the filename can be added to `neb_filenames` in `find_transition()`.

The important point is that **the plotting code does not need to be changed simply because the NEB energy filename changes**. The filename discovery is handled by `io_utils.py`.

The interpretation of the NEB data is:

* NEB image rows contain the energy associated with each image.
* The final entry is treated as the **reaction enthalpy** rather than another NEB image energy.
* The initial image is displayed with a relative energy of `0.00 eV`.
* The transition state is determined from the highest-energy NEB image when sufficient NEB energy information is available.

# Key inputs and validations

The program checks user inputs and repeats the relevant question when an invalid value is supplied.

These include:
* invalid mode numbers
* invalid yes/no responses
* invalid integer shifts
* invalid floating-point energies
* invalid transition-state image numbers
* transition-state images that do not exist
* insufficient NEB energy data

This prevents an invalid input from being silently accepted.

## Display modes
When the program starts, the user selects which structures should be displayed.
### Mode 1 — Initial / Final
Only the first and last NEB structures are displayed. If energy display is enabled, only the reaction enthalpy is required alongside the automatically defined initial energy of `0.00 eV`. A transition-state image or transition-state energy is **not required** for this mode.
### Mode 2 — Initial / Transition State / Final
The figure displays the first, last and main transition NEB structures. If a valid NEB energy file is available, the transition-state image and its energy are determined from the highest-energy NEB image and the enthalpy is determined from the final image, while if an NEB energy file is unavailable, the user is asked to manually specify these values.
### Mode 3 — Initial / All NEB images / Final
All NEB images are displayed. The program can display either **Key energies** (only initial, transition state, and enthalpic energies) or **All energies**. When all image energies are supplied, the transition-state image can be identified automatically as the highest-energy NEB image.

## Energy input
Energy information can be collected in two ways: **Automatic energy input** from neb.dat or **Manual energy input** from user input.

## Projection and structure shifting
The atomic structures can optionally be shifted before plotting. The shift is based on the largest covalent radius present in the structure. The user then supplies integer values for the x and y shifts. Negative integer values shift the structure left/down, while positive values shift it right/up. As such, the shift is calculated by:

```text
Shift = integer × maximum covalent diameter
```

## Shift modes
Three shifting modes are available: **Mode 1 — MANUAL shift for EACH image** (every individual NEB image is treated separately), **Mode 2 — SAME shift for ALL images in EACH SYSTEM** (same shift applied to each image in each system), and **Mode 4 — NO shift** (no shifting of atoms).

The shifting is visually previewed through a temporary image prior to confirmation.

## Shift preview and confirmation
Whenever a shift needs to be selected, the structure is previewed before the shift is confirmed. If the result is rejected, the shift can be entered again. Inputs are repeatedly requested until an appropriate value is supplied.

# Image features
## Colour coding
Atoms are colour-coded according to their chemical element. The code uses ASE/Jmol colours by default. Specific element colours can also be supplied manually; elements which are not user-defined retain the default colour. For example,

```python
element_colors = {
    "Ni": "lightgray",
    "C": "black",
}
```

## Views and periodicity
The default view is a top view:

```python
views = [('0x,0y,0z')]
```

Additional views can be configured if required.

The default periodic repetition is:

```python
repeat = (1, 1, 1)
```

This means that the original unit cell is displayed once. Larger values can be employed if desired.

## Figure layout
The structures can be arranged as either "horizontal" or "vertical".

## Plot styles
Plot fonts, sizes and other visual properties can be configured through the plotting/style settings.

# Image saving
The output directory to store the figures can be changed using:

```python
save_dir = "NEB_plots"
```

The transition path is converted into an image name using underscores. Before an image is generated, the transition/system name is printed to the terminal so that the user can identify which structure is currently being processed.

# Structure consistency
All NEB images belonging to the same transition system are checked for consistency. The program verifies that the structures contain the same number of atoms and the same element ordering. A mismatch can indicate that the structures are not directly comparable.

# Usage
The code is run from the **main.py** file. 

## External function files

The project is divided into separate function files.

### `io_utils.py`
Handles file and directory discovery.
### `atoms.py`
Loads atomic structures using ASE.
### `check.py`
Checks structural consistency between NEB images.
### `plotting.py`
Handles the creation and saving of the figures.
### `colors.py`
Controls atomic colours.
### `layouts.py`
Controls the arrangement of ASE views in the matplotlib figure.
### `geometry.py`
Handles structure geometry and shifting.
### `inputs.py`
Handles user interaction.

# Example
