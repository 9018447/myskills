---
title: "Documentation"
source: "https://www.scm.com/doc/COSMO-RS/Examples/pKa.html"
author:
published: 2023-05-23
created: 2026-04-10
description: "Software for Chemistry & Materials"
tags:
  - "clippings"
---
## Automated pKa calculation

[`Download relevant coskf file`](https://www.scm.com/doc/COSMO-RS/_downloads/2c68e8c46c049674fbaee02b88e45c10/coskf_pkas.zip)

## Python code

\[show/hide code\]

```python
import os, math
from scm.plams import Settings, init, finish, CRSJob, config
import matplotlib.pyplot as plt

init()
# suppress plams output
config.log.stdout = 0

class PkaSystem:
    def __init__(
        self,
        comp_protonated: Settings = None,
        comp_deprotonated: Settings = None,
        systype="acid",
    ):
        self.comp_protonated = comp_protonated
        self.comp_deprotonated = comp_deprotonated
        self.type = systype.lower()
        self.g_cp = []
        self.g_cd = []
        self.pka = {}
        self.error = self.check_type()

    def check_type(self):
        if not all(isinstance(x, Settings) for x in [self.comp_protonated, self.comp_deprotonated]):
            print("Incorrect input type for compounds in PkaSystem... must be a plams.Settings instance")
            return False
        return True

class PkaCalculator:
    def __init__(
        self,
        systems=None,
        solv_protonated=None,
        solv_deprotonated=None,
        temp_range=[298.15, 298.15],
        steps=0,
        use_correction=True,
    ):

        self.systems = systems
        self.solv_protonated = solv_protonated
        self.solv_deprotonated = solv_deprotonated
        self.temp_range = temp_range
        self.steps = steps
        self.use_correction = use_correction
        self.R_const = 0.001987  # kcal/(mol K)

        self.g_sp = []
        self.g_sd = []

        if self.steps == 0:
            self.temp_vals = [temp_range[0]]
        else:
            self.temp_vals = [
                self.temp_range[0] * (1 - t_idx / self.steps) + self.temp_range[1] * (t_idx / self.steps)
                for t_idx in range(self.steps + 1)
            ]

        self.calc_G_values()
        self.calc_pkas()

    def calc_G_values(self):

        for temp in self.temp_vals:
            settings = Settings()
            settings.input.property._h = "ACTIVITYCOEF"
            # optionally, change to the COSMOSAC2013 method
            # settings.input.method = 'COSMOSAC2013'
            settings.input.temperature = temp

            compounds = [Settings()] * (2 + 2 * len(systems))
            compounds[0] = self.solv_deprotonated
            compounds[0].frac1 = 1.0
            compounds[1] = self.solv_protonated

            for i, system in enumerate(systems):
                compounds[2 + 2 * i] = system.comp_deprotonated
                compounds[2 + 2 * i + 1] = system.comp_protonated

            settings.input.compound = compounds
            my_job = CRSJob(settings=settings)
            out = my_job.run()
            res = out.get_results()

            g_vals = res["G solute"]
            for i, system in enumerate(systems):
                system.g_cd.append(g_vals[2 + 2 * i])
                system.g_cp.append(g_vals[2 + 2 * i + 1])
            self.g_sd.append(g_vals[0])
            self.g_sp.append(g_vals[1])

    def calc_pkas(self):
        for i, temp in enumerate(self.temp_vals):
            temp_key = round(temp, 3)
            for system in self.systems:
                g_diss = system.g_cd[i] - system.g_cp[i] + self.g_sp[i] - self.g_sd[i]
                if self.use_correction:
                    pka = self.calc_corrected_pka(g_diss, system, temp)
                else:
                    pka = g_diss / (self.R_const * temp * math.log(10)) - 1.74
                system.pka[temp_key] = pka

    def calc_corrected_pka(self, g_diss, system, temp):
        if system.type == "acid":
            return 0.62 * g_diss / (self.R_const * temp * math.log(10)) + 2.1
        else:
            return 0.67 * g_diss / (self.R_const * temp * math.log(10)) - 2.0

if __name__ == "__main__":

    ##################  Note: Ensure to download the coskf_pkas before running the script  ##################
    database_path = os.path.abspath("./coskf_pkas")

    if not os.path.exists(database_path):
        raise OSError(f"The provided path does not exist. Exiting.")

    systems = []

    benzoic_acid = Settings({"_h": os.path.join(database_path, "Benzoic_acid.coskf")})
    benzoic_acid_deprotonated = Settings({"_h": os.path.join(database_path, "conjugate_base_Benzoic_acid.coskf")})
    systems.append(PkaSystem(comp_protonated=benzoic_acid, comp_deprotonated=benzoic_acid_deprotonated, systype="acid"))

    pyridine = Settings({"_h": os.path.join(database_path, "Pyridine.coskf")})
    pyridineH = Settings({"_h": os.path.join(database_path, "conjugate_acid_Pyridine.coskf")})
    systems.append(PkaSystem(comp_protonated=pyridineH, comp_deprotonated=pyridine, systype="base"))

    water = Settings({"_h": os.path.join(database_path, "Water.coskf")})
    h3o = Settings({"_h": os.path.join(database_path, "conjugate_acid_Water.coskf")})

    PkaCalculator(systems, solv_protonated=h3o, solv_deprotonated=water, temp_range=[298.15, 348.15], steps=5)

    for system in systems:
        print(system.pka)

finish()
```