[Free trial](https://www.scm.com/free-trial/)

[ ![Software for Chemistry & Materials](https://www.scm.com/wp-content/themes/scm/images/logos/scm-logo-compact.svg) ![Software for Chemistry & Materials](https://www.scm.com/wp-content/themes/scm/images/logos/scm-logo.svg) ](https://www.scm.com)

  * [Applications](https://www.scm.com/applications/ "Applications")
  * [Products](https://www.scm.com/amsterdam-modeling-suite/ "Products")
  * [Support](https://www.scm.com/support/ "Support")
  * [About us](https://www.scm.com/about-us/ "About us")

[](https://www.scm.com/search.php)Search

[![Logo](../../../../../_static/plams_logo.png) ](../../../../../index.html)

  * 

Table of contents

  * [General](../../../../../general.html)
  * [Introduction](../../../../../intro.html)
  * [Getting started](../../../../../started.html)
  * [Components overview](../../../../../components/components.html)
  * [Interfaces](../../../../../interfaces/interfaces.html)
  * [Examples](../../../../../examples/examples.html)
  * [Cookbook](../../../../../cookbook/cookbook.html)
  * [Citations](../../../../../citations.html)

  * [FAQ](../../../../../FAQ.html)

__[PLAMS](../../../../../index.html)

  * [Documentation](../../../../../PLAMS.html/../../Documentation/index.html)/
  * [PLAMS](../../../../../index.html)/
  * [Module code](../../../../index.html)/
  * scm.plams.interfaces.adfsuite.mopac

# Source code for scm.plams.interfaces.adfsuite.mopac
[code]
    from ...core.basejob import SingleJob
    from .scmjob import SCMResults
    
    __all__ = ['MOPACJob', 'MOPACResults']
    
    [[docs]](../../../../../interfaces/mopac.html#scm.plams.interfaces.adfsuite.mopac.MOPACResults)class MOPACResults(SCMResults):
        """A class for results of computation done with MOPAC.
    
        This class inherits all methods from |SCMResults|.
    
        .. technical::
    
            In case of a MOPAC job, preparation is much different from other programs of AMSuite, but the result handling is quite similar due to presence of KF files. Therefore |MOPACResults| is a subclass of |SCMResults|, but |MOPACJob| is not a subclass of |SCMJob|.
        """
        _rename_map = {'results.rkf':'$JN.rkf', '$JN.in.aux':'$JN.aux', '$JN.in.arc':'$JN.arc', '$JN.in.out':'$JN.out' }
        _kfext = '.rkf'
    
        def _int2inp(self):
            return list(range(1, 1+len(self.job.molecule)))
    
    [[docs]](../../../../../interfaces/mopac.html#scm.plams.interfaces.adfsuite.mopac.MOPACResults._atomic_numbers_input_order)    def _atomic_numbers_input_order(self):
            return self.readkf('Molecule', 'AtomicNumbers')
    
    [[docs]](../../../../../interfaces/mopac.html#scm.plams.interfaces.adfsuite.mopac.MOPACJob)class MOPACJob(SingleJob):
        """A class representing a single computational job with MOPAC."""
        _result_type = MOPACResults
        _command = 'MOPAC2016-SCM.exe'
    
    [[docs]](../../../../../interfaces/mopac.html#scm.plams.interfaces.adfsuite.mopac.MOPACJob.get_input)    def get_input(self):
            """Transform the contents of ``input`` branch of ``settings`` into the first line of MOPAC input. Print the molecular coordinates together with frozen coordinate flags."""
            aux = self.settings.input.find_case('aux')
            if aux not in self.settings.input:
                self.settings.input[aux] = [0,'PRECISION=9']
    
            keylist = []
            for key, value in self.settings.input.items():
                if value is True:
                    keylist.append(key)
                elif isinstance(value, tuple):
                    keylist.append(key + '=(' + ','.join(map(str, value)) + ')' )
                elif isinstance(value, list):
                    keylist.append(key + '(' + ','.join(map(str, value)) + ')' )
                else:
                    keylist.append(key + '=' + str(value))
            ret = ' '.join(keylist) + '\n\n\n'
    
            for at in self.molecule:
                line = '{:7}'.format(at.symbol)
                for c in ['x', 'y', 'z']:
                    num = at.__getattribute__(c)
                    frz = 0 if ('mopac_freeze' in at.properties and c in at.properties.mopac_freeze) else 1
                    line += ' {: 11.8f} {:d}'.format(num,frz)
                ret += line + '\n'
            return ret
    
    [[docs]](../../../../../interfaces/mopac.html#scm.plams.interfaces.adfsuite.mopac.MOPACJob.get_runscript)    def get_runscript(self):
            """Generate a MOPAC runscript.
    
            The name of the MOPAC executable is taken from class attribute ``MOPACJob._command``. If you experience problems running MOPAC, check if that value corresponds to the name of the executable and this executable is visible in your ``$PATH`` (in case of AMSuite it's in ``$AMSBIN``). Note that a bare MOPAC executable should be used here, please avoid using any wrappers.
    
            The execution of MOPAC binary is followed by calling a simple command line tool ``tokf`` which reads various output text files produced by MOPAC and collects all the data in a binary KF file. See :ref:`kf-files` for details.
            """
            ret = self._command + ' ' + self._filename('inp')
            if self.settings.runscript.stdout_redirect:
                ret += ' >'+self._filename('out')
            ret += '\n\n'
            ret += 'cp {} {}.stdout\n'.format(self._filename('err'), self._filename('inp'))
            ret += 'tokf mopac {} {}.rkf\n'.format(self._filename('inp'), self.name)
            ret += 'rm {}.stdout\n\n'.format(self._filename('inp'))
            ret += 'rm {}\n\n'.format(self._filename('out'))
            return ret
    
    [[docs]](../../../../../interfaces/mopac.html#scm.plams.interfaces.adfsuite.mopac.MOPACJob.check)    def check(self):
            """Grep standard output for ``* JOB ENDED NORMALLY *``."""
            s = self.results.grep_output('* JOB ENDED NORMALLY *')
            return len(s) > 0
    
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
