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
  * scm.plams.interfaces.thirdparty.dirac

# Source code for scm.plams.interfaces.thirdparty.dirac
[code]
    import os
    
    from os.path import join as opj
    
    from ...core.basejob import SingleJob
    from ...core.private import saferun
    from ...core.results import Results
    from ...core.settings import Settings
    
    __all__ = ['DiracJob', 'DiracResults']
    
    [[docs]](../../../../../interfaces/dirac.html#scm.plams.interfaces.thirdparty.dirac.DiracResults)class DiracResults(Results):
        """A class for result of computation done with DIRAC."""
        _rename_map = {'DFCOEF':'$JN.dfcoef', 'GRIDOUT':'$JN.grid', 'dirac.xml':'$JN.xml',}
    
    [[docs]](../../../../../interfaces/dirac.html#scm.plams.interfaces.thirdparty.dirac.DiracResults.collect)    def collect(self):
            """After collecting the files produced by job execution with parent method :meth:`Results.collect<scm.plams.core.results.Results.collect>` append the ``pam`` output to the regular output file.
            """
            Results.collect(self)
            pamfile = self.job._filename('out')
            process = saferun(['grep', 'output file', pamfile], cwd=self.job.path)
            output = process.stdout.decode()
            diracfile = output.split(':')[-1].strip()
            if diracfile in self.files:
                pampath = opj(self.job.path, pamfile)
                diracpath = opj(self.job.path, diracfile)
                with open(pampath, 'r') as f:
                    pamoutput = f.readlines()
                with open(diracpath, 'r') as f:
                    diracoutput = f.readlines()
                with open(pampath, 'w') as f:
                    f.writelines(diracoutput)
                    f.write('\n\n   '+'*'*74+'\n')
                    f.write('   '+'*'*30+'  pam output  '+'*'*30+'\n')
                    f.write('   '+'*'*74+'\n\n')
                    f.writelines(pamoutput)
                os.remove(diracpath)
            self.refresh()
    
    [[docs]](../../../../../interfaces/dirac.html#scm.plams.interfaces.thirdparty.dirac.DiracJob)class DiracJob(SingleJob):
        """A class representing a single computational job with DIRAC."""
    
        _result_type = DiracResults
        _top = ['dirac']
        _filenames = {'inp':'$JN.inp', 'run':'$JN.run', 'out':'$JN.out', 'err': '$JN.err'}
    
    [[docs]](../../../../../interfaces/dirac.html#scm.plams.interfaces.thirdparty.dirac.DiracJob.__init__)    def __init__(self, **kwargs):
            SingleJob.__init__(self, **kwargs)
            self.settings.runscript.pam.noarch = True
            self.settings.runscript.pam.get = ['DFCOEF', 'GRIDOUT', 'dirac.xml']
    
    [[docs]](../../../../../interfaces/dirac.html#scm.plams.interfaces.thirdparty.dirac.DiracJob._get_ready)    def _get_ready(self):
            """Before generating runscript and input with parent method :meth:`SingleJob._get_ready<scm.plams.core.basejob.SingleJob._get_ready>` add proper ``mol`` and ``inp`` entries to ``self.settings.runscript.pam``. If already present there, ``mol`` will not be added.
            """
            s = self.settings.runscript.pam
            if 'mol' not in s:
                s.mol = self.name+'.xyz'
                with open(opj(self.path, self.name+'.xyz'), 'w') as f:
                    f.write(str(len(self.molecule)) + '\n\n')
                    for atom in self.molecule:
                        suffix = 'b={block}' if hasattr(atom,'block') else ''
                        f.write(atom.str(suffix=suffix)+'\n')
            s.inp = self._filename('inp')
            SingleJob._get_ready(self)
    
    [[docs]](../../../../../interfaces/dirac.html#scm.plams.interfaces.thirdparty.dirac.DiracJob.get_input)    def get_input(self):
            """Transform all contents of ``input`` branch of ``settings`` into string with blocks, subblocks, keys and values.
    
            On the highest level alphabetic order of iteration is modified: keys occuring in class attribute ``_top`` are printed first. See :ref:`dirac-input` for details.
            """
            is_empty = lambda x: isinstance(x, Settings) and len(x) == 0
    
            def parse_key(key, value):
                ret = '.' + key.upper() + '\n'
                if not (value is True or is_empty(value)):
                    if isinstance(value, list):
                        for i in value:
                            ret += str(i) + '\n'
                    else:
                        ret += str(value) + '\n'
                return ret
    
            def parse_block(block):
                enabler = '_en'
                ret = '**' + block.upper() + '\n'
                s = self.settings.input[block]
                for k,v in s.items():
                    if not isinstance(v, Settings) or is_empty(v):
                        ret += parse_key(k, v)
                for k,v in s.items():
                    if isinstance(v, Settings) and enabler in v:
                        ret += parse_key(k, v[enabler])
                for k,v in s.items():
                    if isinstance(v, Settings) and len(v) > 0:
                        ret += '*' + k.upper() + '\n'
                        for kk,vv in v.items():
                            if kk != enabler:
                                ret += parse_key(kk, vv)
                return ret
    
            inp = ''
            for block in self._top:
                if block in self.settings.input:
                    inp += parse_block(block)
            for block in self.settings.input:
                if block not in self._top:
                    inp += parse_block(block)
            inp += '*END OF INPUT\n'
            return inp
    
    [[docs]](../../../../../interfaces/dirac.html#scm.plams.interfaces.thirdparty.dirac.DiracJob.get_runscript)    def get_runscript(self):
            """Generate a runscript. Returned string is a ``pam`` call followed by option flags generated based on ``self.settings.runscript.pam`` contents. See :ref:`dirac-runscript` for details."""
            r = self.settings.runscript.pam
            ret = 'pam'
            for k,v in r.items():
                ret += ' --%s'%k
                if v is not True:
                    if isinstance(v, list):
                        ret += '="%s"' % ' '.join(v)
                    else:
                        ret += '='+str(v)
    
            if self.settings.runscript.stdout_redirect:
                ret += ' >'+self._filename('out')
            ret += '\n\n'
            return ret
    
    [[docs]](../../../../../interfaces/dirac.html#scm.plams.interfaces.thirdparty.dirac.DiracJob.check)    def check(self):
            """Check if the calculation was successful by examining the last line of ``pam`` output."""
            s = self.results.grep_output('exit           :')[0]
            status = s.split(':')[-1].strip()
            return status == 'normal'
    
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
