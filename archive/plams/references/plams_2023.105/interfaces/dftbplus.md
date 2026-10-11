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
      * DFTB+
        * Preparing a calculation
        * Results extraction
        * Example
        * API
      * [Dirac](dirac.html)
      * [MOPAC (standalone program)](mopac.html)
      * [ORCA](orca.html)
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
  * DFTB+

# DFTB+¶

(_contributed by_ [Patrick Melix](https://www.researchgate.net/profile/Patrick_Melix))

DFTB+ is a density-functional tight-binding implemenation. More information about DFTB can be found on its [official website](http://www.dftb-plus.info).

PLAMS offers a simple and incomplete DFTB+ interface. It is so far capable of handling molecular calculations. The relevant classes are `DFTBPlusJob` and `DFTBPlusResults`.

## Preparing a calculation¶

Preparing an instance of `DFTBPlusJob` follows the general principles for [`SingleJob`](../components/jobs.html#scm.plams.core.basejob.SingleJob "scm.plams.core.basejob.SingleJob"). Information adjusting the input file is stored in the `myjob.settings.input` branch. The geometry of your system can be supplied via the class [`Molecule`](../components/mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule"). If the Atomic Simulation Environment ([ASE](https://wiki.fysik.dtu.dk/ase/index.html)) is installed, the molecule is written using its engine. Otherwise this interface provies a basic routine. Note that the molecule is in this case transformed into the `GenFormat` with the `C` (cluster) or `S` (supercell) option, meaning the internal routine can handle clusters and supercell systems. The option `F` for fractional coordinates is not available! See [the manual](http://www.dftb-plus.info/documentation/) for further information on the different geometry-input types.

### Input¶

Input files for DFTB+ are either in HSD (_human-friendly structured data_) or XML format. This interface will produce HSD format input files. See [the manual](http://www.dftb-plus.info/documentation/) for further information on keywords and structure. The input file must be named _dftb_in.hsd_ and is therefore created using this name. Note that many values have standard settings, those will all be printed to _dftb_pin.hsd_ when you start a calculation. Check both files for errors when having problems.

HSD input files are organized using different properties. Each property is represented by a key. The key can be of type _logical_ , _integer_ , _real_ , _string_ , _property list_ or _method type_. The last two begin and end with curly brackets. Since _property lists_ and _method types_ are very similar in notation we require a way of representing that style in the tree-like structure of [`Settings`](../components/settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings"). This is done by automatically creating either _property lists_ or _method types_ whenever a key has a subkey.

  * If a key has a subkey and a key `_h`, the string assigned to `_h` will be used as a method name.

  * If a key has one or more subkeys it will be created as a _property list_ :
[code] #sets the hamiltonian property to be of a method type named DFTB
        myjob.setting.input.hamiltonian._h = 'DFTB'
        #sets the key parserversion of the property list parserversion to 4
        myjob.setting.input.parseroptions.parserversion = '4'
        
[/code]

Empty _method types_ can be created by not giving any subkeys to a key except `_h`.

### Runscript¶

The runscript will call the binary `dftb+`, so make sure it is in your `$PATH`. No options are supported. The standard output is redirected to `$JN.out`, errors to `$JN.err`.

## Results extraction¶

DFTB+ creates multiple outputfiles, none of them are renamed. See `detailed.out` for the results of your calculation. Resulting geometries are saved in `.xyz` and `.gen` format by DFTB+. Other files might be created depending on your calculation type.

General text processing methods from [`Results`](../components/results.html#scm.plams.core.results.Results "scm.plams.core.results.Results") can be used to obtain data from results files. At the moment only three functions for result extraction are defined:

  * Read the total energy `get_energy()`

  * Get the molecule from the `.xyz` file `get_molecule()`

  * Read the atomic charges `get_atomic_charges()`

## Example¶
[code] 
    common = Settings()
    
    common.input.driver._h = 'ConjugateGradient'
    common.input.hamiltonian._h = 'DFTB'
    common.input.hamiltonian.scc = 'yes'
    common.input.hamiltonian.mixer._h = 'Broyden'
    common.input.hamiltonian.mixer.mixingparameter = '0.2'
    common.input.hamiltonian.slaterkosterfiles._h = 'Type2Filenames'
    common.input.hamiltonian.slaterkosterfiles.prefix = '"~/SLAKO/mio-1-1/"'
    common.input.hamiltonian.slaterkosterfiles.separator = '"-"'
    common.input.hamiltonian.slaterkosterfiles.suffix = ".skf"
    common.input.hamiltonian.slaterkosterfiles.lowercasetypename = 'No'
    common.input.hamiltonian.maxangularmomentum.c = '"p"'
    common.input.hamiltonian.maxangularmomentum.h = '"s"'
    common.input.parseroptions.parserversion = '4'
    
    mol = Molecule(filename='mol.xyz') # read Molecule from mol.xyz
    
    job = DFTBPlusJob(name='plamstest', molecule=mol, settings=common)
    jobres = job.run()
    
    energy = jobres.get_energy(string='Fermi energy', unit='ev')
    print(energy)
    
    mol = jobres.get_molecule()
    print(mol)
    
    atomic_charges = jobres.get_atomic_charges()
    print(atomic_charges)
    
[/code]

## API¶

_class _`DFTBPlusJob`(_molecule =None_, _name ='plamsjob'_, _settings =None_, _depend =None_)[[source]](../_modules/scm/plams/interfaces/thirdparty/dftbplus.html#DFTBPlusJob)¶
    
A class representing a single computational job with DFTB+. Only supports molecular coordinates, no support for lattice yet.

`get_input`()[[source]](../_modules/scm/plams/interfaces/thirdparty/dftbplus.html#DFTBPlusJob.get_input)¶
    
Transform all contents of `setting.input` branch into string with blocks, keys and values.

Automatic handling of `molecule` can be disabled with `settings.ignore_molecule = True`.

`get_runscript`()[[source]](../_modules/scm/plams/interfaces/thirdparty/dftbplus.html#DFTBPlusJob.get_runscript)¶
    
dftb+ has to be in your $PATH!

`check`()[[source]](../_modules/scm/plams/interfaces/thirdparty/dftbplus.html#DFTBPlusJob.check)¶
    
Returns true if ‘ERROR!’ is not found in the output.

_class _`DFTBPlusResults`(_job_)[[source]](../_modules/scm/plams/interfaces/thirdparty/dftbplus.html#DFTBPlusResults)¶
    
A Class for handling DFTB+ Results.

`get_molecule`()[[source]](../_modules/scm/plams/interfaces/thirdparty/dftbplus.html#DFTBPlusResults.get_molecule)¶
    
Return the molecule from the ‘geo_end.gen’ file. If there is an Error, try to read the ‘geo_end.xyz’ file.

`get_energy`(_string ='Total energy'_, _unit ='au'_)[[source]](../_modules/scm/plams/interfaces/thirdparty/dftbplus.html#DFTBPlusResults.get_energy)¶
    
Return the energy given in the output with the description _string_ , expressed in _unit_. Defaults to `Total energy` and `au`.

`get_atomic_charges`()[[source]](../_modules/scm/plams/interfaces/thirdparty/dftbplus.html#DFTBPlusResults.get_atomic_charges)¶
    
Returns a dictonary with atom numbers and their charges, ordering is the same as in the input.

[Next ](dirac.html "Dirac") [ Previous](crystal.html "Crystal")

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
