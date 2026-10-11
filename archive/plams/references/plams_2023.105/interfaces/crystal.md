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
      * Crystal
        * Preparing a calculation
        * Molecule parsing
        * Results extraction
        * Example
        * API
      * [DFTB+](dftbplus.html)
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
  * Crystal

# Crystal¶

(_contributed by_ [Patrick Melix](https://www.researchgate.net/profile/Patrick_Melix))

More information about CRYSTAL can be found on its [official website](http://www.crystal.unito.it).

PLAMS offers a simple CRYSTAL interface which does not offer access to all possible input types of CRYSTAL just most. CRYSTAL14 was used by the developer, but as far as the developer can tell the new input features from CRYSTAL17 can be achieved with this interface. Older CRYSTAL versions are more restrictive with the input, so they have not been tested. The relevant classes are `CrystalJob` and [`Results`](../components/results.html#scm.plams.core.results.Results "scm.plams.core.results.Results").

## Preparing a calculation¶

Preparing an instance of `CrystalJob` follows the general principles for [`SingleJob`](../components/jobs.html#scm.plams.core.basejob.SingleJob "scm.plams.core.basejob.SingleJob"). Information adjusting the input file is stored in the `myjob.settings.input` branch. The geometry of your system can be supplied via the class [`Molecule`](../components/mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") and will be parsed into a `fort.34` file using the _EXTERNAL_ keyword (only if you have [ASE](https://wiki.fysik.dtu.dk/ase/index.html) installed). It can also be supplied to the `myjob.settings.input` branch by using the function `mol2CrystalConf` to create a CRYSTAL-type input of your structure inside the input file (set `myjob.settings.ignore_molecule = True`). Consult [the manual](http://http://www.crystal.unito.it/documentation.php) for further information on the different input options of CRYSTAL.

### Input¶

Settings must contain at least (case insensitive):

  * one geometry key (‘CRYSTAL’,’SLAB’,’POLYMER’,’HELIX’,’MOLECULE’,’EXTERNAL’,’DLVINPUT’), if the [`Molecule`](../components/mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") parser of `CrystalJob` is used the ‘EXTERNAL’ keyword is added automatically. For using `mol2CrystalConf`, see below).

  * one basis key (‘BASISSET’)

  * one option_key (‘options’ and anything else)

The ordering inside the geometry-, basis- and option-block can be controlled:
[code] 
    settings.input.basisset._h = 'top line'
    settings.input.basisset._1 = 'first line'
    settings.input.basisset._2 = 'second line'
    
[/code]

and so on. Note that you can also pass lists to the ordered version. Every item will end up in one line.

To make input nicer, the ‘options’ key will never be printed, since the input does not allow an opening statement for this block. This way you can use:
[code] 
    settings.input.options.bla = 'bla'
    settings.input.options.test = ''
    settings.input.options._h = 'FIRST'
    
[/code]

without the ‘options’ beeing printed, but the section will still be closed with an ‘END’.

### Runscript¶

The command `crystal` should point to the crystal binary or a runscript (so make sure it is in your `$PATH`), that the input can be piped to. Modify `CrystalJob._command` if necessary. PLAMS will not clean up the mess of files that crystal produces. If you want that, your runscript should do it for you. Standard output is written to `$JN.out`.

## Molecule parsing¶

The [`Molecule`](../components/mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") parser of `CrystalJob` makes use of the `EXTERNAL` keyword by writing the [`Molecule`](../components/mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") instance to the file _fort.34_. This is done using the `write_crystal` method from ASE.

If you do not have ASE installed you cannot use this feature. In this case use the function `mol2CrystalConf` to create a list to pass to `myjob.settings.input.<geomKey>`. Remember to set `myjob.settings.ignore_molecule = True` if you are doing this.

## Results extraction¶

There is no special results extraction yet, use the standard methods from the [`Results`](../components/results.html#scm.plams.core.results.Results "scm.plams.core.results.Results") class.

## Example¶
[code] 
    mol = Molecule('test.xyz')
    common = Settings()
    geom = ['0 0 0',
    '194',
    '2.456 6.696',
    '2',
    '6 0.0     0.0     0.25',
    '6 0.333333  0.666667  0.75',
    'SLAB',
    '0 0 1',
    '1 1',
    'OPTGEOM',
    'FULLOPTG',
    'ENDGEOM']
    
    common.input.basisset = 'STO-3G'
    common.input.options.shrink = '9 18'
    common.input.options.scfdir = ''
    common.input.options._h = 'RHF'
    common.input.options.dft.exchange = 'PBE'
    common.input.options.dft.correlat = 'PBE'
    common.input.options.maxcycle = 250
    common.input.options.fmixing = 90
    #common.input.options.test = True
    
    common.input.crystal = geom
    common.ignore_molecule = True
    
    #alternative 1
    #common.input.crystal = mol2CrystalConf(mol)
    #common.ignore_molecule = True
    
    #alternative 2
    #just pass the molecule to CrystalJob if you have ASE
    
    job = CrystalJob(name='crystaltest', settings=common, molecule=mol)
    jobres = job.run()
    
[/code]

## API¶

_class _`CrystalJob`(_name ='plamsjob'_, _settings =None_, _depend =None_)[[source]](../_modules/scm/plams/interfaces/thirdparty/crystal.html#CrystalJob)¶
    
A class representing a single computational job with CRYSTAL <https://www.crystal.unito.it/> Use Crystal version >= 14, lower versions have an even stricter and more complicated input.

`get_input`()[[source]](../_modules/scm/plams/interfaces/thirdparty/crystal.html#CrystalJob.get_input)¶
    
Transform all contents of `input` branch of `settings` into string.

`get_runscript`()[[source]](../_modules/scm/plams/interfaces/thirdparty/crystal.html#CrystalJob.get_runscript)¶
    
Run Crystal.

`check`()[[source]](../_modules/scm/plams/interfaces/thirdparty/crystal.html#CrystalJob.check)¶
    
Look for the normal termination signal in output. Note, that does not mean your calculation was successful!

`mol2CrystalConf`(_molecule_)[[source]](../_modules/scm/plams/interfaces/thirdparty/crystal.html#mol2CrystalConf)¶
    
Call this function to create a CRYSTAL-type input of your structure:

Returns a given [`Molecule`](../components/mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") object as a geomkey and a list of strings that can be used to create a Settings instance for Crystal.
[code] 
    >>> print(crystalMol2Conf(mol))
    'GEOMKEY', ['0 0 0', '1', 'lattice', 'nAtoms', 'ElementNumber1 X1 Y1 Z1','ElementNumber2 X2 Y2 Z2', ...]
    
[/code]

  * IFLAG,IFHR and IFSO are returned as 0,0,0 by default with Symmetry group P1 (number 1). This should allow most calculations to run. The user needs to change them if he wants to take advantage of symmetry.

  * The geometry key is guessed from the number of lattice vectors. For special stuff change it by hand.

  * The number of lattice vectors in the given molecule should correspond to the dimensionality of the system. Do not fill them with zeros or unit vectors, this will result in a 3D-Periodic system with wrong fractional coordinates. So stick with the standard PLAMS way of doing things.

[Next ](dftbplus.html "DFTB+") [ Previous](cp2k.html "CP2K")

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
