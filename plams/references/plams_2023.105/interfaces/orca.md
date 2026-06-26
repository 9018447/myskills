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
  * [Interfaces](interfaces.html)
    * [Amsterdam Modeling Suite](amssuite.html)
    * [Other programs](thirdparty.html)
      * [CP2K](cp2k.html)
      * [Crystal](crystal.html)
      * [DFTB+](dftbplus.html)
      * [Dirac](dirac.html)
      * [MOPAC (standalone program)](mopac.html)
      * ORCA
        * Settings
        * Loading jobs
        * API
      * [RASPA](raspa.html)
      * [VASP](vasp.html)
  * [Examples](../examples/examples.html)
  * [Cookbook](../cookbook/cookbook.html)
  * [Citations](../citations.html)

  * [FAQ](../FAQ.html)

__[PLAMS](../index.html)

  * [Documentation](../PLAMS.html/../../Documentation/index.html)/
  * [PLAMS](../index.html)/
  * [Interfaces](interfaces.html)/
  * [Other programs](thirdparty.html)/
  * ORCA

# ORCA¶

## Settings¶

The `input.main` branch of the [`Settings`](../components/settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") class corresponds to the lines starting with the special character `!` in the ORCA input. See the [orcalibrary](https://sites.google.com/site/orcainputlibrary) and the [manual](https://orcaforum.kofo.mpg.de/app.php/portal) for details. The `input.molecule` branch can be used to manually set the coordinate input line (e.g. to use an external file), it overwrites any existing molecule of the `ORCAJob`. If not set, the molecule of the `ORCAJob` will be parsed using the `xyz` option of ORCA.

An _end_ keyword is mandatory for only a subset of sections. For instance the following orca input shows the keywords _methods_ and _basis_ use of end:
[code] 
    job = ORCAJob(molecule=Molecule(<Path/to/molecule>), copy="input.xyz")
    job.settings.input.main = "UKS B3LYP/G SV(P) SV/J TightSCF Direct Grid3 FinalGrid4"
    job.settings.input.maxcore = "2000"
    job.settings.input.method.SpecialGridAtoms = 26
    job.settings.input.method.SpecialGridIntAcc = 7
    
    job.settings.input.basis.NewGTO._end = '26 "CP(PPP)"'
    job.settings.input.basis.NewAuxGTO = '26 "TZV/J" end'
    
    job.settings.input.molecule = "xyzfile +2 1 input.xyz" #overwrites the molecule given above
    
[/code]

The input generated during the execution of the ORCA job is similar to:
[code] 
    ! UKS B3LYP/G SV(P) SV/J TightSCF Direct Grid3 FinalGrid4
    %maxcore 2000
    %method SpecialGridAtoms 26
            SpecialGridIntAcc 7
            end
    %basis NewGTO 26 "CP(PPP)" end
           NewAuxGTO 26 "TZV/J" end
           end
    * xyzfile +2 1 input.xyz
    
[/code]

Additional input files (molecules, restart files, …) can be automatically copied to the jobs rundir by passing them to the `ORCAJob` initilization under `copy` (string or list). To reduce disk usage, symlinks can be used if the filesystem permits.

## Loading jobs¶

Calculations done without PLAMS can be loaded using the [`load_external()`](../components/jobs.html#scm.plams.core.basejob.SingleJob.load_external "scm.plams.core.basejob.SingleJob.load_external") functionality. The `ORCAResults` class does not support reading input files into [`Settings`](../components/settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") objects.

## API¶

_class _`ORCAJob`(_copy =None_, _copy_symlink =False_)[[source]](../_modules/scm/plams/interfaces/thirdparty/orca.html#ORCAJob)¶
    
A class representing a single computational job with [ORCA](https://orcaforum.cec.mpg.de).

In addition to the arguments of [`SingleJob`](../components/jobs.html#scm.plams.core.basejob.SingleJob "scm.plams.core.basejob.SingleJob"), `ORCAJob` takes a `copy_files` argument. `copy_files` can be a list or string, containing paths to files to be copied to the jobs directory. This might e.g. be a molecule, restart files etc. By setting `copy_symlink`, the files are not copied, but symlinked with relative links. The same things can be passed using the `settings` instance of the job, i.e. `self.settings.copy_files` and `self.settings.copy_symlink`. The former overwrites the latter.

`_result_type`¶
    
alias of `scm.plams.interfaces.thirdparty.orca.ORCAResults`

`__init__`(_copy_files =None_, _copy_symlink =False_, _** kwargs_)[[source]](../_modules/scm/plams/interfaces/thirdparty/orca.html#ORCAJob.__init__)¶
    
Initialize self. See help(type(self)) for accurate signature.

`_get_ready`()[[source]](../_modules/scm/plams/interfaces/thirdparty/orca.html#ORCAJob._get_ready)¶
    
Copy files to execution dir if self.copy_files is set.

`get_input`()[[source]](../_modules/scm/plams/interfaces/thirdparty/orca.html#ORCAJob.get_input)¶
    
Transform all contents of `input` branch of `settings` into string with blocks, subblocks, keys and values.

`print_molecule`()[[source]](../_modules/scm/plams/interfaces/thirdparty/orca.html#ORCAJob.print_molecule)¶
    
Print a molecule in the ORCA format using the xyz notation.

`get_runscript`()[[source]](../_modules/scm/plams/interfaces/thirdparty/orca.html#ORCAJob.get_runscript)¶
    
Returned runscript is just one line: `orca myinput.inp`

`check`()[[source]](../_modules/scm/plams/interfaces/thirdparty/orca.html#ORCAJob.check)¶
    
Look for the normal termination signal in the output.

_class _`ORCAResults`[[source]](../_modules/scm/plams/interfaces/thirdparty/orca.html#ORCAResults)¶
    
A class for ORCA results.

`get_runtime`()[[source]](../_modules/scm/plams/interfaces/thirdparty/orca.html#ORCAResults.get_runtime)¶
    
Return runtime in seconds from output.

`get_timings`()[[source]](../_modules/scm/plams/interfaces/thirdparty/orca.html#ORCAResults.get_timings)¶
    
Return timings section as dictionary. Units are seconds.

`check`()[[source]](../_modules/scm/plams/interfaces/thirdparty/orca.html#ORCAResults.check)¶
    
Returns true if ORCA TERMINATED NORMALLY is in the output

`get_scf_iterations`(_index =- 1_)[[source]](../_modules/scm/plams/interfaces/thirdparty/orca.html#ORCAResults.get_scf_iterations)¶
    
Returns Number of SCF Iterations from the Output File.

Set `index` to choose the n-th occurence, _e.g._ to choose an certain step. Also supports slices. Defaults to the last occurence.

`get_energy`(_index =- 1_, _unit ='a.u.'_)[[source]](../_modules/scm/plams/interfaces/thirdparty/orca.html#ORCAResults.get_energy)¶
    
Returns ‘FINAL SINGLE POINT ENERGY:’ from the output file.

Set `index` to choose the n-th occurence of the total energy in the output, _e.g._ to choose an certain step. Also supports slices. Defaults to the last occurence.

`get_dispersion`(_index =- 1_, _unit ='a.u.'_)[[source]](../_modules/scm/plams/interfaces/thirdparty/orca.html#ORCAResults.get_dispersion)¶
    
Returns ‘Dispersion correction’ from the output file.

Set `index` to choose the n-th occurence of the dispersion energy in the output, _e.g._ to choose a certain step. Also supports slices. Defaults to the last occurence.

`get_electrons`(_index =- 1_, _spin_resolved =False_)[[source]](../_modules/scm/plams/interfaces/thirdparty/orca.html#ORCAResults.get_electrons)¶
    
Get Electron count from Output.

Set `spins` to `True` to get a tuple of alpha and beta electrons instead of totals. Set `index` to choose the n-th occurcence in the output, _e.g._ to choose a certain step. Also supports slices. Defaults to the last occurence.

`get_gradients`(_match =0_, _energy_unit ='a.u.'_, _dist_unit ='bohr'_)[[source]](../_modules/scm/plams/interfaces/thirdparty/orca.html#ORCAResults.get_gradients)¶
    
Returns list of ndarrays with forces from the output (there the unit is a.u./bohr).

`match` is passed to `get_output_chunk()`, defaults to 0.

`get_dipole_vector`(_index =- 1_, _unit ='a.u.'_)[[source]](../_modules/scm/plams/interfaces/thirdparty/orca.html#ORCAResults.get_dipole_vector)¶
    
Get the Dipole Vector Returns the dipole vector, expressed in _unit_.

`get_dipole`(_** kwargs_)[[source]](../_modules/scm/plams/interfaces/thirdparty/orca.html#ORCAResults.get_dipole)¶
    
Get Hirshfeld Analysis from Output

Uses `get_dipole_vector()` to calculate the total dipole. All options are passed on.

`get_atomic_charges`(_method ='mulliken'_, _match =0_)[[source]](../_modules/scm/plams/interfaces/thirdparty/orca.html#ORCAResults.get_atomic_charges)¶
    
Get Atomic Charges from Output

  * method: Can be any one that is available in the output, e.g. mulliken or loewdin.

  * match: Select occurence in the output to use. E.g. when running multiple structures at once.
    
Is passed to `get_output_chunk()`, defaults to 0.

`get_hirshfeld`(_return_spin =False_, _match =0_, _skip =5_)[[source]](../_modules/scm/plams/interfaces/thirdparty/orca.html#ORCAResults.get_hirshfeld)¶
    
Get Hirshfeld Analysis from Output

  * return_spin: Return a tuple of (charge, spin) instead of just charge.

  * match: Select occurence in the output to use. E.g. when running multiple structures at once.
    
Is passed to `get_output_chunk()`, defaults to 0.

  * skip: Number of lines after the keyword in the outputfile to be skipped.
    
Don’t touch if you don’t have trouble with your ORCA versions output.

`get_orbital_energies`(_unit ='a.u.'_, _return_occupancy =False_, _match =0_)[[source]](../_modules/scm/plams/interfaces/thirdparty/orca.html#ORCAResults.get_orbital_energies)¶
    
Returns Orbital Energies.

  * Set return_occupancy to _True_ to recieve a tuple (Energy, Occupation) for each MO.

  * match: Select occurence in the output to use. E.g. when running multiple structures at once.
    
Is passed to `get_output_chunk()`, defaults to 0.

[Next ](raspa.html "RASPA") [ Previous](mopac.html "MOPAC \(standalone program\)")

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
