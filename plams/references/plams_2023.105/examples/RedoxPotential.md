[Free trial](https://www.scm.com/free-trial/)

[ ![Software for Chemistry & Materials](https://www.scm.com/wp-content/themes/scm/images/logos/scm-logo-compact.svg) ![Software for Chemistry & Materials](https://www.scm.com/wp-content/themes/scm/images/logos/scm-logo.svg) ](https://www.scm.com)

  * [Applications](https://www.scm.com/applications/ "Applications")
  * [Products](https://www.scm.com/amsterdam-modeling-suite/ "Products")
  * [Support](https://www.scm.com/support/ "Support")
  * [About us](https://www.scm.com/about-us/ "About us")

[](https://www.scm.com/search.php)Search

[![Logo](../_static/plams_logo.png) ](../index.html)

  * 

Table of contents

  * [General](../general.html)
  * [Introduction](../intro.html)
  * [Getting started](../started.html)
  * [Components overview](../components/components.html)
  * [Interfaces](../interfaces/interfaces.html)
  * [Examples](examples.html)
    * [Getting Started](examples.html#getting-started)
    * [Molecule analysis](examples.html#molecule-analysis)
    * [Benchmarks](examples.html#benchmarks)
    * [Workflows](examples.html#workflows)
      * Reduction and oxidation potentials
        * Definitions and introduction
        * Redox potential results
        * Code example
        * The PLAMS recipes/classes
        * Details about individual calculations
      * [Workflow: filtering molecules based on excitation energies](ExcitationsWorkflow.html)
      * [AMS transition state workflow](AMSTSWorkflow/AMSTSWorkflow.html)
      * [Charge transfer integrals with ADF](ChargeTransferIntegralsADF.html)
      * [Tuning the range separation](gammascan.html)
      * [Conformers Generation](ConformersGeneration/ConformersGeneration.html)
    * [COSMO-RS and property prediction](examples.html#cosmo-rs-and-property-prediction)
    * [Packmol and AMS-ASE interfaces](examples.html#packmol-and-ams-ase-interfaces)
    * [ParAMS and pyZacros](examples.html#params-and-pyzacros)
    * [Other AMS calculations](examples.html#other-ams-calculations)
    * [Pymatgen](examples.html#pymatgen)
    * [Pre-made recipes](examples.html#pre-made-recipes)
  * [Cookbook](../cookbook/cookbook.html)
  * [Citations](../citations.html)

  * [FAQ](../FAQ.html)

__[PLAMS](../index.html)

  * [Documentation](../PLAMS.html/../../Documentation/index.html)/
  * [PLAMS](../index.html)/
  * [Examples](examples.html)/
  * Reduction and oxidation potentials

# Reduction and oxidation potentials¶

**Note** : This example requires AMS2023 or later.

## Definitions and introduction¶

**Reduction potential** : A + e– → A– ; ΔG⁰ = –nFE⁰

**Oxidation potential** : A → A+ \+ e– ; ΔG⁰ = nFE⁰

There are three PLAMS recipes for calculating one-electron reduction or oxidation potentials in implicit solvent:

  * `AMSRedoxDirectJob`: The best method. Geometry optimizations (and optionally frequencies) are calculated for both neutral and reduced/oxidized species in implicit solvent. The solvent must be supported by ADF. Requires an ADF license.

  * `AMSRedoxThermodynamicCycleJob`: Only useful if you include the vibrations (frequencies) and the molecule is large (in which case it is faster but less accurate than AMSRedoxDirectJob). The frequencies are only calculated for the gasphase molecule. A thermodynamic cycle gives the reduction or oxidation potential. The solvent must be supported by ADF. Requires an ADF license.

  * `AMSRedoxScreeningJob`: The fastest (and least accurate) method. Geometry optimizations are performed at the GFN1-xTB level of theory. The solvation free energy is evaluated by COSMO-RS. Vibrational effects are always implicitly accounted for. A `.coskf` file for the solvent is required - this can either be obtained from the ADFCRS-2018 database or generated with an `ADFCOSMORSCompoundJob`. Requires DFTB, ADF, and COSMO-RS licenses.

The `AMSRedoxScreeningJob` workflow was developed by [Belic et al., Phys. Chem. Chem. Phys. 24, 197–210 (2022)](https://pubs.rsc.org/en/content/articlehtml/2021/cp/d1cp04218a) for calculating oxidation potentials. The paper also describes the other workflows in detail.

Note

The `AMSRedoxScreeningJob` uses the recommended ADF settings for generating .coskf files. Belic et al. used a different density functional. Using the class will give slightly different results compared to Belic et al.

The **free energy of the electron** is set to be –0.0375 eV (see Belic et al.).

In this example the above three workflows are used to evaluate the **reduction potential of benzoquinone in water**. The experimental value is E⁰ = +0.10 V relative to SHE (**standard hydrogen electrode**).

[Ho et al.](https://doi.org/10.1201/b19122) ([preprint pdf](https://comp.chem.umn.edu/truhlar/docs/C86preprint.pdf)) evaluated E⁰ = -0.40 V or -0.28 V for benzoquinone relative to SHE using different computational methods.

The reduction and oxidation potentials calculated by the PLAMS classes are given on an **absolute scale**. On this scale, the SHE is at +4.42 or +4.28 V (see Ho et al.). To get potentials relative to SHE, we therefore subtract 4.42 V from the calculated values.

Note

Energy differences in eV correspond directly to potentials in V.

Tip

If you compare many calculated reduction potentials, use one of them as the reference state. See for example [Huyhn et al., J. Am. Chem. Soc. 2016, 138, 49, 15903–15910](https://doi.org/10.1021/jacs.6b05797) in the case of substituted quinones.

Technical

These classes can only be used for

  * molecules that do not undergo big conformational changes (or dissociation) upon oxidation/reduction.

  * one-electron reduction/oxidation. For multiple electrons, run the same script with different initial charges for the molecule

  * molecules with 0 or 1 unpaired electrons

## Redox potential results¶

**Results** : The below script outputs the following table:
[code] 
    The experimental reduction potential of benzoquinone is +0.10 V vs. SHE
    Jobname                  Eox(vib,rel-to-SHE)[V]   Ered(vib,rel-to-SHE)[V]  Eox(rel-to-SHE)[V]       Ered(rel-to-SHE)[V]
    quick_screening          2.95                     0.44                     2.95                     0.44
    direct_best_method       2.62                     -0.08                    2.72                     -0.09
    thermodynamic_cycle      2.64                     -0.07                    2.71                     -0.10
    
[/code]

The first two columns give the oxidation and reduction potentials incorporating vibrational effects in the calculation. The last two columns ignore the vibrational effects. Here, we are only interested in the two **Ered** columns (reduction potentials). We see:

  * Compared to the experimental E⁰ = +0.10 V, the screening method gives a higher value (+0.44 V) and the more accurate methods a lower value (-0.08 V or -0.07 V).

  * For this molecule, vibrational effects on the reduction potential are very small (e.g. the vibrations cause E⁰ to go from -0.09 V to -0.08 V for the direct method). Because calculating the vibrations is computationally expensive, they could have been turned off by setting `vibrations = False` in the below script.

  * The oxidation potentials (Eox) are given for demonstration purposes only. Turn them off by setting `oxidation = False` in the below script.

## Code example¶

**Download** [`ReductionOxidationPotentials.py`](../_downloads/f278b63045419893bbffdac2a9808c8a/ReductionOxidationPotentials.py)
[code] 
    #!/usr/bin/env amspython
    from scm.plams import *
    
    def main():
        mol = from_smiles('C1=CC(=O)C=CC1=O', forcefield='uff')  # benzoquinone
        solvent_name = 'Water'   # Solvent for AMSRedoxDirectJob and AMSRedoxThermodynamicCycleJob. See the ADF Solvation documentation for which solvents are available.
        solvent_coskf = CRSJob.database() + '/Water.coskf' # .coskf file or AMSRedoxScreeningJob
    
        vibrations = True   # set to False to turn off vibrations for AMSRedoxDirectJob and AMSRedoxThermodynamicCycleJob
        reduction = True
        oxidation = True    # not really relevant for benzoquinone, set to False to not calculate
    
        # DFT settings for AMSRedoxDirectJob and AMSRedoxThermodynamicCycleJob
        # Note: These are for demonstration purposes only. Use a better functional/settings for production purposes.
        s = Settings()
        s.input.adf.basis.type = 'DZP'
        s.input.adf.xc.gga = 'PBE'
        s.input.ams.GeometryOptimization.Convergence.Quality = 'Basic'
    
        jobs = [
            AMSRedoxScreeningJob(name='quick_screening', molecule=mol, reduction=reduction, oxidation=oxidation, solvent_coskf=solvent_coskf),
            AMSRedoxDirectJob(name='direct_best_method', molecule=mol, settings=s, reduction=reduction, oxidation=oxidation, vibrations=vibrations, solvent=solvent_name),
            AMSRedoxThermodynamicCycleJob(name='thermodynamic_cycle', molecule=mol, settings=s, reduction=reduction, oxidation=oxidation, vibrations=vibrations, solvent=solvent_name),
        ]
    
        for job in jobs:
            job.run()
            print_results([job])
    
        print("Final summary:")
        print_results(jobs)
    
    def print_results(jobs):
        SHE = 4.42 # standard hydrogen electrode in eV on absolute scale
    
        print("The experimental reduction potential of benzoquinone is +0.10 V vs. SHE")
        print("{:24s} {:24s} {:24s} {:24s} {:24s}".format("Jobname", "Eox(vib,rel-to-SHE)[V]", "Ered(vib,rel-to-SHE)[V]", "Eox(rel-to-SHE)[V]", "Ered(rel-to-SHE)[V]"))
    
        for job in jobs:
            s = f'{job.name:24s}'
            for vibrations in [True, False]:
                try:
                    Eox = job.results.get_oxidation_potential(vibrations=vibrations) - SHE
                    Eox = f'{Eox:.2f}'
                except:
                    Eox = 'N/A'
                s += f' {Eox:24s}'
    
                try:
                    Ered = job.results.get_reduction_potential(vibrations=vibrations) - SHE
                    Ered = f'{Ered:.2f}'
                except:
                    Ered = 'N/A'
                s += f' {Ered:24s}'
    
            print(s)
    
    if __name__ == '__main__':
        init()
        main()
        finish()
    
[/code]

## The PLAMS recipes/classes¶

This section contains some details about the implementation.

The oxidation and reduction potentials are calculated as follows:
[code] 
    class AMSRedoxDirectResults(AMSRedoxParentResults):
        def get_oxidation_potential(self, vibrations=True, unit='eV'):
            Greact = self._get_energy(self.job.children['job_0'], vibrations=vibrations)
            Gprod = self._get_energy(self.job.children['job_ox'], vibrations=vibrations) + self.Gelectron 
            ret = (Gprod - Greact) * Units.convert(1.0, 'hartree', unit)
            return ret 
    
        def get_reduction_potential(self, vibrations=True, unit='eV'):
            Greact = self._get_energy(self.job.children['job_0'], vibrations=vibrations) + self.Gelectron 
            Gprod = self._get_energy(self.job.children['job_red'], vibrations=vibrations) 
            ret = (Gprod - Greact) * Units.convert(1.0, 'hartree', unit)
            ret *= -1 # deltaG = -nFE
            return ret 
    
[/code]
[code] 
    class AMSRedoxThermodynamicCycleResults(AMSRedoxParentResults):
        def get_oxidation_potential(self, vibrations=True, unit='eV'):
            Greact  = self._get_energy(self.job.children['go_0_vacuum'], vibrations=vibrations) \
                    + self._get_energy(self.job.children['go_0_vacuum_sp_solvated'], vibrations=False) \
                    + self._get_energy(self.job.children['go_0_solvated_sp_vacuum'], vibrations=False) \
                    - 2*self._get_energy(self.job.children['go_0_vacuum'], vibrations=False) 
    
            Gprod   = self._get_energy(self.job.children['go_ox_vacuum'], vibrations=vibrations) \
                    + self._get_energy(self.job.children['go_ox_vacuum_sp_solvated'], vibrations=False) \
                    + self._get_energy(self.job.children['go_ox_solvated_sp_vacuum'], vibrations=False) \
                    - 2*self._get_energy(self.job.children['go_ox_vacuum'], vibrations=False) \
                    + self.Gelectron
    
            ret = (Gprod - Greact) * Units.convert(1.0, 'hartree', unit)
            return ret 
    
        def get_reduction_potential(self, vibrations=True, unit='eV'):
            Greact  = self._get_energy(self.job.children['go_0_vacuum'], vibrations=vibrations) \
                    + self._get_energy(self.job.children['go_0_vacuum_sp_solvated'], vibrations=False) \
                    + self._get_energy(self.job.children['go_0_solvated_sp_vacuum'], vibrations=False) \
                    - 2*self._get_energy(self.job.children['go_0_vacuum'], vibrations=False)  \
                    + self.Gelectron
    
            Gprod   = self._get_energy(self.job.children['go_red_vacuum'], vibrations=vibrations) \
                    + self._get_energy(self.job.children['go_red_vacuum_sp_solvated'], vibrations=False) \
                    + self._get_energy(self.job.children['go_red_solvated_sp_vacuum'], vibrations=False) \
                    - 2*self._get_energy(self.job.children['go_red_vacuum'], vibrations=False) 
    
            ret = (Gprod - Greact) * Units.convert(1.0, 'hartree', unit)
            ret *= -1 # deltaG = -nFE
            return ret 
    
[/code]

where

  * `go_0_vacuum` is a **g** eometry **o** ptimization for the neutral (**0**) molecule in vacuum,

  * `go_0_vaccum_sp_solvated` is a **s** ingle **p** oint in implicit solvent on the previous structure,

  * etc.

[code] 
    class AMSRedoxScreeningResults(Results):
        Gelectron =  -0.0375 / 27.211  # in hartree
    
        def get_oxidation_potential(self, vibrations=True, unit='eV'):
            """ Note: vibrations cannot be disabled for AMSRedoxScreening """
            Greact = self.job.children['activitycoef_0'].results.get_gibbs_energy()
            Gprod = self.job.children['activitycoef_ox'].results.get_gibbs_energy() + self.Gelectron 
            ret = (Gprod - Greact) * Units.convert(1.0, 'hartree', unit)
            return ret 
    
        def get_reduction_potential(self, vibrations=True, unit='eV'):
            """ Note: vibrations cannot be disabled for AMSRedoxScreening """
            Greact = self.job.children['activitycoef_0'].results.get_gibbs_energy() + self.Gelectron
            Gprod = self.job.children['activitycoef_red'].results.get_gibbs_energy() 
            ret = (Gprod - Greact) * Units.convert(1.0, 'hartree', unit)
            ret *= -1 # deltaG = -nFE
            return ret 
    
[/code]

The complete class definitions:
[code] 
    import os
    import shutil
    from ..core.functions import add_to_instance
    from ..core.basejob import MultiJob
    from ..core.results import Results
    from ..core.settings import Settings
    from ..mol.molecule import Molecule
    from ..interfaces.adfsuite.ams import AMSJob, AMSResults
    from ..interfaces.adfsuite.crs import CRSJob, CRSResults
    from ..tools.units import Units
    from .adfcosmorscompound import ADFCOSMORSCompoundJob
    from typing import Union, List
    from collections import OrderedDict
    
    """
        Classes for calculating oxidation potentials and reduction potentials in implicit solvent.
    
        To get the results, call
    
        job.results.get_oxidation_potential(vibrations=False)
    
        or
    
        job.results.get_reduction_potential(vibrations=False)
    
        Set ``vibrations=True`` to include vibrational effects if the job was run
        with ``vibrations=True``.
    
        The potential is returned in V. It is on an absolute scale. To get
        potential relative to SHE, subtract 4.47 V.
    
        AMSRedoxDirectJob
        --------------------
    
        Calculates reaction energies for 
        A + e^- --> A^-     if ``reduction=True``,
        and/or
        A --> A^+ + e^-     if ``oxidation=True``.
    
        using direct geometry optimizations in implicit solvent. The solvent must be one supported by ADF.
    
        If ``vibrations`` = True, then calculate and use Gibbs free energies at room temperature.
    
        ``settings`` should be set to the engine settings, excluding spin polarization and implicit solvation.
    
        Requires an ADF license.
    
        AMSRedoxThermodynamicCycleJob
        -----------------------------
    
        Sometimes more efficient (and less accurate) alternative to AMSRedoxDirectJob. Can be
        useful if the molecule is large and if ``vibrations=True``. For small molecules just use AMSRedoxDirectJob.
    
        Requires an ADF license.
    
        AMSRedoxScreeningJob
        -----------------------
    
        The fastest and least accurate option. Geometries are optimized at the DFTB
        level, ADF is then used to generate a .coskf file and the solvation free
        energies are evaluated with COSMO-RS.
    
        Note: you must supply ``solvent_coskf``, a path to the solvent .coskf file.
        If you do not have one, you can generate one with the
        ``ADFCOSMORSCompoundJob`` recipe.
    
        Requires DFTB, ADF, and COSMO-RS licenses.
    
        Note: The functional used is different from Belic et al. This class uses the
        settings that are meant to be used for generating .coskf files.
    
    """
    
    __all__ = [
        'AMSRedoxScreeningJob', 'AMSRedoxScreeningResults',
        'AMSRedoxDirectJob', 'AMSRedoxDirectResults',
        'AMSRedoxThermodynamicCycleJob', 'AMSRedoxThermodynamicCycleResults'
    ]
    
    def _spinpol_settings(molecule, charge=0):
        sett = Settings()
        num_electrons = sum(atom.atnum for atom in molecule) - charge
        spinpol = num_electrons % 2
        if spinpol == 0: 
            unrestricted = 'No'
        else:            
            unrestricted = 'Yes'
        sett.input.adf.SpinPolarization = spinpol
        sett.input.adf.Unrestricted = unrestricted
        return sett
    
    class AMSRedoxParentJob(MultiJob):
        def __init__(self, 
                     molecule:Molecule, # Molecule
                     name:str=None, 
                     settings:Settings=None,
                     oxidation:bool=True, 
                     reduction:bool=False):
    
            MultiJob.__init__(self, children=OrderedDict(), name=name)
    
            self.oxidation = oxidation
            self.reduction = reduction
            self.input_molecule = molecule
            self.settings = settings or Settings()
            self.orig_charge = molecule.properties.get('charge', 0) 
            self.ox_charge = self.orig_charge + 1
            self.red_charge = self.orig_charge - 1
    
        @staticmethod
        def solvation_settings(solvent):
            sett = Settings()
            if solvent is None:
                solvent = 'vacuum'
            if isinstance(solvent, str):
                sett.input.adf.Solvation.Solv = f"name={solvent}"
            elif isinstance(solvent, tuple):
                sett.input.adf.Solvation.Solv = f"eps={solvent[0]} rad={solvent[1]}"
            else:
                raise TypeError(f"solvent is of type {type(solvent)}, expected str or 2-tuple")
                
            return sett
    
        def get_dft_0_settings(self, vibrations=False, perturbcoordinates=False):
            """ all settings except task and solvation """
            s = Settings()
            s += self.settings
            s.update( _spinpol_settings(self.input_molecule, self.orig_charge) )
            s.input.ams.System.Charge = self.orig_charge
            s.input.ams.System.PerturbCoordinates = 0.01 if perturbcoordinates else 0.00
            s.input.ams.Properties.NormalModes = str(vibrations)
            return s
    
        def get_dft_ox_settings(self, vibrations=False, perturbcoordinates=False):
            sox = self.get_dft_0_settings(vibrations=vibrations, perturbcoordinates=perturbcoordinates)
            sox.update(_spinpol_settings(self.input_molecule, self.ox_charge))
            sox.input.ams.System.Charge = self.ox_charge
            return sox
    
        def get_dft_red_settings(self, vibrations=False, perturbcoordinates=False):
            sred = self.get_dft_0_settings(vibrations=vibrations, perturbcoordinates=perturbcoordinates)
            sred.update(_spinpol_settings(self.input_molecule, self.red_charge))
            sred.input.ams.System.Charge = self.red_charge
            return sred
            
    class AMSRedoxParentResults(Results):
        Gelectron =  -0.0375 / 27.211  # in hartree
    
        @staticmethod
        def _get_energy(job, vibrations:bool):
            if not vibrations:
                return job.results.get_energy()
            e = job.results.readrkf('Thermodynamics', 'Gibbs free Energy', file='engine')
            if isinstance(e, list):
                return e[0]
            return e
    
        @staticmethod
        def _get_solvation_energy(job):
           dG_solvation = job.results.readrkf('Energy','Solvation Energy (el)','adf') + job.results.readrkf('Energy','Solvation Energy (cd)','adf')
           return dG_solvation
    
    class CRSActivityCoefficientResults(CRSResults):
        def get_gibbs_energy(self):
            """ Gibbs energy in hartree """
            return float(self.get_results()['G solute'][1]) * 0.00159376 # kcal/mol to hartree
    
    class CRSActivityCoefficientJob(CRSJob):
        _result_type = CRSActivityCoefficientResults
        
        def __init__(self, solvent_coskf, solute_coskf, name=None, temperature=298.15, copy_coskf=False):
            CRSJob.__init__(self, name=name)
            self.solvent_coskf = solvent_coskf
            self.solute_coskf = solute_coskf
            self.temperature = temperature
            self.copy_coskf = copy_coskf
    
        def prerun(self):
            self._prerun()
    
        def _prerun(self):
            if self.copy_coskf:
                new_solvent = f'solvent_{os.path.basename(self.solvent_coskf)}'
                new_solute  = f'solute_{os.path.basename(self.solute_coskf)}'
                shutil.copy(self.solvent_coskf, os.path.join(self.path, new_solvent))
                shutil.copy(self.solute_coskf, os.path.join(self.path, new_solute))
                self.solvent_coskf =  new_solvent
                self.solute_coskf = new_solute
            self.settings.input.property._h = 'ACTIVITYCOEF'
            compounds = [Settings(), Settings()]
            compounds[0]._h    = self.solvent_coskf;    compounds[1]._h    = self.solute_coskf
            compounds[0].frac1 = 1;               compounds[1].frac1 = 0
            
            self.settings.input.temperature = str(self.temperature)
            self.settings.input.compound = compounds
    
    class AMSRedoxDirectResults(AMSRedoxParentResults):
        def get_oxidation_potential(self, vibrations=True, unit='eV'):
            Greact = self._get_energy(self.job.children['job_0'], vibrations=vibrations)
            Gprod = self._get_energy(self.job.children['job_ox'], vibrations=vibrations) + self.Gelectron 
            ret = (Gprod - Greact) * Units.convert(1.0, 'hartree', unit)
            return ret 
    
        def get_reduction_potential(self, vibrations=True, unit='eV'):
            Greact = self._get_energy(self.job.children['job_0'], vibrations=vibrations) + self.Gelectron 
            Gprod = self._get_energy(self.job.children['job_red'], vibrations=vibrations) 
            ret = (Gprod - Greact) * Units.convert(1.0, 'hartree', unit)
            ret *= -1 # deltaG = -nFE
            return ret 
    
    class AMSRedoxDirectJob(AMSRedoxParentJob):
        _result_type = AMSRedoxDirectResults
    
        def __init__(self, 
                     molecule:Molecule, # Molecule
                     solvent:str,  # ADF pre-defined solvent
                     name:str=None, 
                     settings:Settings=None,
                     oxidation:bool=True, 
                     reduction:bool=False,
                     vibrations:bool=True):
    
            AMSRedoxParentJob.__init__(self, name=name, settings=settings, molecule=molecule, oxidation=oxidation, reduction=reduction)
    
            self.solvent = solvent
            self.vibrations = vibrations
    
            s = Settings()
            s += self.settings
            s.input.ams.Task = 'GeometryOptimization'
            s += self.solvation_settings(self.solvent)
            s.update( _spinpol_settings(self.input_molecule, self.orig_charge) )
            s.input.ams.System.Charge = self.orig_charge
            s.input.ams.System.PerturbCoordinates = 0.01
            s.input.ams.Properties.NormalModes = str(self.vibrations)
            job_0 = AMSJob(settings=s, name='job_0', molecule=self.input_molecule)
            self.children['job_0'] = job_0
    
            if oxidation:
                sox = s.copy()
                sox.update(_spinpol_settings(self.input_molecule, self.ox_charge))
                sox.input.ams.System.Charge = self.ox_charge
                sox.input.ams.System.PerturbCoordinates = 0.01
                job_ox = AMSJob(settings=sox, name='job_ox')
    
                @add_to_instance(job_ox)
                def prerun(self):
                    self.molecule = job_0.results.get_main_molecule()
    
                self.children['job_ox'] = job_ox
    
            if reduction:
                sred = s.copy()
                sred.update( _spinpol_settings(self.input_molecule, self.red_charge) )
                sred.input.ams.System.Charge = self.red_charge
                sred.input.ams.System.PerturbCoordinates = 0.01
                job_red = AMSJob(settings=sred, name='job_red')
    
                @add_to_instance(job_red)
                def prerun(self):
                    self.molecule = job_0.results.get_main_molecule()
    
                self.children['job_red'] = job_red
    
    class AMSRedoxScreeningResults(Results):
        Gelectron =  -0.0375 / 27.211  # in hartree
    
        def get_oxidation_potential(self, vibrations=True, unit='eV'):
            """ Note: vibrations cannot be disabled for AMSRedoxScreening """
            Greact = self.job.children['activitycoef_0'].results.get_gibbs_energy()
            Gprod = self.job.children['activitycoef_ox'].results.get_gibbs_energy() + self.Gelectron 
            ret = (Gprod - Greact) * Units.convert(1.0, 'hartree', unit)
            return ret 
    
        def get_reduction_potential(self, vibrations=True, unit='eV'):
            """ Note: vibrations cannot be disabled for AMSRedoxScreening """
            Greact = self.job.children['activitycoef_0'].results.get_gibbs_energy() + self.Gelectron
            Gprod = self.job.children['activitycoef_red'].results.get_gibbs_energy() 
            ret = (Gprod - Greact) * Units.convert(1.0, 'hartree', unit)
            ret *= -1 # deltaG = -nFE
            return ret 
            
    class AMSRedoxScreeningJob(AMSRedoxParentJob):
        _result_type = AMSRedoxScreeningResults
    
        def __init__(self, 
                     molecule:Molecule, # Molecule
                     solvent_coskf:str, # path to solvent .coskf file
                     name:str=None, 
                     settings:Settings=None,
                     oxidation:bool=True, 
                     reduction:bool=False,
                     copy_coskf=False):
    
            """
                copy_coskf: bool
                    Will copy the coskf files into the job's own directory before running.
            """
            AMSRedoxParentJob.__init__(self, name=name, settings=settings, molecule=molecule, oxidation=oxidation, reduction=reduction)
    
            self.solvent_coskf = solvent_coskf
    
            # dftb_go_0
            s = Settings()
            s.input.ams.Task = 'GeometryOptimization'
            s.input.DFTB.Model = 'GFN1-xTB'
            s.input.ams.System.Charge = self.orig_charge
            s.input.ams.System.PerturbCoordinates = 0.01
            dftb_go_0 = AMSJob(settings=s, molecule=self.input_molecule, name='dftb_go_0')
            self.children['dftb_go_0'] = dftb_go_0
    
            if oxidation:
                sox = s.copy()
                sox.input.ams.System.PerturbCoordinates = 0.01
                sox.input.ams.System.Charge = self.ox_charge
                dftb_go_ox = AMSJob(settings=sox, name='dftb_go_ox')
    
                @add_to_instance(dftb_go_ox)
                def prerun(self):
                    self.molecule = dftb_go_0.results.get_main_molecule()
                self.children['dftb_go_ox'] = dftb_go_ox
    
            if reduction:
                sred = s.copy()
                sred.input.ams.System.PerturbCoordinates = 0.01
                sred.input.ams.System.Charge = self.red_charge
                dftb_go_red = AMSJob(settings=sred, name='dftb_go_red')
    
                @add_to_instance(dftb_go_red)
                def prerun(self):
                    self.molecule = dftb_go_0.results.get_main_molecule()
                self.children['dftb_go_red'] = dftb_go_red
    
            # gencoskf_0
            s = self.settings.copy()
            s.update( _spinpol_settings(self.input_molecule, self.orig_charge) )
            s.input.ams.System.Charge = self.orig_charge
            gencoskf_0 = ADFCOSMORSCompoundJob(molecule=None, name='gencoskf_0', singlepoint=True, settings=s)
    
            @add_to_instance(gencoskf_0)
            def prerun(self):
                self.input_molecule = dftb_go_0.results.get_main_molecule() # will inherit the charge
            self.children['gencoskf_0'] = gencoskf_0
    
            if oxidation:
                sox = s.copy()
                sox.update( _spinpol_settings(self.input_molecule, self.ox_charge) )
                sox.input.ams.System.Charge = self.ox_charge
                gencoskf_ox = ADFCOSMORSCompoundJob(molecule=None, name='gencoskf_ox', singlepoint=True, settings=sox)
    
                @add_to_instance(gencoskf_ox)
                def prerun(self):
                    self.input_molecule = dftb_go_ox.results.get_main_molecule()
                self.children['gencoskf_ox'] = gencoskf_ox
    
            if reduction:
                sred = s.copy()
                sred.update( _spinpol_settings(self.input_molecule, self.red_charge) )
                sred.input.ams.System.Charge = self.red_charge
                gencoskf_red = ADFCOSMORSCompoundJob(molecule=None, name='gencoskf_red', singlepoint=True, settings=sred)
    
                @add_to_instance(gencoskf_red)
                def prerun(self):
                    self.input_molecule = dftb_go_red.results.get_main_molecule()
                self.children['gencoskf_red'] = gencoskf_red
                
            # activitycoef_0
            activitycoef_0 = CRSActivityCoefficientJob(name='activitycoef_0', solvent_coskf=self.solvent_coskf, solute_coskf=None, copy_coskf=copy_coskf)
    
            @add_to_instance(activitycoef_0)
            def prerun(self):
                self.solute_coskf = gencoskf_0.results.coskfpath()
                self._prerun()
            self.children['activitycoef_0'] = activitycoef_0
    
            if oxidation:
                activitycoef_ox = CRSActivityCoefficientJob(name='activitycoef_ox', solvent_coskf=self.solvent_coskf, solute_coskf=None, copy_coskf=copy_coskf)
    
                @add_to_instance(activitycoef_ox)
                def prerun(self):
                    self.solute_coskf = gencoskf_ox.results.coskfpath()
                    self._prerun()
                self.children['activitycoef_ox'] = activitycoef_ox
    
            if reduction:
                activitycoef_red = CRSActivityCoefficientJob(name='activitycoef_red', solvent_coskf=self.solvent_coskf, solute_coskf=None, copy_coskf=copy_coskf)
    
                @add_to_instance(activitycoef_red)
                def prerun(self):
                    self.solute_coskf = gencoskf_red.results.coskfpath()
                    self._prerun()
                self.children['activitycoef_red'] = activitycoef_red
    
    class AMSRedoxThermodynamicCycleResults(AMSRedoxParentResults):
        def get_oxidation_potential(self, vibrations=True, unit='eV'):
            Greact  = self._get_energy(self.job.children['go_0_vacuum'], vibrations=vibrations) \
                    + self._get_energy(self.job.children['go_0_vacuum_sp_solvated'], vibrations=False) \
                    + self._get_energy(self.job.children['go_0_solvated_sp_vacuum'], vibrations=False) \
                    - 2*self._get_energy(self.job.children['go_0_vacuum'], vibrations=False) 
    
            Gprod   = self._get_energy(self.job.children['go_ox_vacuum'], vibrations=vibrations) \
                    + self._get_energy(self.job.children['go_ox_vacuum_sp_solvated'], vibrations=False) \
                    + self._get_energy(self.job.children['go_ox_solvated_sp_vacuum'], vibrations=False) \
                    - 2*self._get_energy(self.job.children['go_ox_vacuum'], vibrations=False) \
                    + self.Gelectron
    
            ret = (Gprod - Greact) * Units.convert(1.0, 'hartree', unit)
            return ret 
    
        def get_reduction_potential(self, vibrations=True, unit='eV'):
            Greact  = self._get_energy(self.job.children['go_0_vacuum'], vibrations=vibrations) \
                    + self._get_energy(self.job.children['go_0_vacuum_sp_solvated'], vibrations=False) \
                    + self._get_energy(self.job.children['go_0_solvated_sp_vacuum'], vibrations=False) \
                    - 2*self._get_energy(self.job.children['go_0_vacuum'], vibrations=False)  \
                    + self.Gelectron
    
            Gprod   = self._get_energy(self.job.children['go_red_vacuum'], vibrations=vibrations) \
                    + self._get_energy(self.job.children['go_red_vacuum_sp_solvated'], vibrations=False) \
                    + self._get_energy(self.job.children['go_red_solvated_sp_vacuum'], vibrations=False) \
                    - 2*self._get_energy(self.job.children['go_red_vacuum'], vibrations=False) 
    
            ret = (Gprod - Greact) * Units.convert(1.0, 'hartree', unit)
            ret *= -1 # deltaG = -nFE
            return ret 
    
    class AMSRedoxThermodynamicCycleJob(AMSRedoxParentJob):
        _result_type = AMSRedoxThermodynamicCycleResults
    
        def __init__(self, 
                     molecule:Molecule, # Molecule
                     name:str=None, 
                     solvent:str='Water',
                     settings:Settings=None,
                     oxidation:bool=True, 
                     reduction:bool=False,
                     vibrations:bool=False):
    
            AMSRedoxParentJob.__init__(self, name=name, settings=settings, molecule=molecule, oxidation=oxidation, reduction=reduction)
    
            self.vibrations = vibrations
            self.solvent = solvent
    
            # go_0_vacuum
            s = self.get_dft_0_settings(vibrations=self.vibrations, perturbcoordinates=True)
            s.input.ams.Task = 'GeometryOptimization'
            go_0_vacuum = AMSJob(settings=s, molecule=self.input_molecule, name='go_0_vacuum')
    
            @add_to_instance(go_0_vacuum)
            def prerun(self):
                self.molecule = self.parent.input_molecule
                
            self.children['go_0_vacuum'] = go_0_vacuum
    
            # go_0_vacuum_sp_solvated
            ss = self.get_dft_0_settings(vibrations=False, perturbcoordinates=False)
            ss.input.ams.Task = 'SinglePoint'
            ss += self.solvation_settings(self.solvent)
            go_0_vacuum_sp_solvated = AMSJob(settings=ss, molecule=None, name='go_0_vacuum_sp_solvated')
    
            @add_to_instance(go_0_vacuum_sp_solvated)
            def prerun(self):
                self.molecule = go_0_vacuum.results.get_main_molecule()
    
            self.children['go_0_vacuum_sp_solvated'] = go_0_vacuum_sp_solvated
    
            # go_0_solvated
            s = self.get_dft_0_settings(vibrations=self.vibrations, perturbcoordinates=True)
            s.input.ams.Task = 'GeometryOptimization'
            s += self.solvation_settings(self.solvent)
            go_0_solvated = AMSJob(settings=s, molecule=None, name='go_0_solvated')
    
            @add_to_instance(go_0_solvated)
            def prerun(self):
                self.molecule = go_0_vacuum.results.get_main_molecule()
                
            self.children['go_0_solvated'] = go_0_solvated
    
            # go_0_solvated_sp_vacuum
            ss = self.get_dft_0_settings(vibrations=False, perturbcoordinates=False)
            ss.input.ams.Task = 'SinglePoint'
            go_0_solvated_sp_vacuum = AMSJob(settings=ss, molecule=None, name='go_0_solvated_sp_vacuum')
    
            @add_to_instance(go_0_solvated_sp_vacuum)
            def prerun(self):
                self.molecule = go_0_solvated.results.get_main_molecule()
    
            self.children['go_0_solvated_sp_vacuum'] = go_0_solvated_sp_vacuum
    
            if oxidation:
                # go_ox_vacuum
                s = self.get_dft_ox_settings(vibrations=self.vibrations, perturbcoordinates=True)
                s.input.ams.Task = 'GeometryOptimization'
                go_ox_vacuum = AMSJob(settings=s, molecule=self.input_molecule, name='go_ox_vacuum')
    
                @add_to_instance(go_ox_vacuum)
                def prerun(self):
                    self.molecule = go_0_vacuum.results.get_main_molecule()
                    
                self.children['go_ox_vacuum'] = go_ox_vacuum
    
                # go_ox_vacuum_sp_solvated
                ss = self.get_dft_ox_settings(vibrations=False, perturbcoordinates=False)
                ss.input.ams.Task = 'SinglePoint'
                ss += self.solvation_settings(self.solvent)
                go_ox_vacuum_sp_solvated = AMSJob(settings=ss, molecule=None, name='go_ox_vacuum_sp_solvated')
    
                @add_to_instance(go_ox_vacuum_sp_solvated)
                def prerun(self):
                    self.molecule = go_ox_vacuum.results.get_main_molecule()
    
                self.children['go_ox_vacuum_sp_solvated'] = go_ox_vacuum_sp_solvated
    
                # go_ox_solvated
                s = self.get_dft_ox_settings(vibrations=self.vibrations, perturbcoordinates=True)
                s.input.ams.Task = 'GeometryOptimization'
                s += self.solvation_settings(self.solvent)
                go_ox_solvated = AMSJob(settings=s, molecule=None, name='go_ox_solvated')
    
                @add_to_instance(go_ox_solvated)
                def prerun(self):
                    self.molecule = go_ox_vacuum.results.get_main_molecule()
                    
                self.children['go_ox_solvated'] = go_ox_solvated
    
                # go_ox_solvated_sp_vacuum
                ss = self.get_dft_ox_settings(vibrations=False, perturbcoordinates=False)
                ss.input.ams.Task = 'SinglePoint'
                go_ox_solvated_sp_vacuum = AMSJob(settings=ss, molecule=None, name='go_ox_solvated_sp_vacuum')
    
                @add_to_instance(go_ox_solvated_sp_vacuum)
                def prerun(self):
                    self.molecule = go_ox_solvated.results.get_main_molecule()
    
                self.children['go_ox_solvated_sp_vacuum'] = go_ox_solvated_sp_vacuum
    
            if reduction:
                # go_red_vacuum
                s = self.get_dft_red_settings(vibrations=self.vibrations, perturbcoordinates=True)
                s.input.ams.Task = 'GeometryOptimization'
                go_red_vacuum = AMSJob(settings=s, molecule=self.input_molecule, name='go_red_vacuum')
    
                @add_to_instance(go_red_vacuum)
                def prerun(self):
                    self.molecule = go_0_vacuum.results.get_main_molecule()
                    
                self.children['go_red_vacuum'] = go_red_vacuum
    
                # go_red_vacuum_sp_solvated
                ss = self.get_dft_red_settings(vibrations=False, perturbcoordinates=False)
                ss.input.ams.Task = 'SinglePoint'
                ss += self.solvation_settings(self.solvent)
                go_red_vacuum_sp_solvated = AMSJob(settings=ss, molecule=None, name='go_red_vacuum_sp_solvated')
    
                @add_to_instance(go_red_vacuum_sp_solvated)
                def prerun(self):
                    self.molecule = go_red_vacuum.results.get_main_molecule()
    
                self.children['go_red_vacuum_sp_solvated'] = go_red_vacuum_sp_solvated
    
                # go_red_solvated
                s = self.get_dft_red_settings(vibrations=self.vibrations, perturbcoordinates=True)
                s.input.ams.Task = 'GeometryOptimization'
                s += self.solvation_settings(self.solvent)
                go_red_solvated = AMSJob(settings=s, molecule=None, name='go_red_solvated')
    
                @add_to_instance(go_red_solvated)
                def prerun(self):
                    self.molecule = go_red_vacuum.results.get_main_molecule()
                    
                self.children['go_red_solvated'] = go_red_solvated
    
                # go_red_solvated_sp_vacuum
                ss = self.get_dft_red_settings(vibrations=False, perturbcoordinates=False)
                ss.input.ams.Task = 'SinglePoint'
                go_red_solvated_sp_vacuum = AMSJob(settings=ss, molecule=None, name='go_red_solvated_sp_vacuum')
    
                @add_to_instance(go_red_solvated_sp_vacuum)
                def prerun(self):
                    self.molecule = go_red_solvated.results.get_main_molecule()
    
                self.children['go_red_solvated_sp_vacuum'] = go_red_solvated_sp_vacuum
                
[/code]

## Details about individual calculations¶

The paper by Belic et al. describes four ways to calculate the oxidation potential which are described in the tabs below, however we have extended them to allow for calculation of the reduction potential. In general, \\(g_p^i\\) denotes the optimised geometry of the molecule in phase \\(p\\) (solvent [sol] or gaseous [gas]) and in state \\(i\\) (oxidised [+]/reduced [-] or neutral [0]), \\(G_P^I(g_p^i)\\) denotes the Gibbs free energy of the geometry \\(g_p^i\\) calculated in phase \\(P\\) and state \\(I\\), similarly \\(E_P(g_p^i)\\) denotes the bond energy of the geometry \\(g_p^i\\) calculated in phase \\(P\\). The electron Gibbs free energy \\(G_{gas}(e^-)=0.0375 \text{eV}\\) is also used in these calculations.

Direct (DC)Thermodynamic Cycle (TC)Screening

Direct method of calculating oxidation potential using the COSMO solvation model.

\\[\Delta G^{DC}_{COSMO} = G_{sol}^\pm(g_{sol}^\pm) \pm G_{gas}(e^-) - G_{sol}^0(g_{sol}^0)\\]

The following steps are calculated

Step | Task | Structure | Method | I | P | Frequencies  
---|---|---|---|---|---|---  
1 | GO |  | DFT | 0 | sol | Yes  
2 | GO |  | DFT | \\(\pm\\) | sol | Yes  
  
Thermodynamic cycle using either the COSMO or the COSMO-RS solvation model.

\\[\Delta G^{TC}_{COSMO/COSMO-RS} = G_{sol}^\pm(g_{gas}^\pm) \pm G_{gas}(e^-) - G_{sol}^0(g_{gas}^0)\\]

where we have

\\[G_{sol}^i = G_{gas}^i(g_{gas}^i) + \Delta G_{sol}^i(g_{gas}^i) + [E_{gas}(g_{sol}^i) - E_{gas}(g_{gas}^i)].\\]

The following steps are calculated

Step | Task | Structure | Method | I | P | Frequencies  
---|---|---|---|---|---|---  
1 | GO |  | DFT | 0 | gas | Yes  
2 | SP | \\(g^0_{gas}\\), step 1 | DFT | 0 | sol | No  
3 | GO |  | DFT | 0 | sol | No  
4 | SP | \\(g^0_{sol}\\), step 3 | DFT | 0 | gas | No  
5 | GO |  | DFT | \\(\pm\\) | gas | Yes  
6 | SP | \\(g^\pm_{gas}\\), step 5 | DFT | \\(\pm\\) | sol | No  
7 | GO |  | DFT | \\(\pm\\) | sol | No  
8 | SP | \\(g^\pm_{sol}\\), step 7 | DFT | \\(\pm\\) | gas | No  
  
This method also implements the thermodynamic cycle, but uses lower theory methods (DFTB) to greatly increase speed of calculation. This method uses COSMO-RS as the solvation method.

\\[\Delta G_{COSMO-RS}^{screening} = G_{sol, CRS}^\pm(g_{gas}^\pm) \pm G_{gas}(e^-) - G_{sol, CRS}^0(g_{gas}^0)\\]

where we have

\\[G_{sol, CRS}^i = E_{sol}^i(g_{gas}^i) + \Delta G_{sol, CRS}^i(g_{gas}^i])\\]

Step | Task | Structure | Method | I | P | Frequencies  
---|---|---|---|---|---|---  
1 | GO |  | DFTB | 0 | gas | No  
2 | SP | \\(g^0_{gas}\\), step 1 | DFT | 0 | sol | No  
3 | GO |  | DFTB | \\(\pm\\) | gas | No  
4 | SP | \\(g^\pm_{gas}\\), step 3 | DFT | \\(\pm\\) | sol | No  
  
[Next ](ExcitationsWorkflow.html "Workflow: filtering molecules based on excitation energies") [ Previous](ReactionEnergyBenchmark.html "Reaction energies with many different engines")

* * *

  * ### Application Areas

    * [Batteries & PVs](https://www.scm.com/applications/batteries/)
    * [Bonding Analysis](https://www.scm.com/applications/chemical-bonding-analysis/)
    * [Catalysis](https://www.scm.com/applications/catalysis/)
    * [Heavy Elements](https://www.scm.com/applications/heavy-elements/)
    * [Inorganic Chemistry](https://www.scm.com/applications/inorganic-chemistry/)
    * [Life Sciences](https://www.scm.com/applications/pharma/)
    * [Materials Science](https://www.scm.com/applications/materials-science/)
    * [Nanotechnology](https://www.scm.com/applications/nanotechnology/)
    * [Oil and Gas](https://www.scm.com/applications/oil-and-gas/)
    * [Organic Electronics](https://www.scm.com/applications/organic-electronics/)
    * [Polymers](https://www.scm.com/applications/polymers/)
    * [Spectroscopy](https://www.scm.com/applications/spectroscopy/)
    * [Supercomputer / HPC](https://www.scm.com/applications/a-computing-center/)
    * [Teaching Computational Chemistry with AMS](https://www.scm.com/applications/teaching/)

  * ### Products

    * [AMS Driver](https://www.scm.com/product/ams/)
    * [ADF](https://www.scm.com/product/adf/)
    * [BAND](https://www.scm.com/product/band_periodicdft/)
    * [COSMO-RS](https://www.scm.com/product/cosmo-rs/)
    * [DFTB](https://www.scm.com/product/dftb/)
    * [GUI](https://www.scm.com/product/gui/)
    * [ML Potentials & FF](https://www.scm.com/product/machine-learning-potentials/)
    * [MOPAC](https://www.scm.com/product/mopac/)
    * [ParAMS](https://www.scm.com/product/params/)
    * [PLAMS](https://www.scm.com/product/plams/)
    * [Quantum ESPRESSO](https://www.scm.com/product/quantum-espresso/)
    * [ReaxFF](https://www.scm.com/product/reaxff/)
    * [Workflows](https://www.scm.com/product/advanced-workflows/)

  * ### Support

    * [Brochure](https://www.scm.com/amsterdam-modeling-suite/brochures/)
    * [Consulting & Contract Research](https://www.scm.com/amsterdam-modeling-suite/consulting/)
    * [Discussion List](https://www.scm.com/adf-discussion-list/)
    * [Documentation](https://www.scm.com/support/ams-tutorials-and-manuals/)
    * [Downloads](https://www.scm.com/support/downloads/)
    * [FAQs](https://www.scm.com/faq/)
    * [GUI Tutorials](https://www.scm.com/doc/Tutorials/GUI_overview/GUI_overview_tutorials.html)
    * [Installation](https://www.scm.com/support/ams-installation-videos/)
    * [Literature Highlights](https://www.scm.com/category/highlights/)
    * [Papers Citing ADF](https://www.scm.com/amsterdam-modeling-suite/research-papers-citing-adf/)
    * [Release Notes](https://www.scm.com/support/documentation-previous-versions/release-notes/)
    * [Support Overview](https://www.scm.com/support/)
    * [Teaching Materials](https://www.scm.com/support/background/amsterdam-modeling-suite-teaching-materials/)
    * [Videos](https://www.scm.com/amsterdam-modeling-suite/videos-tutorials-and-web-presentations/)
    * [Webinars](https://www.scm.com/about-us/news-agenda/web-presentations-by-adf-experts/)
    * [Workshops](https://www.scm.com/about-us/news-agenda/adf-hands-on-workshops/)

  * ### About Us

    * [Careers](https://www.scm.com/about-us/careers/)
    * [Collaborations](https://www.scm.com/about-us/collaborations/)
    * [Contact Us](https://www.scm.com/about-us/contact-us/)
    * [Contributors](https://www.scm.com/about-us/our-authors/)
    * [EU Projects](https://www.scm.com/about-us/eu-projects/)
    * [Events](https://www.scm.com/about-us/news-agenda/)
    * [Mission & Vision](https://www.scm.com/about-us/mission-vision/)
    * [News](https://www.scm.com/category/news/)
    * [Newsletters](https://www.scm.com/newsletters/)
    * [The SCM Team](https://www.scm.com/about-us/our-people/)

  * ### Pricing & Licensing

    * [License Terms](https://www.scm.com/amsterdam-modeling-suite/pricing-licensing/scm-license-terms/)
    * [Ordering](https://www.scm.com/amsterdam-modeling-suite/pricing-licensing/ordering-procedure/)
    * [Price Calculator](https://www.scm.com/amsterdam-modeling-suite/pricing-licensing/price-quote/calculate-your-price/)
    * [Price Quote](https://www.scm.com/amsterdam-modeling-suite/pricing-licensing/price-quote/)
    * [Pricing & Licensing](https://www.scm.com/amsterdam-modeling-suite/pricing-licensing/)
    * [Resellers](https://www.scm.com/amsterdam-modeling-suite/pricing-licensing/adf-resellers/)

  * [Copyright](https://www.scm.com/copyright/)
  * [Terms of Use](https://www.scm.com/terms-of-use/)
  * [Privacy Policy](https://www.scm.com/privacy-policy/)
