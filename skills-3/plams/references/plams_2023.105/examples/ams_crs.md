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
      * [Property Prediction](PropertyPrediction/PropertyPrediction.html)
      * ADF and COSMO-RS workflow
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
  * ADF and COSMO-RS workflow

# ADF and COSMO-RS workflow¶

**Note** : This example requires AMS2023 or later.

This example uses ADF to generate the .coskf file for benzene. You can also modify it to instead use the Benzene.coskf from the ADFCRS-2018 database. Note that you first need to install the ADFCRS-2018 database.

The script then plots the sigma profile. This is not a necessary step but is done for illustration purposes only.

Then a solubility calculation is performed for benzene in water between 0 and 10 degrees C. The melting point and enthalpy of fusion can either be estimated using the property prediction tool, or the experimental numbers can be given (recommended).

**Example usage** : ([`ams_crs.py`](../_downloads/eefdfb91c59a673c27b5c2e9ff48d999/ams_crs.py))
[code] 
    #!/usr/bin/env amspython
    from scm.plams import *
    import numpy as np
    import os
    import matplotlib.pyplot as plt
    
    def solubility():
        # database can also be replaced with the output of "$AMSBIN/amspackages loc adfcrs" /ADFCRS-2018
        database = CRSJob.database()
        
        solute_smiles = 'c1ccccc1'
        solute_coskf = generate_coskf(solute_smiles, 'adf_benzene') # generate files with ADF 
        #solute_coskf = os.path.abspath('plams_workdir/adf_benzene/adf_benzene.coskf') # to not rerun the ADF calculation
        #solute_coskf = os.path.join(database, 'Benzene.coskf') # to load from database
    
        # You can also estimate the solute properties with the Property Prediction tool. See the Property Prediction example
        solute_properties = { 'meltingpoint': 278.7, 'hfusion': 9.91  } #experimental values for benzene, hfusion in kJ/mol
    
        solvent_coskf = os.path.join(database, 'Water.coskf')
        solvent_density = 1.0
    
        s = Settings()
        s.input.property._h = 'solubility'
        s.input.property.DensitySolvent = solvent_density
        s.input.temperature = "273.15 283.15 10"
        s.input.pressure = "1.01325 1.01325 10"
    
        s.input.compound = [Settings(), Settings()]
    
        s.input.compound[0]._h = solvent_coskf
        s.input.compound[0].frac1 = 1.0
    
        s.input.compound[1]._h = solute_coskf
        s.input.compound[1].meltingpoint = solute_properties['meltingpoint']
        s.input.compound[1].hfusion = solute_properties['hfusion'] * Units.convert(1.0, 'kJ/mol', 'kcal/mol') # convert from kJ/mol to kcal/mol
    
        job = CRSJob(name='benzene_in_water', settings=s)
        job.run()
    
        plot_results(job)
    
    def generate_coskf(smiles, jobname=None):
        molecule = from_smiles(smiles, nconfs=100, forcefield='uff')[0]
        job = ADFCOSMORSCompoundJob(name=jobname, molecule=molecule)
        job.run()
        plot_sigma_profile(job)
        return job.results.coskfpath()
    
    def plot_results(job):
        res = job.results.get_results('SOLUBILITY')
        solubility_g_L = res['solubility g_per_L_solvent'][1]
        temperatures = res['temperature']
        for temperature, sol_g_l in zip(temperatures, solubility_g_L):
            print(f'{temperature:.2f} {sol_g_l:.4f}')
    
        plt.plot(temperatures, solubility_g_L)
        plt.xlabel("Temperature (K)")
        plt.ylabel("Solubility (g/L solvent)")
        plt.show()
    
    def plot_sigma_profile(job):
        sigma = job.results.get_sigma_profile()
        xlabel = 'σ (e/A**2)'
        for profile in sigma:
            if profile == xlabel:
                continue
            plt.plot(sigma[xlabel], sigma[profile], label=profile.split('.')[0])
    
        plt.xlabel('σ (e/Å**2)')
        plt.ylabel('p(σ)')
        plt.legend()
        plt.show()
    
    def main():
        solubility()
    
    if __name__ == '__main__':
        init()
        main()
        finish()
    
[/code]

[Next ](PackMolExample/PackMolExample.html "Packmol example") [ Previous](PropertyPrediction/PropertyPrediction.html "Property Prediction")

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
