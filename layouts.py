#Plot atoms
import matplotlib.pyplot as plt #Plot adsorption surfaces
import numpy as np #Mathematical calculations

#Create the figure and axes according to the selected layout
def create_axes(layout, n_rot, n_structures):
    if layout == "horizontal": #Horizontal
        fig, axes = plt.subplots(n_rot, n_structures, figsize=(6*n_structures, 6*n_rot), squeeze=False)
        return fig, axes

    elif layout == "vertical": #Vertical
        fig, axes = plt.subplots(n_structures, n_rot, figsize=(6*n_rot, 6*n_structures), squeeze=False)
        return fig, axes

    else:
        raise ValueError(f"Unknown layout: {layout}")

#Iterate through all axes regardless of their container type
def iter_axes(axes): #generator function
    if isinstance(axes, dict): #Check for a dictionary
        for v in axes.values():
            if isinstance(v, list): #Convert to a list
                for ax in v:
                    yield ax #faster output
            else:
                yield v
    else:
        for ax in np.ravel(axes):
            yield ax #1D list