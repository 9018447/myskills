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
      * [Packmol example](PackMolExample/PackMolExample.html)
      * [Engine ASE: AMS geometry optimizer with forces from any ASE calculator](CustomASECalculator.html)
      * [AMSCalculator: ASE geometry optimizer with AMS forces](AMSCalculator/ASECalculator.html)
      * [AMSCalculator: Access results files & Charged systems](AMSCalculator/ChargedAMSCalculator.html)
      * i-PI path integral MD with AMS
      * [Sella transition state search with AMS](SellaTransitionStateSearch.html)
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
  * i-PI path integral MD with AMS

# i-PI path integral MD with AMS¶

**Note** : This example requires AMS2023 or later.

This example shows how to couple the [i-PI](http://ipi-code.org) code to AMS using the AMS [ASE calculator](AMSCalculator/ASECalculator.html#asecalculatorexample).

i-PI can be used to run for example path integral molecular dynamics. The example shows how to run thermostatted ring polymer molecular dynamics for a water molecule together with the UFF force field.

For more information about i-PI, refer to the i-PI documentation and examples.

The below example only runs on Linux as it uses a unix socket.

Technical

i-PI is not included with AMS and is not supported by SCM.

**Example usage:** ([`Download run-ase.py`](../_downloads/be6bb934f86c4564b87ad6385f8ca859/run-ase.py) and auxiliary files [`input.xml`](../_downloads/d5f2457b1e471bc4ad431e29eed5bfcd/input.xml), [`firstframe.xyz`](../_downloads/fe1f4b37232baa33a7d4ebd1dca18909/firstframe.xyz), [`run-server.sh`](../_downloads/a6bd5a884ccaa11d5238f44f0acf4a15/run-server.sh))
[code] 
    #!/usr/bin/env amspython
    from ase.calculators.socketio import SocketClient
    from ase.io import read
    from scm.plams import Settings, finish, init
    from scm.plams.interfaces.adfsuite.ase_calculator import AMSCalculator
    
    """
    Example illustrating how to use AMS as a client together with i-PI.
    
    The i-PI configuration in input.xml sets up a short ring-polymer molecular
    dynamics (RPMD) simulation. 
    
    The connection between server and client is of type 'unixsocket' (a file in
    /tmp). This example will only run on Linux.
    
    The settings below set up AMS to use the UFF force field to calculate the
    energy, forces, and stress tensor of whatever system the i-PI server requests
    and return them to i-PI.
    
    AMS is run in "AMSWorker" mode (interactive mode), which means that AMS does
    **not** shut down and start up again between calculations.
    
    To run this example, 
    
    * modify run-server.sh to provide the correct path to the i-pi executable,
    * sh run-server.sh
    * In a different terminal: $AMSBIN/amspython run-ase.py
    """
    
    def main():
        init()
    
        use_stress = False
        atoms = read('firstframe.xyz')
    
        sett = Settings()
        sett.input.ams.Task = 'SinglePoint'
        sett.input.ams.Properties.Gradients = 'True'
        sett.input.ams.Properties.StressTensor = str(use_stress)
        sett.input.forcefield.type = 'UFF'
        sett.runscript.nproc = 1
    
        with AMSCalculator(settings=sett, amsworker=True) as calc:
            atoms.set_calculator(calc)
            client = SocketClient(unixsocket='driver-irpmd-16') # socket should match the one given in input.xml
            client.run(atoms, use_stress=use_stress)
    
        finish()
    
    if __name__ == '__main__':
        main()
    
[/code]

[Next ](SellaTransitionStateSearch.html "Sella transition state search with AMS") [ Previous](AMSCalculator/ChargedAMSCalculator.html "AMSCalculator: Access results files & Charged systems")

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
