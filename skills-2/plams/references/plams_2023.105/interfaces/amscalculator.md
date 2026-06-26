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
      * [AMS driver and engines](ams.html)
      * [AMS worker](amsworker.html)
      * ASE Calculator for AMS
        * Introduction
        * AMS settings
        * AMS standalone and worker mode
        * Technical
        * AMSCalculator API
      * [Quick jobs](quickjobs.html)
      * [Analysis tools: Densf, FCF, analysis](postadf.html)
      * [KF files](kffiles.html)
      * [COSMO-RS](crs.html)
      * [ParAMS](params.html)
      * [Conformers](conformers.html)
      * [Zacros](zacros.html)
      * [ADF (pre-2020 version)](adf.html)
      * [ReaxFF (pre-2019 version)](reaxff.html)
    * [Other programs](thirdparty.html)
  * [Examples](../examples/examples.html)
  * [Cookbook](../cookbook/cookbook.html)
  * [Citations](../citations.html)

  * [FAQ](../FAQ.html)

__[PLAMS](../index.html)

  * [Documentation](../PLAMS.html/../../Documentation/index.html)/
  * [PLAMS](../index.html)/
  * [Interfaces](interfaces.html)/
  * [Amsterdam Modeling Suite](amssuite.html)/
  * ASE Calculator for AMS

# ASE Calculator for AMS¶

## Introduction¶

The `AMSCalculator` class is an ASE Calculator that lets you use any AMS engine (ADF, BAND, DFTB, ReaxFF, MLPotential, ForceField, …) together with ASE.

See also

**Example** : [AMSCalculator: ASE geometry optimizer with AMS forces](../examples/AMSCalculator/ASECalculator.html#asecalculatorexample)

**Engine ASE** : Couple [external ASE calculators](../../ASE/index.html) to the AMS Driver

Technical

Before using an AMSCalculator, you must call the `init()` function from PLAMS. This is done automatically if you use the `plams` binary.

## AMS settings¶

A [`Settings`](../components/settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") object is used to set up the AMS settings in the same way as for normal PLAMS jobs.

See also

[Preparing input for AMS jobs in PLAMS](ams.html#ams-preparing-input)

### ASE results¶

Currently only the energy, forces and stress tensor are provided through the ASE interface. All other results can be accessed through `AMSCalculator.ams_results`, which is an [`AMSResults`](ams.html#scm.plams.interfaces.adfsuite.ams.AMSResults "scm.plams.interfaces.adfsuite.ams.AMSResults") object. Use `AMSCalculator.ensure_property('forces')` and `AMSCalculator.ensure_property('stress')` to ensure these ASE properties are computed regardless of whether it was originally requested in the [`Settings`](../components/settings.html#scm.plams.core.settings.Settings "scm.plams.core.settings.Settings") object.

### Charge¶

There is currently no universal interface in ASE for the total charge of a system and is instead considered to be Calculator specific. The easiest way to set the charge a calculation with the `AMSCalculator` is to define `Atoms.info['charge']`. Additionally, when the charge needs to be treated extensively w.r.t. manipulations of the `Atoms` object in ASE, the initial charge of each atom can also be set. The total charge is thus obtained as `sum(Atoms.get_initial_charges())+Atoms.info['charge']`. See the ASE documentation for details on initial charges and info.

See also

**Example** : [AMSCalculator: Access results files & Charged systems](../examples/AMSCalculator/ChargedAMSCalculator.html#chargedamscalculatorexample)

## AMS standalone and worker mode¶

AMS can run in two modes: standalone and worker.

In **standalone mode** (`amsworker=False`), AMS is started for every new structure, and stores the normal AMS output. Use this mode if:

  * you need to access all results, _or_

  * you run a calculation not supported by the AMSworker (e.g., a PESScan)

In **AMSworker mode** (`amsworker=True`), AMS is only started once. This significantly reduces overhead, especially for fast engines like ReaxFF. The downside is that you cannot access all results. Use this mode if:

  * you only need access to energy, forces, and stress tensor, _and_

  * you only need to run single point calculations, for example to use the `ase.optimize.BFGS` geometry optimizer.

Technical

In **AMSworker mode** , make sure to use `AMSCalculator` as a context manager, or explicitly call `AMSCalculator.stop_worker()` when you want to terminate the AMS process.

## Technical¶

Technical

When creating a deepcopy of `AMSCalculator` the [`AMSWorker`](amsworker.html#scm.plams.interfaces.adfsuite.amsworker.AMSWorker "scm.plams.interfaces.adfsuite.amsworker.AMSWorker") is not copied and instead every copy of `AMSCalculator` has a reference to the same [`AMSWorker`](amsworker.html#scm.plams.interfaces.adfsuite.amsworker.AMSWorker "scm.plams.interfaces.adfsuite.amsworker.AMSWorker").

## AMSCalculator API¶

_class _`AMSCalculator`(_settings =None_, _name =''_, _amsworker =False_, _restart =True_, _molecule =None_, _extractors =[]_)[[source]](../_modules/scm/plams/interfaces/adfsuite/ase_calculator.html#AMSCalculator)¶
    
ASE Calculator which can run any AMS engine (ADF, BAND, DFTB, ReaxFF, MLPotential, ForceField, …).

The settings are specified with a PLAMS `Settings` object in the same way as when running AMS through PLAMS.

Technical

Before initializing the AMSCalculator you need to call `plams.init()`:
[code] 
    from scm.plams import *
    init()
    
[/code]

Parameters:

settingsSettings
    
A Settings object representing the input for an AMSJob or AMSWorker. This also determines which implemented_properties are available: settings.input.ams.properties.gradients: force settings.input.ams.properties.stresstensor: stress

namestr, optional
    
Name of the rundir of calculations done by this calculator. A counter is appended to the name for every calculation.

amsworkerbool , optional
    
If True, use the AMSWorker to set up an interactive session. The AMSWorker will spawn a seperate process (an amsdriver). In order to make sure this process is closed, either use AMSCalculator as a context manager or ensure that AMSCalculator.stop_worker() is called before python is finished:
[code] 
    with AMSCalculator(settings=settings, amsworker=True) as calc:
        atoms.set_calculator(calc)
        atoms.get_potential_energy()
    
[/code]

If False, use AMSJob to set up an io session (a normal AMS calculation storing all output on disk).

restartbool , optional
    
Allow the engine to restart based on previous calculations.

moleculeMolecule , optional
    
A Molecule object for which the calculation has to be performed. If settings.input.ams.system is defined it overrides the molecule argument. If AMSCalculator.calculate(atoms = atoms) is called with an atoms argument it overrides any earlier definition of the system and remembers it.

extractors: List[BasePropertyExtractor] , optional
    
Define extractors for additional properties.

Examples:

_static _`__new__`(_cls_ , _settings =None_, _name =''_, _amsworker =False_, _restart =True_, _molecule =None_, _extractors =[]_)[[source]](../_modules/scm/plams/interfaces/adfsuite/ase_calculator.html#AMSCalculator.__new__)¶
    
Dispatch object creation to AMSPipeCalculator or AMSJobCalculator depending on [`AMSWorker`](amsworker.html#scm.plams.interfaces.adfsuite.amsworker.AMSWorker "scm.plams.interfaces.adfsuite.amsworker.AMSWorker")

_property _`implemented_properties`¶
    
Returns the list of properties that this calculator has implemented

`calculate`(_atoms =None_, _properties =['energy']_, _system_changes =['positions', 'numbers', 'cell', 'pbc', 'initial_charges', 'initial_magmoms']_)[[source]](../_modules/scm/plams/interfaces/adfsuite/ase_calculator.html#AMSCalculator.calculate)¶
    
Calculate the requested properties. If atoms is not set, it will reuse the last known Atoms object.

`ensure_property`(_properties_)[[source]](../_modules/scm/plams/interfaces/adfsuite/ase_calculator.html#AMSCalculator.ensure_property)¶
    
A list of ASE properties that the calculator will ensure are available from AMS or it gives an error.

`stop_worker`()[[source]](../_modules/scm/plams/interfaces/adfsuite/ase_calculator.html#AMSCalculator.stop_worker)¶
    
Stops the amsworker if it exists

`clean_exit`()[[source]](../_modules/scm/plams/interfaces/adfsuite/ase_calculator.html#AMSCalculator.clean_exit)¶
    
Function called by ASEPipeWorker to tell the Calculator to stop and clean up

[Next ](quickjobs.html "Quick jobs") [ Previous](amsworker.html "AMS worker")

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
