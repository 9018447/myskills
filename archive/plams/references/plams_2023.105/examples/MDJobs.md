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
    * [COSMO-RS and property prediction](examples.html#cosmo-rs-and-property-prediction)
    * [Packmol and AMS-ASE interfaces](examples.html#packmol-and-ams-ase-interfaces)
    * [ParAMS and pyZacros](examples.html#params-and-pyzacros)
    * [Other AMS calculations](examples.html#other-ams-calculations)
    * [Pymatgen](examples.html#pymatgen)
    * [Pre-made recipes](examples.html#pre-made-recipes)
      * [ADF: Task COSMO-RS Compound](ADFCOSMORSCompound.html)
      * AMS Molecular Dynamics PLAMS jobs
        * AMSMDJob API
        * AMSNVEJob API
        * AMSNVTJob API
        * AMSNPTJob API
        * AMSNVESpawnerJob API
        * AMSMDScanDensityJob API
        * AMSRDFJob API
        * AMSMSDJob API
        * AMSVACFJob API
      * [ADF fragment job](adffragment.html)
      * [Reorganization Energy](ReorganizationEnergy.html)
      * [NBO with ADF](adfnbo.html)
      * [Numerical gradients](numgrad.html)
      * [Numerical Hessian](numhess.html)
      * [Global Minimum Search](global_minimum.html)
      * [Vibronic Density of States using the AH-FC method](pyAHFCDOS.html)
      * [Vibronic Density of States with ADF](fcf_dos.html)
  * [Cookbook](../cookbook/cookbook.html)
  * [Citations](../citations.html)

  * [FAQ](../FAQ.html)

__[PLAMS](../index.html)

  * [Documentation](../PLAMS.html/../../Documentation/index.html)/
  * [PLAMS](../index.html)/
  * [Examples](examples.html)/
  * AMS Molecular Dynamics PLAMS jobs

# AMS Molecular Dynamics PLAMS jobs¶

See also

**Example** : [Molecular dynamics with Python tutorial](../../Tutorials/MolecularDynamicsAndMonteCarlo/MDintroPython/intro.html)

In AMS2023, the following special Jobs exist to simplify running MD simulations (and continuing/restarting MD simulations):

  * `AMSMDJob`. A general class for which you can set up most common MD options using arguments to the constructor.

  * `AMSNVEJob` for NVE simulations

  * `AMSNVTJob` for NVT simulations

  * `AMSNPTJob` for NPT simulations

  * `AMSMDScanDensityJob` for running MD deformation simulations while isotropically scaling the density

  * `AMSNVESpawnerJob` is a special MultiJob that runs several NVE simulations with initial velocities taken from evenly spaced frames in a previous job.

Some default values are different from AMS. For example, the checkpoint frequency is set to a higher number, and the thermostat constant `tau` is automatically set to 400 times the timestep, by default.

Always check the input by calling `job.get_input()` before running a job.

In general, the jobs and results classes inherit from [`AMSJob`](../interfaces/ams.html#scm.plams.interfaces.adfsuite.ams.AMSJob "scm.plams.interfaces.adfsuite.ams.AMSJob") and [`AMSResults`](../interfaces/ams.html#scm.plams.interfaces.adfsuite.ams.AMSResults "scm.plams.interfaces.adfsuite.ams.AMSResults").

The NVE, NVT, and NPT classes simply remove the below options if they are set:

allowed input block | AMSMDJob | NVE | NVT | NPT  
---|---|---|---|---  
Thermostat | yes | no | yes | yes  
Barostat | yes | no | no | yes  
Nanoreactor | yes | no | no | no  
Deformation | yes | no | no | no  
  
The following jobs help with the postanalysis:

  * `AMSMSDJob` for calculating mean square displacement (MSD)

  * `AMSRDFJob` for calculating radial distribution functions (RDF)

  * `AMSVACFJob` for calculating velocity autocorrelation functions (VACF)

## AMSMDJob API¶

_class _`AMSMDJob`(_velocities =None_, _timestep =None_, _samplingfreq =None_, _nsteps =None_, _checkpointfrequency =None_, _writevelocities =None_, _writebonds =None_, _writemolecules =None_, _writecharges =None_, _writeenginegradients =None_, _calcpressure =None_, _molecule =None_, _temperature =None_, _thermostat =None_, _tau =None_, _thermostat_region =None_, _pressure =None_, _barostat =None_, _barostat_tau =None_, _scale =None_, _equal =None_, _constantvolume =None_, _binlog_time =None_, _binlog_pressuretensor =None_, __enforce_thermostat =False_, __enforce_barostat =False_, _** kwargs_)[[source]](../_modules/scm/plams/recipes/md/amsmdjob.html#AMSMDJob)¶
    
molecule: Molecule
    
The initial structure

name: str
    
The name of the job

settings: Settings
    
Settings for the job. You should normally not populate neither settings.input.ams.MolecularDynamics nor settings.input.ams.Task

velocities: float or AMSJob or str (path/to/ams.rkf) or 2-tuple (path/to/ams.rkf, frame-number)
    
If float, it is taken as the temperature. If AMSJob or str, the velocities are taken from the EndVelocities section of the corresponding ams.rkf file. If 2-tuple, the first item must be a path to an ams.rkf, and the second item an integer specifying the frame number - the velocities are then read from History%Velocities(framenumber).

timestep: float
    
Timestep

samplingfreq: int
    
Sampling frequency

nsteps: int
    
Length of simulation

**Trajectory options** :

checkpointfrequency: int
    
How frequently to write MDStep*.rkf checkpoint files

writevelocitiesbool
    
Whether to save velocities to ams.rkf (needed for example to restart from individual frames or to calculate velocity autocorrelation functions)

writebonds: bool
    
Whether to save bonds to ams.rkf

writemolecules: bool
    
Whether to write molecules to ams.rkf

writeenginegradients: bool
    
Whether to save engine gradients (negative of atomic forces) to ams.rkf

**Thermostat (NVT, NPT) options** :

thermostat: str
    
‘Berendsen’ or ‘NHC’

tau: float
    
Thermostat time constant (fs)

temperature: float or tuple of floats
    
Temperature (K). If a tuple/list of floats, the Thermostat.Duration option will be set to evenly divided intervals.

thermostat_region: str
    
Region for which to apply the thermostat

**Barostat (NPT) options** :

barostat: str
    
‘Berendsen’ or ‘MTK’

barostat_tau: float
    
Barostat time constant (fs)

pressure: float
    
Barostat pressure (pascal)

equal: str
    
‘XYZ’ etc.

scale: str
    
‘XYZ’ etc.

constantvolume: bool
    
Constant volume?

**Other options** :

calcpressure: bool
    
Whether to calculate pressure for each frame.

binlog_time: bool
    
Whether to log the time at every timestep in the BinLog section on ams.rkf

binlog_pressuretensor: bool
    
Whether to log the pressure tensor at every timestep in the BinLog section on ams.rkf

`__init__`(_velocities =None_, _timestep =None_, _samplingfreq =None_, _nsteps =None_, _checkpointfrequency =None_, _writevelocities =None_, _writebonds =None_, _writemolecules =None_, _writecharges =None_, _writeenginegradients =None_, _calcpressure =None_, _molecule =None_, _temperature =None_, _thermostat =None_, _tau =None_, _thermostat_region =None_, _pressure =None_, _barostat =None_, _barostat_tau =None_, _scale =None_, _equal =None_, _constantvolume =None_, _binlog_time =None_, _binlog_pressuretensor =None_, __enforce_thermostat =False_, __enforce_barostat =False_, _** kwargs_)[[source]](../_modules/scm/plams/recipes/md/amsmdjob.html#AMSMDJob.__init__)¶
    
`get_velocities_from`(_other_job_ , _frame =None_, _update_molecule =True_)[[source]](../_modules/scm/plams/recipes/md/amsmdjob.html#AMSMDJob.get_velocities_from)¶
    
Function to update the InitialVelocities block in self. It is normally not needed, instead use the e.g. AMSNVEJob.restart_from() function.

This function can be called in prerun() methods for MultiJobs

_classmethod _`restart_from`(_other_job_ , _frame =None_, _settings =None_, _use_prerun =False_, _** kwargs_)[[source]](../_modules/scm/plams/recipes/md/amsmdjob.html#AMSMDJob.restart_from)¶
    
other_job: AMSJob
    
The job to restart from.

frame: int
    
Which frame to read the structure and velocities from. If None, the final structure and end velocities will be used (section Molecule and MDResults%EndVelocities)

settings: Settings
    
Settings that override any other settings. All settings from other_job (e.g. the engine settings) are inherited by default but they can be overridden here.

use_prerun: bool
    
If True, the molecule and velocities will only be read from other_job inside the prerun() method. Set this to True to prevent PLAMS from waiting for other_job to finish as soon as the new job is defined.

kwargs: many options
    
See the docstring for AMSMDJob.

## AMSNVEJob API¶

This class uses the same arguments as `AMSMDJob`.

_class _`AMSNVEJob`(_** kwargs_)[[source]](../_modules/scm/plams/recipes/md/amsmdjob.html#AMSNVEJob)¶
    
A class for running NVE MD simulations

`__init__`(_** kwargs_)[[source]](../_modules/scm/plams/recipes/md/amsmdjob.html#AMSNVEJob.__init__)¶
    
## AMSNVTJob API¶

This class uses the same arguments as `AMSMDJob`.

_class _`AMSNVTJob`(_** kwargs_)[[source]](../_modules/scm/plams/recipes/md/amsmdjob.html#AMSNVTJob)¶
    
A class for running NVT MD simulations

`__init__`(_** kwargs_)[[source]](../_modules/scm/plams/recipes/md/amsmdjob.html#AMSNVTJob.__init__)¶
    
## AMSNPTJob API¶

This class uses the same arguments as `AMSMDJob`.

`AMSNPTResults` inherits from `AMSResults`.

_class _`AMSNPTJob`(_** kwargs_)[[source]](../_modules/scm/plams/recipes/md/amsmdjob.html#AMSNPTJob)¶
    
A class for running NPT MD simulations

`__init__`(_** kwargs_)[[source]](../_modules/scm/plams/recipes/md/amsmdjob.html#AMSNPTJob.__init__)¶
    
_class _`AMSNPTResults`(_* args_, _** kwargs_)[[source]](../_modules/scm/plams/recipes/md/amsmdjob.html#AMSNPTResults)¶
    
`get_equilibrated_molecule`(_equilibration_fraction =0.667_, _return_index =False_)[[source]](../_modules/scm/plams/recipes/md/amsmdjob.html#AMSNPTResults.get_equilibrated_molecule)¶
    
Discards the first equilibration_fraction of the trajectory. Calculates the average density of the rest. Returns the molecule with the closest density to the average density among the remaining trajectory.

## AMSNVESpawnerJob API¶

_class _`AMSNVESpawnerJob`(_previous_job_ , _n_nve =1_, _name ='nvespawnerjob'_, _** kwargs_)[[source]](../_modules/scm/plams/recipes/md/nvespawner.html#AMSNVESpawnerJob)¶
    
A class for running multiple NVE simulations with initial structures/velocities taken from an NVT trajectory. The NVT trajectory must contain the velocities!

`__init__`(_previous_job_ , _n_nve =1_, _name ='nvespawnerjob'_, _** kwargs_)[[source]](../_modules/scm/plams/recipes/md/nvespawner.html#AMSNVESpawnerJob.__init__)¶
    
previous_job: AMSJob
    
An AMSJob with an MD trajectory. Must contain velocities (WriteVelocities Yes). Note that the trajectory should have been equilibrated before it starts.

n_nveint
    
The number of NVE simulations to spawn

All other settings can be set as for an AMSNVEJob (e.g. `nsteps`).

`prerun`()[[source]](../_modules/scm/plams/recipes/md/nvespawner.html#AMSNVESpawnerJob.prerun)¶
    
Constructs the children jobs

## AMSMDScanDensityJob API¶

_class _`AMSMDScanDensityJob`(_molecule_ , _scan_density_upper =1.4_, _startstep =None_, _** kwargs_)[[source]](../_modules/scm/plams/recipes/md/scandensity.html#AMSMDScanDensityJob)¶
    
A class for scanning the density using MD Deformations

`__init__`(_molecule_ , _scan_density_upper =1.4_, _startstep =None_, _** kwargs_)[[source]](../_modules/scm/plams/recipes/md/scandensity.html#AMSMDScanDensityJob.__init__)¶
    
## AMSRDFJob API¶

_class _`AMSRDFJob`(_previous_job_ , _atom_indices =None_, _atom_indices_to =None_, _rmin =0.5_, _rmax =6_, _rstep =0.1_, _** kwargs_)[[source]](../_modules/scm/plams/recipes/md/trajectoryanalysis.html#AMSRDFJob)¶
    
`__init__`(_previous_job_ , _atom_indices =None_, _atom_indices_to =None_, _rmin =0.5_, _rmax =6_, _rstep =0.1_, _** kwargs_)[[source]](../_modules/scm/plams/recipes/md/trajectoryanalysis.html#AMSRDFJob.__init__)¶
    
previous_job: AMSJob
    
AMSJob with finished MD trajectory.

atom_indices: List[int]
    
Atom indices (starting with 1). If None, calculate RDF _from_ all atoms.

atom_indices_to: List[int]
    
Atom indices (starting with 1). If None, calculate RDF _to_ all atoms.

rmin: float
    
Minimum distance (angstrom)

rmax: float
    
Maximum distance (angstrom)

rstep: float
    
Bin width for the histogram (angstrom)

`prerun`()[[source]](../_modules/scm/plams/recipes/md/trajectoryanalysis.html#AMSRDFJob.prerun)¶
    
Creates the final settings. Do not call or override this method.

`postrun`()[[source]](../_modules/scm/plams/recipes/md/trajectoryanalysis.html#AMSRDFJob.postrun)¶
    
Creates rdf.txt. Do not call or override this method.

## AMSMSDJob API¶

_class _`AMSMSDJob`(_previous_job_ , _max_correlation_time_fs =10000_, _start_time_fit_fs =2000_, _atom_indices =None_, _** kwargs_)[[source]](../_modules/scm/plams/recipes/md/trajectoryanalysis.html#AMSMSDJob)¶
    
A convenient class wrapping around the trajectory analysis MSD tool

`__init__`(_previous_job_ , _max_correlation_time_fs =10000_, _start_time_fit_fs =2000_, _atom_indices =None_, _** kwargs_)[[source]](../_modules/scm/plams/recipes/md/trajectoryanalysis.html#AMSMSDJob.__init__)¶
    
previous_job: AMSJob
    
An AMSJob with an MD trajectory. Note that the trajectory should have been equilibrated before it starts.

max_correlation_time_fs: float
    
Maximum correlation time in femtoseconds

start_time_fit_fsfloat
    
Smallest correlation time for the linear fit

atom_indicesList[int]
    
If None, use all atoms. Otherwise use the specified atom indices (starting with 1)

kwargs: dict
    
Other options to AMSAnalysisJob

`prerun`()[[source]](../_modules/scm/plams/recipes/md/trajectoryanalysis.html#AMSMSDJob.prerun)¶
    
Constructs the final settings

`postrun`()[[source]](../_modules/scm/plams/recipes/md/trajectoryanalysis.html#AMSMSDJob.postrun)¶
    
Creates msd.txt, fit_msd.txt, and D.txt

## AMSVACFJob API¶

_class _`AMSVACFJob`(_previous_job_ , _max_correlation_time_fs =5000_, _max_freq =5000_, _atom_indices =None_, _** kwargs_)[[source]](../_modules/scm/plams/recipes/md/trajectoryanalysis.html#AMSVACFJob)¶
    
A class for calculating the velocity autocorrelation function and its power spectrum

`__init__`(_previous_job_ , _max_correlation_time_fs =5000_, _max_freq =5000_, _atom_indices =None_, _** kwargs_)[[source]](../_modules/scm/plams/recipes/md/trajectoryanalysis.html#AMSVACFJob.__init__)¶
    
previous_job: AMSJob
    
An AMSJob with an MD trajectory. Note that the trajectory should have been equilibrated before it starts.

max_correlation_time_fs: float
    
Maximum correlation time in femtoseconds

max_freq: float
    
The maximum frequency for the power spectrum in cm^-1

atom_indices: List[int]
    
Atom indices (starting with 1). If None, use all atoms.

`prerun`()[[source]](../_modules/scm/plams/recipes/md/trajectoryanalysis.html#AMSVACFJob.prerun)¶
    
Creates final settings

`postrun`()[[source]](../_modules/scm/plams/recipes/md/trajectoryanalysis.html#AMSVACFJob.postrun)¶
    
Creates vacf.txt and power_spectrum.txt

[Next ](adffragment.html "ADF fragment job") [ Previous](ADFCOSMORSCompound.html "ADF: Task COSMO-RS Compound")

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
