---
title: "Documentation"
source: "https://www.scm.com/doc/COSMO-RS/Examples/BinodalSpinodal.html"
author:
published: 2023-05-23
created: 2026-04-10
description: "Software for Chemistry & Materials"
tags:
  - "clippings"
---
## Binodal and Spinodal Curves

Binodal and spinodal curves are useful for understanding phase stability. The binodal curve (or coexistence curve) defines the temperatures and compositions at which phase separation is thermodynamically favorable. The spinodal curve is located within the binodal curve and indicates the limit of local phase stability. Compositions between the spinodal and binodal curves – while not thermodynamically stable – are robust against small fluctuations (i.e., the free energy surface is locally convex for points in this region).

## Python code (Binary mixture)

\[show/hide code\]

```python
import os
import numpy as np
import matplotlib.pyplot as plt
from scm.plams import Settings, init, finish, CRSJob, config

########  Note: Ensure to configure the database path to either the installed ADFCRS-2018 directory or your own specified directory  ########

database_path = os.path.join(os.environ["SCM_PKG_ADFCRSDIR"], "ADFCRS-2018")
if not os.path.exists(database_path):
    raise OSError(f"The provided path does not exist. Exiting.")

init()
# suppress plams output
config.log.stdout = 0

files = ["Nitrobenzene.coskf", "Hexane.coskf"]
nring = [6, 0]
# problem paramters
temp_range = [203.15, 243.15]  # K -- the temperature range over which the curves are calculated
steps = 40  # number of steps to take within the temperature range

def binmix_at_T(files, temp):

    # initialize settings object
    settings = Settings()
    settings.input.property._h = "BINMIXCOEF"

    settings.input.property.nfrac = 100

    # make compounds
    compounds = [Settings() for i in range(len(files))]
    for i, (file, nr) in enumerate(zip(files, nring)):
        compounds[i]._h = os.path.join(database_path, file)
        compounds[i].nring = nr

    settings.input.temperature = temp

    # optionally, change to the COSMOSAC2013 method
    settings.input.method = "COSMOSAC2013"
    # we'll also tighten the convergence threshold for better numerical accuracy
    settings.input.Technical.sacconv = 1e-10

    # add the compounds to the settings object
    settings.input.compound = compounds
    # create a job that can be run by COSMO-RS
    my_job = CRSJob(settings=settings)
    # run the job
    out = my_job.run()
    # convert all the results into a python dict
    res = out.get_results()

    return res

def calc_binodal_at_T(res):

    # this is the miscibility gap, so we can use the result calculated by the program
    if res["showmiscgap"]:
        return res["xlle"][:2]
    else:
        return None

def calc_spinodal_at_T(res):

    # here, we'll look for points with d^2(G_mix)/dx^2 = 0
    # we'll calculate a numerical second derivative for every point
    spinodal = []
    gmix = res["Gibbs energy of mixing"]
    frac1 = res["molar fraction"][0]
    second_deriv = np.zeros(len(gmix))

    # initial values for endpoints (assuming convexity close to pure compounds)
    second_deriv[0] = 0.0001
    second_deriv[-1] = 0.0001

    for i in range(1, len(gmix) - 1):
        delta1 = frac1[i] - frac1[i - 1]
        delta2 = frac1[i + 1] - frac1[i]
        d1 = (gmix[i] - gmix[i - 1]) / delta1
        d2 = (gmix[i + 1] - gmix[i]) / delta2
        second_deriv[i] = 2 * (d2 - d1) / (delta1 + delta2)

    for i in range(len(second_deriv) - 1):
        if second_deriv[i] * second_deriv[i + 1] < 0:
            dist1 = abs(second_deriv[i])
            dist2 = abs(second_deriv[i + 1])
            tot = dist1 + dist2
            zero = (dist2 * frac1[i] + dist1 * frac1[i + 1]) / tot
            spinodal.append(zero)

    return spinodal if spinodal else None

temps = [temp_range[0] + (temp_range[1] - temp_range[0]) / steps * i for i in range(steps + 1)]
bin_left_points = []
bin_right_points = []
spin_left_points = []
spin_right_points = []
print("Temperature".ljust(15), "Binodal points".ljust(25), "Spinodal points")
for temp in temps:
    res = binmix_at_T(files, temp)
    binodal = calc_binodal_at_T(res)
    spinodal = calc_spinodal_at_T(res)

    bin_str = "(" + ",".join(["{0:<10.5g}".format(x) for x in binodal]) + ")" if binodal is not None else "--"
    spin_str = "(" + ",".join(["{0:<10.5g}".format(x) for x in spinodal]) + ")" if spinodal is not None else "--"
    print("{0:.5g}".format(temp).ljust(15), bin_str.ljust(25), spin_str)

    if binodal is not None:
        bin_left_points.append((binodal[0], temp))
        bin_right_points.append((binodal[1], temp))
    if spinodal is not None:
        spin_left_points.append((spinodal[0], temp))
        spin_right_points.append((spinodal[-1], temp))

bin_points = bin_left_points + list(reversed(bin_right_points))
spin_points = spin_left_points + list(reversed(spin_right_points))

plt.plot([x[0] for x in bin_points], [y[1] for y in bin_points], label="Binodal curve")
plt.plot([x[0] for x in spin_points], [y[1] for y in spin_points], label="Spinodal curve")
plt.xlabel("Mole fraction compound 1")
plt.ylabel("Temperature (K)")
plt.legend(loc="upper right")
plt.grid()
# plt.savefig('./Binodalspinodal_binary.png',dpi=300)
plt.show()

finish()
```

This code produces the following output:

## Python code (Ternary mixture)

> [!note] Note
> This example uses the python package `ternary`, but this is *only required for plotting*. This external python package can be installed from the internet in amspython using pip as follows: `amspython -m pip install python-ternary`. Users may choose to remove the plotting features of the code and not install `ternary`.

\[show/hide code\]

```python
import os
import numpy as np
import matplotlib.pyplot as plt
from scm.plams import *

try:
    import ternary
except ImportError:
    print("Cannot find ternary package.")
    print("Try to install with:")
    print("amspython -m pip install python-ternary")
    exit()

########  Note: Ensure to configure the database path to either the installed ADFCRS-2018 directory or your own specified directory  ########

database_path = os.path.join(os.environ["SCM_PKG_ADFCRSDIR"], "ADFCRS-2018")
if not os.path.exists(database_path):
    raise OSError(f"The provided path does not exist. Exiting.")

init()
# suppress plams output
config.log.stdout = 0

files = ["Water.coskf", "Chloroform.coskf", "Acetic_acid.coskf"]
nring = [0, 0, 0]
nfrac = 50  # the nfrac parameter for ternary mixtures
temp_range = [273.15, 273.15]  # K -- the temperature range over which the curves are calculated
steps = 0  # number of steps to take within the temperature range

def ternmix_at_T(files, temp, nfrac=20):

    # initialize settings object
    settings = Settings()
    settings.input.property._h = "TERNARYMIX"
    settings.input.property.nfrac = nfrac

    # make compounds
    compounds = [Settings() for i in range(len(files))]
    for i, (file, nr) in enumerate(zip(files, nring)):
        compounds[i]._h = os.path.join(database_path, file)
        compounds[i].nring = nr

    settings.input.temperature = temp

    # optionally, change to the COSMOSAC2013 method
    settings.input.method = "COSMOSAC2013"
    # we'll also tighten the convergence threshold for better numerical accuracy
    settings.input.Technical.sacconv = 1e-10
    settings.input.Technical.rsconv = 1e-10

    # add the compounds to the settings object
    settings.input.compound = compounds
    # create a job that can be run by COSMO-RS
    my_job = CRSJob(settings=settings)
    # run the job
    out = my_job.run()
    # convert all the results into a python dict
    res = out.get_results()

    return res

def calc_binodal_at_T(res):

    # this is the miscibility gap, so we can use the result calculated by the program
    points_l = []
    points_r = []

    if res["nxll"] > 0:
        for i in range(len(res["xll"]) // 6):
            points_l.append(res["xll"][6 * i : 6 * i + 3])
            points_r.append(res["xll"][6 * i + 3 : 6 * i + 6])
        return points_l + list(reversed(points_r))
    else:
        return None

def calc_spinodal_at_T(res):

    # in this function, we search for mole fraction values where the determinant of the hessian of G_mix with respect to mole fractions is 0
    # using the first two mole fractions as degrees of freedom
    spinodal = []
    gmix_res = res["Gibbs energy of mixing"]
    fracs = res["molar fraction"][:2]

    step_size = abs(fracs[0][1] - fracs[0][0])
    tot_steps = round(1.0 / step_size) + 1
    gmix = np.empty((tot_steps, tot_steps))
    gmix.fill(None)
    det_mat = np.empty((tot_steps, tot_steps))
    det_mat.fill(None)

    for x1, x2, gmix_val in zip(fracs[0], fracs[1], gmix_res):
        idx1 = int(round(x1 / step_size, 0))
        idx2 = int(round(x2 / step_size, 0))
        gmix[idx1, idx2] = gmix_val

    # calculate second derivatives and determinants
    for i in range(tot_steps):
        for j in range(tot_steps - i):
            # these finite difference expressions work because the ternary mixture always has a constant step size
            if 0 < i < tot_steps - 1 and 0 < j < tot_steps - 1:
                d_xx = (gmix[i + 1, j] - 2 * gmix[i, j] + gmix[i - 1, j]) / (step_size**2)
                d_yy = (gmix[i, j + 1] - 2 * gmix[i, j] + gmix[i, j - 1]) / (step_size**2)
                d_xy = (gmix[i + 1, j + 1] - gmix[i + 1, j - 1] - gmix[i - 1, j + 1] + gmix[i - 1, j - 1]) / (
                    4 * step_size**2
                )
                det_mat[i, j] = d_xx * d_yy - d_xy**2

    for i in range(tot_steps):
        for j in range(tot_steps - i):
            # compare right and below
            for (i1, j1), (i2, j2) in [[(i, j), (i + 1, j)], [(i, j), (i, j + 1)]]:
                if (
                    i2 < tot_steps
                    and j2 < tot_steps
                    and not np.isnan(det_mat[i1, j1])
                    and not np.isnan(det_mat[i2, j2])
                    and det_mat[i1, j1] * det_mat[i2, j2] < 0
                ):

                    x1 = step_size * np.array([i1, j1, tot_steps - 1 - i1 - j1])
                    x2 = step_size * np.array([i2, j2, tot_steps - 1 - i2 - j2])

                    spin = (abs(det_mat[i2, j2]) * x1 + abs(det_mat[i1, j1]) * x2) / (
                        abs(det_mat[i1, j1]) + abs(det_mat[i2, j2])
                    )
                    spinodal.append(spin)

    return spinodal

## Make ternary figure
figure, tax = ternary.figure(scale=1.0)
tax.boundary(linewidth=2.0)
tax.gridlines(color="black", multiple=0.05)
# Set Axis labels and Title
fontsize = 10
tax.bottom_axis_label("$x_1$", fontsize=fontsize, offset=0.2)
tax.right_axis_label("$x_2$", fontsize=fontsize, offset=0.2)
tax.left_axis_label("$x_3$", fontsize=fontsize, offset=0.2)

tax.ticks(axis="lbr", multiple=0.1, linewidth=1, tick_formats="%.1f", offset=0.02, fontsize=fontsize)

# Remove default Matplotlib Axes
tax.clear_matplotlib_ticks()

temps = []
if steps > 0:
    temps = [temp_range[0] + (temp_range[1] - temp_range[0]) / steps * i for i in range(steps + 1)]
else:
    temps = [temp_range[0]] if isinstance(temps, list) else [temp_range]

for temp in temps:
    res = ternmix_at_T(files, temp, nfrac)
    binodal = calc_binodal_at_T(res)
    spinodal = calc_spinodal_at_T(res)

    # the sorting index might need to be changed here if the curves are in a different position
    binodal.sort(key=lambda x: x[1])
    spinodal.sort(key=lambda x: x[1])

    tax.plot(binodal, label="Binodal  T=" + str(temp) + " K")
    tax.plot(spinodal, label="Spinodal T=" + str(temp) + " K")

tax.get_axes().axis("off")
ternary.plt.legend(bbox_to_anchor=(1.1, 1.0), loc="right")
ternary.plt.show()

finish()
```

This code produces the following output: