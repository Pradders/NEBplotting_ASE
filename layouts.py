#Plot atoms
import matplotlib.pyplot as plt #Plot adsorption surfaces
import numpy as np #Mathematical calculations

def create_axes(layout, n_rot):
    if layout == "horizontal": #Horizontal
        fig, axes = plt.subplots(n_rot, 2, figsize=(12, 6*n_rot), squeeze=False)
        return fig, axes

    elif layout == "vertical": #Vertical
        fig, axes = plt.subplots(2, n_rot, figsize=(6*n_rot, 10), squeeze=False)
        return fig, axes

    else:
        raise ValueError(f"Unknown layout: {layout}")

def iter_axes(axes): #generator function,  
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