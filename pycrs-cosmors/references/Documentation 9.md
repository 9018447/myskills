---
title: "Documentation"
source: "https://www.scm.com/doc/COSMO-RS/Examples/Sigma_moments.html"
author:
published: 2023-05-23
created: 2026-04-10
description: "Software for Chemistry & Materials"
tags:
  - "clippings"
---
## Sigma Moments

moment are useful chemical descriptors derived from the -profile. They are analogous to moments of a statistical distribution and can be thought of as a way to reduce the high-dimensional information present in a -profile to a smaller number of descriptors that characterize that -profile. -moments are known to be valuable descriptors in QSPR and are thought to represent the solvent space well.

moment can be calculated by the following equation through the -profile, , and the -profile, , of a compound. The zero-order moment is the molecular area of a compound. The first-order moment is the negative of total charge of a compound. The second-order sigma moment represents the polarity of a compound. The third-order moment represents the asymmetry of the -profile of a compound. The other moment, , and , do not have well-established physical interpretations. Last, the and quantify the strength of a molecule’s ability to form hydrogen-bond interactions as an acceptor and a donor, respectively. The different values of correspond to varying threshold values, , used in the equation.

where the unit are and for and respectively.

The following script will calculate the moment for few common compounds. By default, it computes five moment (, , , , ). To generate 15 moment, you can specify the `moment_power` and `hb_moment_level` parameters in the `calculate_moments` function, as demonstrated in the script.

## Python code

\[show/hide code\]

```python
import os
import numpy as np
from scm.plams import *
import matplotlib.pyplot as plt
from typing import List, Optional, Dict

class SigmaMoments:
    def __init__(self, filenames: List[str], database_path: str, hb_cutoff: float = 0.00854):
        """
        Initialize the SigmaMoments class and prepare the sigma profile for subsequent sigma moment calculations.

        Args:
            filenames : List[str]
                A list of \`.coskf\` files to be used for calculating sigma moments.
            database_path : str
                The directory path where the \`.coskf\` files are stored.
            hb_cutoff : float, optional
                The hydrogen bond cutoff value for the COSMO-RS model.
                Default is 0.00854 e/Å².
        """
        self.filenames = filenames
        self.database_path = os.path.abspath(database_path)
        self.hb_cutoff = hb_cutoff
        self._calc_profiles_and_chdens()

    def calculate_moments(
        self, moment_power: Optional[List[int]] = None, hb_moment_level: Optional[List[int]] = None
    ) -> dict:
        """
        Calculate the sigma moment.

        Args:
            moment_power : List[int], optional
                A list of integers specifying the powers for standard moment calculations.
                Default is [0, 2, 3]. The recommended maximum power is 6.

            hb_moment_level : List[int], optional
                A list of integers specifying the hydrogen bond moment levels to be calculated.
                For the 1st level, the \`hb_cutoff\` corresponds to the COSMO-RS parameter, defaulting to 0.00854 e/Å².
                For the 2nd, 3rd, and 4th levels, the \`hb_cutoff\` is defined as 0.006 + 0.002 * l e/Å², where l represents the level (2, 3, or 4).
        """
        if moment_power is None:
            moment_power = [0, 2, 3]
        if hb_moment_level is None:
            hb_moment_level = [2]

        self.moments = {}
        self._calc_standard_moments(moment_power)
        self._calc_hb_moments(hb_moment_level)
        return self.moments

    def __repr__(self):
        max_mom_len = max([len(m) for m in self.moments])
        lens = [len(fn) for fn in self.filenames]

        text = ""
        text += (" " * 5).join(["Moment".ljust(max_mom_len)] + self.filenames)
        text += "\n"
        for mom_name in self.moments:
            text += (" " * 5).join(
                [mom_name.ljust(max_mom_len)]
                + [("{0:.5g}".format(m)).rjust(l) for m, l in zip(self.moments[mom_name], lens)]
            )
            text += "\n"

        return f"{text}"

    def to_dataframe(self):
        """
        Convert the calculated result into pandas DataFrame.
        """
        try:
            import pandas as pd
        except ImportError:
            print(
                "Pandas is included by default in AMS2026 and later. On older AMS versions, install it through AMSpackages via the GUI or with:\namspackages install pandas"
            )
            return None

        df = pd.DataFrame(self.moments)
        df.insert(0, "filename", self.filenames)

        return df

    def _calc_profiles_and_chdens(self):
        # initialize settings object
        settings = Settings()
        settings.input.property._h = "PURESIGMAPROFILE"
        # set the cutoff value for h-bonding
        settings.input.CRSParameters.sigmahbond = self.hb_cutoff
        compounds = [Settings() for i in range(len(self.filenames))]
        for i, filename in enumerate(self.filenames):
            compounds[i]._h = os.path.join(self.database_path, filename)

        settings.input.compound = compounds
        # create a job that can be run by COSMO-RS
        my_job = CRSJob(settings=settings)
        # run the job
        out = my_job.run()
        # convert all the results into a python dict
        res = out.get_results()
        # retain profiles and charge density values
        self.tot_profiles = res["profil"]
        self.hb_profiles = res["hbprofil"]
        self.chdens = res["chdval"]

    def _calc_standard_moments(self, moment_power: Optional[List[int]] = None):
        if moment_power is None:
            moment_power = [0, 2, 3]
        for i in moment_power:
            tmp_moms = []
            for prof in self.tot_profiles:
                tmp_moms.append(np.sum(prof * np.power(self.chdens, i)))
            self.moments["MOM" + str(i)] = tmp_moms

    def _calc_hb_moments(self, hb_moment_level: Optional[List[int]] = None):
        if hb_moment_level is None:
            hb_moment_level = [2]

        for l in hb_moment_level:
            self.moments["MOM_hb_acc" + str(l)] = []
        for l in hb_moment_level:
            self.moments["MOM_hb_don" + str(l)] = []

        zeros = np.zeros(len(self.chdens))
        for prof in self.hb_profiles:
            for l in hb_moment_level:
                if l == 1:
                    hb_cutoff = self.hb_cutoff
                else:
                    hb_cutoff = 0.006 + 0.002 * l

                self.moments["MOM_hb_acc" + str(l)].append(np.sum(prof * np.maximum(zeros, self.chdens - hb_cutoff)))
                self.moments["MOM_hb_don" + str(l)].append(np.sum(prof * np.maximum(zeros, -self.chdens - hb_cutoff)))

    def plot_sigmaprofile(self, compound_idx: int, show: bool = True, save: bool = False, dir_path: str = "./"):
        """
        Plots the sigma profile for a specific compound.

        Args:
            compound_idx: int
                The index of the compound to visualize its sigma profile.
            show : bool, optional
                If True, displays the sigma profile plot. Default is True.
            save : bool, optional
                If True, saves the sigma profile plot to a file. Default is False.
            dir_path : str, optional
                The directory path where the sigma profile plot will be saved, if \`save\` is True. Default is the current working directory.
        """
        chdens = self.chdens
        tot_profiles = self.tot_profiles[compound_idx]
        hb_profiles = self.hb_profiles[compound_idx]
        name = self.filenames[compound_idx]

        fig = plt.figure(figsize=(5, 6))
        ax1 = fig.add_subplot(211)
        ax2 = fig.add_subplot(212)

        ax1.plot(chdens, tot_profiles, label="total", color="blue")
        ax1.set_xlabel("$\u03C3(e/\u212B^{{2}})$")
        ax1.set_ylabel("P(\u03C3) $(\u212B^{{2}})$")
        ax1.set_title("$\u03C3$ profile (total)")
        ax1.set_xlim([-0.025, 0.025])
        ax1.legend()

        ax2.plot(chdens, hb_profiles, label="hb", color="red")
        ax2.set_xlabel("charge density $(e/\u212B^{{2}})$")
        ax2.set_xlabel("$\u03C3(e/\u212B^{{2}})$")
        ax2.set_ylabel("P(\u03C3) $(\u212B^{{2}})$")
        ax2.set_title("$\u03C3$ profile (hydrogen bond)")
        ax2.set_xlim([-0.025, 0.025])

        ax2.legend()
        fig.suptitle(f"{name}")
        fig.tight_layout()

        if save:
            dir_path = os.path.abspath(dir_path)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            figname = f"SP_{name.replace('.coskf', '')}.png"
            fig.savefig(os.path.join(dir_path, figname))

        if show:
            plt.show()

##################  Note: Be sure to add the path to your own AMSCRS directory here  ##################
database_path = os.path.join(os.environ["SCM_PKG_ADFCRSDIR"], "ADFCRS-2018")
if not os.path.exists(database_path):
    raise OSError(f"The provided path does not exist. Exiting.")

init()
config.log.stdout = 0  # suppress plams output

# Define the files we want to use to calculate sigma moments
filenames = ["Water.coskf", "Hexane.coskf", "Ethanol.coskf", "Acetone.coskf", "Acetic_acid.coskf"]

# Initialize SigmaMoments with the specified filenames and database path
sm = SigmaMoments(filenames, database_path)

# Calculate sigma moments with default settings:
# - moment_power: [0, 2, 3]
# - hb_moment_level: [2]
sm.calculate_moments()
print(f"Default 5 sigma moments:\n{sm}")

# Calculate all 15 sigma moments by specifying:
# - moment_power: [0, 1, 2, 3, 4, 5, 6]
# - hb_moment_level: [1, 2, 3, 4]
sm.calculate_moments(moment_power=[0, 1, 2, 3, 4, 5, 6], hb_moment_level=[1, 2, 3, 4])
print(f"All 15 sigma moments:\n{sm}")

# Convert the sigma moments data to a DataFrame for analysis
# df = sm.to_dataframe()

# Visualize and save the sigma profile for the compound at index 0
# sm.plot_sigmaprofile(compound_idx=0, show=True, save=True, dir_path="./fig")

finish()
```

The output produced is the following

```
Default 5 sigma moments:
Moment          Water.coskf     Hexane.coskf     Ethanol.coskf     Acetone.coskf     Acetic_acid.coskf
MOM0                 43.011           160.38            90.019            103.28                94.302
MOM2              0.0062556         0.001061         0.0046302          0.004566             0.0062206
MOM3            -3.8253e-07       1.1557e-07        1.5947e-05         2.883e-05           -4.4743e-06
MOM_hb_acc2        0.056607                0          0.048228          0.044109              0.027105
MOM_hb_don2        0.056566                0          0.024696                 0              0.042326

All 15 sigma moments:
Moment          Water.coskf     Hexane.coskf     Ethanol.coskf     Acetone.coskf     Acetic_acid.coskf
MOM0                 43.011           160.38            90.019            103.28                94.302
MOM1             0.00026666         0.002145        0.00089555         0.0011418            0.00041249
MOM2              0.0062556         0.001061         0.0046302          0.004566             0.0062206
MOM3            -3.8253e-07       1.1557e-07        1.5947e-05         2.883e-05           -4.4743e-06
MOM4             1.2722e-06       1.3058e-08          8.23e-07        5.6827e-07            9.6505e-07
MOM5            -1.5315e-10       2.6449e-12        4.1365e-09        6.4726e-09           -4.6722e-09
MOM6             2.8941e-10        1.997e-13        1.8283e-10        9.9675e-11            2.1072e-10
MOM_hb_acc1        0.078179                0           0.06562          0.068401              0.055839
MOM_hb_acc2        0.056607                0          0.048228          0.044109              0.027105
MOM_hb_acc3         0.03146                0          0.027298          0.018472             0.0066449
MOM_hb_acc4        0.012196                0          0.011404         0.0056525            0.00031588
MOM_hb_don1        0.078272                0          0.034516                 0              0.053599
MOM_hb_don2        0.056566                0          0.024696                 0              0.042326
MOM_hb_don3        0.031173                0           0.01304                 0              0.028124
MOM_hb_don4         0.01279                0         0.0045683                 0              0.015962
```