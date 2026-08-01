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
  * [Components overview](components.html)
    * [Settings](settings.html)
    * [Jobs](jobs.html)
    * [Results](results.html)
    * [Job runners](runners.html)
    * [Job manager](jobmanager.html)
    * [Public functions](functions.html)
    * [Molecule](molecule.html)
    * [Utilities](utils.html)
    * [Trajectories](trajectories.html)
      * [XYZ trajectory files](xyz.html)
      * [RKF trajectory files](rkf.html)
      * [DCD trajectory files](dcd.html)
      * Trajectory class
  * [Interfaces](../interfaces/interfaces.html)
  * [Examples](../examples/examples.html)
  * [Cookbook](../cookbook/cookbook.html)
  * [Citations](../citations.html)

  * [FAQ](../FAQ.html)

__[PLAMS](../index.html)

  * [Documentation](../PLAMS.html/../../Documentation/index.html)/
  * [PLAMS](../index.html)/
  * [Components overview](components.html)/
  * [Trajectories](trajectories.html)/
  * Trajectory class

# Trajectory class¶

This subsection describes the API of the `Trajectory` class. While the [`RKFTrajectoryFile`](rkf.html#scm.plams.trajectories.rkffile.RKFTrajectoryFile "scm.plams.trajectories.rkffile.RKFTrajectoryFile") clearly represents a file, the `Trajectory` is set up to represent the trajectory itself. It behave like a list of [`Molecule`](mol_api.html#scm.plams.mol.molecule.Molecule "scm.plams.mol.molecule.Molecule") objects, while keeping the memory requirements to a minimum. A `Trajectory` object can be associated with a single RKF file, or with multiple RKF files. In the latter case, the frames will be concatenated.

_class _`Trajectory`(_filenames_)[[source]](../_modules/scm/plams/trajectories/trajectory.html#Trajectory)¶
    
Class representing an AMS trajectory

It creates molecule objects along the trajectory in a list-like fashion. It can also perform analysis tasks.

Basic use of the `Trajectory` class works as follows:
[code] 
    >>> from scm.plams import Trajectory
    
[/code]
[code] 
    >>> trajec = Trajectory('ams.rkf')
    >>> nsteps = len(trajec)
    
[/code]
[code] 
    >>> mol100 = trajec[100]
    >>> for i,mol in enumerate(trajec):
    ...     if i == 100:
    ...         print (mol is mol100)
    ...
    True
    
[/code]

As with a regular list, accessing the same element twice yields the same instance of the molecule.

A trajectory may consist of multiple RKF files, for instance after a restarted MD run.
[code] 
    >>> trajec = Trajectory(['md1.results/ams.rkf','md2.results/ams.rkf'])
    >>> nsteps = len(trajec)
    >>> print ('NSteps in each file: ',trajec.lengths)
    NSteps in each file:  [181, 19]
    
[/code]

Otherwise the object behaves the same, and iteration occurs over the concatenated files.

Note

It is possible to change the molecule objects once they are loaded, but this will not change the underlying files. When the altered molecule objects have been garbage collected, and the same frame is read anew, this frame will have the original molecule attributes.
[code] 
    >>> import gc
    >>> from scm.plams import Trajectory
    
[/code]
[code] 
    >>> trajec = Trajectory('ams.rkf')
    >>> mol = trajec[100]
    >>> print (mol.properties.charge)
    0.0
    >>> mol.properties.charge = 10000.
    >>> print (trajec[100].properties.charge)
    1000.0
    
[/code]
[code] 
    >>> # remove the reference
    >>> mol = None
    >>> gc.collect()
    >>> print (trajec[100].properties.charge)
    0.
    
[/code]

The `Trajectory` object can also be used to perform analysis, using [`AMSAnalysisJob`](../interfaces/postadf.html#scm.plams.interfaces.adfsuite.amsanalysis.AMSAnalysisJob "scm.plams.interfaces.adfsuite.amsanalysis.AMSAnalysisJob") behind the scenes.
[code] 
    >>> from scm.plams import Settings, Trajectory
    >>> from scm.plams import init, finish
    
[/code]
[code] 
    >>> trajec = Trajectory('ams.rkf')
    
[/code]
[code] 
    >>> # Define the type of analysis
    >>> settings = Settings()
    >>> settings.input.Task = 'RadialDistribution'
    >>> settings.input.RadialDistribution.AtomsFrom.Element = ['O']
    >>> settings.input.RadialDistribution.AtomsTo.Element = ['O']
    
[/code]
[code] 
    >>> # Run the analysis
    >>> init()
    >>> plots = trajec.run_analysis(settings)
    >>> finish()
    
[/code]
[code] 
    >>> # Store the plot in human readable format
    >>> for plot in plots :
    ...     plot.write('%s'%(plot.name+'.txt'))
    
[/code]

This results in a text file named RadialDistribution_1.txt, which contains data organized in columns.

`run_analysis`(_settings_ , _steprange =None_)[[source]](../_modules/scm/plams/trajectories/trajectory.html#Trajectory.run_analysis)¶
    
Calls the AMS analysis tool behind the scenes

  * `settings` – PLAMS Settings object Example :
[code] >>> settings = Settings()
        >>> settings.input.Task = 'AutoCorrelation' 
        >>> settings.input.AutoCorrelation.Property = 'Velocities'
        >>> settings.input.AutoCorrelation.MaxFrame = 2000
        
[/code]

  * `steprange` – Start frame, end frame, and stepsize. The default (None) corresponds to all frames in the object

Returns a list of AMSAnalysisPlot objects. Main attributes of the AMSAnalysisPlot objects are :

  * `name` – The name of the plot

  * `x` – A list of lists containing the values of the coordinate system If the coordinate system is 1D, then it is a list containing a single list of values x = [[x1,x2,x3,x4,…,xn]]

  * `y` – A list containing the function values

  * `write()` – A method returning a string containing all plot info

[Next ](../interfaces/interfaces.html "Interfaces") [ Previous](dcd.html "DCD trajectory files")

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
