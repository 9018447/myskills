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
  * scm.plams.core.jobmanager

# Source code for scm.plams.core.jobmanager
[code]
    import os
    import threading
    import re
    import shutil
    try:
        import dill as pickle
    except ImportError:
        import pickle
    
    from os.path import join as opj
    
    from .basejob import MultiJob
    from .errors import PlamsError, FileError
    from .functions import config, log
    
    __all__ = ['JobManager']
    
    [[docs]](../../../../components/jobmanager.html#scm.plams.core.jobmanager.JobManager)class JobManager:
        """Class responsible for jobs and files management.
    
        Every instance has the following attributes:
    
        *   ``foldername`` -- the working folder name.
        *   ``workdir`` -- the absolute path to the working folder.
        *   ``logfile`` -- the absolute path to the logfile.
        *   ``input`` -- the absolute path to the copy of the input file in the working folder.
        *   ``settings`` -- a |Settings| instance for this job manager (see below).
        *   ``jobs`` -- a list of all jobs managed with this instance (in order of |run| calls).
        *   ``names`` -- a dictionary with names of jobs. For each name an integer value is stored indicating how many jobs with that basename have already been run.
        *   ``hashes`` -- a dictionary working as a hash-table for jobs.
    
        The *path* argument should be be a path to a directory inside which the main working folder will be created. If ``None``, the directory from where the whole script was executed is used.
    
        The ``foldername`` attribute is initially set to the *folder* argument. If such a folder already exists (and ``use_existing_folder`` is False), the suffix ``.002`` is appended to *folder* and the number is increased (``.003``, ``.004``...) until a non-existsing name is found. If *folder* is ``None``, the name ``plams_workdir`` is used, followed by the same procedure to find a unique ``foldername``.
    
        The ``settings`` attribute is directly set to the value of *settings* argument (unlike in other classes where they are copied) and it should be a |Settings| instance with the following keys:
    
        *   ``hashing`` -- chosen hashing method (see |RPM|).
        *   ``counter_len`` -- length of number appended to the job name in case of a name conflict.
        *   ``remove_empty_directories`` -- if ``True``, all empty subdirectories of the working folder are removed on |finish|.
    
        """
    
    [[docs]](../../../../components/jobmanager.html#scm.plams.core.jobmanager.JobManager.__init__)    def __init__(self, settings, path=None, folder=None, use_existing_folder=False):
    
            self.settings = settings
            self.jobs = []
            self.names = {}
            self.hashes = {}
    
            self._register_lock = threading.RLock()
    
            if path is None:
                ams_resultsdir = os.getenv("AMS_RESULTSDIR")
                if not ams_resultsdir is None and os.path.isdir(ams_resultsdir):
                    self.path = ams_resultsdir
                else:
                    self.path = os.getcwd()
            elif os.path.isdir(path):
                self.path = os.path.abspath(path)
            else:
                raise PlamsError('Invalid path: {}'.format(path))
    
            basename = os.path.normpath(folder) if folder else 'plams_workdir'
            self.foldername = basename
    
            if not use_existing_folder:
                n = 2
                while os.path.exists(opj(self.path, self.foldername)):
                    self.foldername = basename + '.' + str(n).zfill(3)
                    n += 1
    
            self.workdir = opj(self.path, self.foldername)
            self.logfile = os.environ["SCM_LOGFILE"] if ("SCM_LOGFILE" in os.environ) else opj(self.workdir, 'logfile')
            self.input = opj(self.workdir, 'input')
    
            if not (use_existing_folder and os.path.exists(self.workdir)):
                os.mkdir(self.workdir)
    
    [[docs]](../../../../components/jobmanager.html#scm.plams.core.jobmanager.JobManager.load_job)    def load_job(self, filename):
            """Load previously saved job from *filename*.
    
            *Filename* should be a path to a ``.dill`` file in some job folder. A |Job| instance stored there is loaded and returned. All attributes of this instance removed before pickling are restored. That includes ``jobmanager``, ``path`` (the absolute path to the folder containing *filename* is used) and ``default_settings`` (a list containing only ``config.job``).
    
            See |pickling| for details.
            """
            def setstate(job, path, parent=None):
                job.parent = parent
                job.jobmanager = self
                job.default_settings = [config.job]
                job.path = path
                if isinstance(job, MultiJob):
                    job._lock = threading.Lock()
                    for child in job:
                        setstate(child, opj(path, child.name), job)
                    for otherjob in job.other_jobs():
                        setstate(otherjob, opj(path, otherjob.name), job)
    
                job.results.refresh()
                h = job.hash()
                if h is not None:
                    self.hashes[h] = job
                for key in job._dont_pickle:
                    job.__dict__[key] = None
    
            if os.path.isfile(filename):
                filename = os.path.abspath(filename)
            else:
                raise FileError('File {} not present'.format(filename))
            path = os.path.dirname(filename)
            with open(filename, 'rb') as f:
                try:
                    job = pickle.load(f)
                except Exception as e:
                    log("Unpickling of {} failed. Caught the following Exception:\n{}".format(filename, e), 1)
                    return None
    
            setstate(job, path)
            return job
    
    [[docs]](../../../../components/jobmanager.html#scm.plams.core.jobmanager.JobManager.remove_job)    def remove_job(self, job):
            """Remove *job* from the job manager. Forget its hash."""
            with self._register_lock:
                if job in self.jobs:
                    self.jobs.remove(job)
                    job.jobmanager = None
                h = job.hash()
                if h in self.hashes and self.hashes[h] == job:
                    del self.hashes[h]
                if isinstance(job, MultiJob):
                    for child in job:
                        self.remove_job(child)
                    for otherjob in job.other_jobs():
                        self.remove_job(otherjob)
                shutil.rmtree(job.path)
    
    [[docs]](../../../../components/jobmanager.html#scm.plams.core.jobmanager.JobManager._register)    def _register(self, job):
            """Register the *job*. Register job's name (rename if needed) and create the job folder.
    
            If a job with the same name was already registered, *job* is renamed by appending consecutive integers. The number of digits in the appended number is defined by the ``counter_len`` value in ``settings``.
            Note that jobs whose name already contains a counting suffix, e.g. ``myjob.002`` will have the suffix stripped as the very first step.
            """
            with self._register_lock:
    
                log('Registering job {}'.format(job.name), 7)
                job.jobmanager = self
    
                # If the name ends with the counting suffix, e.g. ".002", remove it.
                # The suffix is just not part of a legitimate job name and users will have to live with it potentially changing.
                orgfname = job._full_name()
                job.name = re.sub(r"(\.\d{%i})+$"%(self.settings.counter_len), "", job.name)
                fname = job._full_name()
                if fname in self.names:
                    self.names[fname] += 1
                    job.name += '.'+str(self.names[fname]).zfill(self.settings.counter_len)
                    fname = job._full_name()
                else:
                    self.names[fname] = 1
                if fname != orgfname:
                    log('Renaming job {} to {}'.format(orgfname, fname), 3)
    
                if job.path is None:
                    if job.parent:
                        job.path = opj(job.parent.path, job.name)
                    else:
                        job.path = opj(self.workdir, job.name)
                os.mkdir(job.path)
    
                self.jobs.append(job)
                job.status = 'registered'
                log('Job {} registered'.format(job.name), 7)
    
    [[docs]](../../../../components/jobmanager.html#scm.plams.core.jobmanager.JobManager._check_hash)    def _check_hash(self, job):
            """Calculate the hash of *job* and, if it is not ``None``, search previously run jobs for the same hash. If such a job is found, return it. Otherwise, return ``None``"""
            h = job.hash()
            if h is not None:
                with self._register_lock:
                    if h in self.hashes:
                        prev = self.hashes[h]
                        log('Job {} previously run as {}, using old results'.format(job.name, prev.name), 1)
                        return prev
                    else:
                        self.hashes[h] = job
            return None
    
    [[docs]](../../../../components/jobmanager.html#scm.plams.core.jobmanager.JobManager._clean)    def _clean(self):
            """Clean all registered jobs according to the ``save`` parameter in their ``settings``. If ``remove_empty_directories`` is ``True``,  traverse the working directory and delete all empty subdirectories."""
            log('Cleaning job manager', 7)
    
            for job in self.jobs:
                job.results._clean(job.settings.save)
    
            if self.settings.remove_empty_directories:
                for root, dirs, files in os.walk(self.workdir, topdown=False):
                    for dirname in dirs:
                        fullname = opj(root, dirname)
                        if not os.listdir(fullname):
                            os.rmdir(fullname)
    
            log('Job manager cleaned', 7)
    
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
