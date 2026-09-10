[Free trial](https://www.scm.com/free-trial/)

[ ![Software for Chemistry & Materials](https://www.scm.com/wp-content/themes/scm/images/logos/scm-logo-compact.svg) ![Software for Chemistry & Materials](https://www.scm.com/wp-content/themes/scm/images/logos/scm-logo.svg) ](https://www.scm.com)

  * [Applications](https://www.scm.com/applications/ "Applications")
  * [Products](https://www.scm.com/amsterdam-modeling-suite/ "Products")
  * [Support](https://www.scm.com/support/ "Support")
  * [About us](https://www.scm.com/about-us/ "About us")

[](https://www.scm.com/search.php)Search

[![Logo](../../../../_static/plams_logo.png) ](../../../../index.html)

  * 

Table of contents

  * [General](../../../../general.html)
  * [Introduction](../../../../intro.html)
  * [Getting started](../../../../started.html)
  * [Components overview](../../../../components/components.html)
  * [Interfaces](../../../../interfaces/interfaces.html)
  * [Examples](../../../../examples/examples.html)
  * [Cookbook](../../../../cookbook/cookbook.html)
  * [Citations](../../../../citations.html)

  * [FAQ](../../../../FAQ.html)

__[PLAMS](../../../../index.html)

  * [Documentation](../../../../PLAMS.html/../../Documentation/index.html)/
  * [PLAMS](../../../../index.html)/
  * [Module code](../../../index.html)/
  * scm.plams.tools.plot

# Source code for scm.plams.tools.plot
[code]
    from ..mol.molecule import Molecule
    
    __all__ = ['plot_band_structure', 'plot_molecule']
    
    [[docs]](../../../../components/utils.html#scm.plams.tools.plot.plot_band_structure)def plot_band_structure(x, y_spin_up, y_spin_down=None, labels=None, fermi_energy=None, zero=None, show=False):
        """
        Plots an electronic band structure from DFTB or BAND with matplotlib.
    
        To control the appearance of the plot you need to call ``plt.ylim(bottom, top)``, ``plt.title(title)``, etc. 
        manually outside this function.
    
        x: list of float
            Returned by AMSResults.get_band_structure()
    
        y_spin_up: 2D numpy array of float
            Returned by AMSResults.get_band_structure()
    
        y_spin_down: 2D numpy array of float. If None, the spin down bands are not plotted.
            Returned by AMSResults.get_band_structure()
    
        labels: list of str
            Returned by AMSResults.get_band_structure()
    
        fermi_energy: float
            Returned by AMSResults.get_band_structure(). Should have the same unit as ``y``.
    
        zero: None or float or one of 'fermi', 'vbmax', 'cbmin'
            Shift the curves so that y=0 is at the specified value. If None, no shift is performed. 'fermi', 'vbmax', and 'cbmin' require that the ``fermi_energy`` is not None. Note: 'vbmax' and 'cbmin' calculate the zero as the highest (lowest) eigenvalue smaller (greater) than or equal to ``fermi_energy``. This is NOT necessarily equal to the valence band maximum or conduction band minimum as calculated by the compute engine.
    
        show: bool
            If True, call plt.show() at the end
        """
        import matplotlib.pyplot as plt
        import numpy as np
        if zero is None:
            zero = 0
        elif zero == 'fermi':
            assert fermi_energy is not None
            zero = fermi_energy 
        elif zero in ['vbm', 'vbmax']:
            assert fermi_energy is not None
            zero = y_spin_up[y_spin_up <= fermi_energy].max()
            if y_spin_down is not None:
                zero = max(zero, y_spin_down[y_spin_down <= fermi_energy].max())
        elif zero in ['cbm', 'cbmax']:
            assert fermi_energy is not None
            zero = y_spin_up[y_spin_up >= fermi_energy].min()
            if y_spin_down is not None:
                zero = min(zero, y_spin_down[y_spin_down <= fermi_energy].min())
    
        labels = labels or []
    
        fig, ax = plt.subplots()
    
        plt.plot(x, y_spin_up-zero, '-')
        if y_spin_down is not None:
            plt.plot(x, y_spin_down-zero, '--')
    
        tick_x = []
        tick_labels = []
        for xx, ll in zip(x, labels):
            if ll:
                if len(tick_x) == 0:
                    tick_x.append(xx)
                    tick_labels.append(ll)
                    continue
                if np.isclose(xx, tick_x[-1]):
                    if ll != tick_labels[-1]:
                        tick_labels[-1] += f',{ll}'
                else:
                    tick_x.append(xx)
                    tick_labels.append(ll)
    
        for xx in tick_x:
            plt.axvline(xx)
    
        if fermi_energy is not None:
            plt.axhline(fermi_energy-zero, linestyle='--')
    
        plt.xticks(ticks=tick_x, labels=tick_labels)
    
        if show:
            plt.show()
    
    [[docs]](../../../../components/utils.html#scm.plams.tools.plot.plot_molecule)def plot_molecule(molecule, figsize=None, ax=None, **kwargs):
        """ Show a molecule in a Jupyter notebook """
        from ase.visualize.plot import plot_atoms
        import matplotlib.pyplot as plt
        from ..interfaces.molecule.ase import toASE
    
        if isinstance(molecule, Molecule):
            molecule = toASE(molecule)
    
        if not ax:
            plt.figure(figsize=figsize or (2,2))
    
        plot_atoms(molecule, ax=ax, **kwargs)
    
        if ax:
            ax.axis('off')
        else:
            plt.axis('off')
    
[/code]

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
