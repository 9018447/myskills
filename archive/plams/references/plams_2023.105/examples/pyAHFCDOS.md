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
      * [AMS Molecular Dynamics PLAMS jobs](MDJobs.html)
      * [ADF fragment job](adffragment.html)
      * [Reorganization Energy](ReorganizationEnergy.html)
      * [NBO with ADF](adfnbo.html)
      * [Numerical gradients](numgrad.html)
      * [Numerical Hessian](numhess.html)
      * [Global Minimum Search](global_minimum.html)
      * Vibronic Density of States using the AH-FC method
      * [Vibronic Density of States with ADF](fcf_dos.html)
  * [Cookbook](../cookbook/cookbook.html)
  * [Citations](../citations.html)

  * [FAQ](../FAQ.html)

__[PLAMS](../index.html)

  * [Documentation](../PLAMS.html/../../Documentation/index.html)/
  * [PLAMS](../index.html)/
  * [Examples](examples.html)/
  * Vibronic Density of States using the AH-FC method

# Vibronic Density of States using the AH-FC method¶

The `FCFDOS` class allows one to easily calculate the density of states for an energy or charge transfer at the AH-FC level of theory by combining the results from two vibronic spectra calculations.

For an example, see [Vibronic Density of States with ADF](fcf_dos.html#fcf-dos).
[code] 
    #from .scmjob import SCMJob, SCMResults
    import os, numpy, math
    from scm.plams import KFFile
    
    __all__ = ['FCFDOS']
    
    class FCFDOS:
        """
        A class for calculating the convolution of two FCF spectra
        """
    
        # Conversion factor to cm-1 == ( me^2 * c * alpha^2 ) / ( 100 * 2pi * amu * hbar )
        G2F = 120.399494933
        #J2Ha = 1.0 / (scipy.constants.m_e * scipy.constants.speed_of_light**2 * 0.0072973525693**2)
        J2Ha = 2.293712278400752e+17
    
        def __init__(self, absrkf, emirkf, absele=0.0, emiele=0.0):
            """
            absrkf : KFFile from an FCF absorption calculation for the acceptor, as name, path, or KFFile object
            emirkf : KFFile from an FCF emission calculation for the donor, as name, path, or KFFile object
            absele : Acceptor absorption electronic energy cm-1
            emiele : Donor emission electronic energy in cm-1
            """
            if isinstance(absrkf, str):
                self.absrkf = KFFile(absrkf)
            else:
                self.absrkf = absrkf
            if isinstance(emirkf, str):
                self.emirkf = KFFile(emirkf)
            else:
                self.emirkf = emirkf
            self.absele = absele
            self.emiele = emiele
            self.spc    = None
    
        def _getstick(self, source):
            spclen = source.read('Fcf', 'nspectrum')
            rawspc = source.read('Fcf', 'spectrum')
            stick = numpy.reshape(numpy.array(rawspc), (2, spclen)).transpose()
            # Reorder spectrum if decreasing
            if stick[0, 0] > stick[-1, 0]:
                for ix in range(numpy.size(stick, 0) // 2):
                    XX = numpy.copy(stick[ix, :])
                    stick[ix, :] = stick[-ix-1, :]
                    stick[-ix-1, :] = XX
            # Get frequencies in cm-1
            frq1 = numpy.array(source.read('Fcf', 'gamma1')) * self.G2F
            frq2 = numpy.array(source.read('Fcf', 'gamma2')) * self.G2F
            # Calculate energy in Joules
            #factor = scipy.constants.pi * scipy.constants.hbar * scipy.constants.speed_of_light * 100.0
            factor = 9.932229285744643e-24
            viben1 = sum(frq1) * factor
            viben2 = sum(frq2) * factor
            # Convert to Hartree
            viben1 = viben1 * self.J2Ha
            viben2 = viben2 * self.J2Ha
            # Add ZPE and electronic energy
            stick[:, 0] = stick[:, 0] + viben2 - viben1 + self.absele + self.emiele
            return stick
    
        def _spcinit(self):
            # Get absorption and emission spectra
            absspc = self._getstick(self.absrkf)
            emispc = self._getstick(self.emirkf)
            # Find spectrum bounds
            absmin = numpy.amin(absspc[:,0])
            absmax = numpy.amax(absspc[:,0])
            emimin = numpy.amin(emispc[:,0])
            emimax = numpy.amax(emispc[:,0])
            spcmin = min(absmin, emimin)
            spcmax = max(absmax, emimax)
            # Find spectrum length and grain
            absdlt = abs(absspc[0, 0] - absspc[1, 0])
            emidlt = abs(absspc[0, 0] - absspc[1, 0])
            spcgrn = min(absdlt, emidlt)
            spclen = math.floor( (spcmax - spcmin) / spcgrn ) + 1
            # Initialize spectrum
            spc = numpy.zeros((spclen, 2), dtype=float)
            self.spc = self.newspc(spcmin, spcmax, spclen)
            return None
    
        def dos(self, lineshape = 'GAU', HWHM = 100.0):
            """
            Calculate density of states by computing the overlap of the two FCF spectra
            The two spectra are broadened using the chosen lineshape and Half-Width at Half-Maximum in cm-1
            """
            # Initialize spectrum
            self._spcinit()
            # Get stick spectra
            absstick = self._getstick(self.absrkf)
            emistick = self._getstick(self.emirkf)
            # Convolute with gaussians
            absspc = numpy.copy(self.spc)
            emispc = numpy.copy(self.spc)
            absspc = self.convolute(absspc, absstick, lineshape, HWHM)
            emispc = self.convolute(emispc, emistick, lineshape, HWHM)
            # Integrate
            absint = self.trapezoid(absspc)
            emiint = self.trapezoid(emispc)
            # Calculate DOS
            self.spc[:, 1] = absspc[:, 1] * emispc[:, 1]
            dos = self.trapezoid(self.spc)
            return dos
    
        def newspc(self, spcmin, spcmax, spclen=1000):
            # Dimensions of the spectrum
            delta = ( spcmax - spcmin ) / ( spclen - 1 )
            spc = numpy.zeros((spclen, 2), dtype=float)
            for ix in range(spclen):
                spc[ix, 0] = spcmin + delta*ix
            return spc
    
        def convolute(self, spc, stick, lineshape = None, HWHM = None):
            """
            Convolute stick spectrum with the chosen width and lineshape
            lineshape : Can be Gaussian or Lorentzian
            HWHM      : expressed in cm-1
            """
            if HWHM is None:
                raise ValueError('HWHM not defined')
            if lineshape is None:
                raise ValueError('Lineshape not defined')
            # Data for the convolution
            delta = spc[1, 0] - spc[0, 0]
            if  lineshape[0:3].upper() == 'GAU':
                # Gaussian lineshape
                idline = 1
                # This includes the Gaussian prefactor and the factor to account for the reduced lineshape width
                #factor = 1. / scipy.special.erf(2*math.sqrt(math.log(2)))
                factor = 1.0188815852036244
                factA = math.sqrt(numpy.log(2.0)/math.pi) * factor / HWHM
                factB = -numpy.log(2.0) / HWHM**2
                # We only convolute between -2HWHM and +2HWHM which accounts for 98.1% of the area
                ishft = math.floor( 2 * HWHM / delta )
            elif lineshape[0:3].upper() == 'LOR':
                # Lorentzian lineshape
                idline = 2
                # This includes the Lorentzian prefactor and the factor to account for the reduced lineshape width
                factA = ( math.pi / math.atan(12) / 2 ) * HWHM / math.pi
                factB = 0.0
                # We only convolute between -12HWHM and +12HWHM which accounts for 94.7% of the area
                ishft = math.floor( 12 * HWHM / delta )
            else:
                raise ValueError('invalid lineshape')
            # Loop over peaks in the stick spectrum
            spclen = numpy.size(spc, 0)
            for ix in range(numpy.size(stick[:, 0])):
                # Find peak position in the convoluted spectrum
                peakpos = 1 + math.floor( (stick[ix, 0] - spc[0, 0]) / delta )
                # Convolution interval, limited to save computational time
                i1 = max(peakpos - ishft, 1)
                i2 = min(peakpos + ishft, spclen)
                factor = factA * stick[ix, 1]
                if   idline == 1: # Gaussian
                    for i in range(i1, i2):
                       spc[i, 1] = spc[i, 1] + factor * math.exp(factB * (spc[i, 0] - stick[ix, 0])**2)
                elif idline == 2: # Lorentzian
                    for i in range(i1, i2):
                       spc[i, 1] = spc[i, 1] + factor / ( HWHM + (spc[i, 0] - stick[ix, 0])**2 )
            return spc
        
        def trapezoid(self, spc):
            """
            Integrate spectrum using the trapezoid rule
            """
            value = ( spc[0, 1] + spc[-1, 1] ) / 2
            value = value + sum(spc[1:-1, 1])
            # The abscissas must be equally spaced for this to work
            value = value * ( spc[1, 0] - spc[0, 0] )
            return value
    
        def __str__(self):
            string = f"Absorption from {self.absrkf.path}\nEmission from {self.emirkf.path}\nAcceptor absorption electronic energy = {self.absele} cm-1\nDonor emission electronic energy = {self.emiele} cm-1"
            return string
    
[/code]

[Next ](fcf_dos.html "Vibronic Density of States with ADF") [ Previous](global_minimum.html "Global Minimum Search")

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
