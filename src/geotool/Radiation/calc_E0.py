# %%
import numpy as np

# %%
def calc_E0(doy):
    gamma = 2 * np.pi * (doy-1)/365
    E0 = 1.000110 + 0.034221 * np.cos(gamma) + 0.001280 * np.sin(gamma) + \
    0.000719*np.cos(2*gamma) + 0.000077*np.sin(2*gamma)
    return E0