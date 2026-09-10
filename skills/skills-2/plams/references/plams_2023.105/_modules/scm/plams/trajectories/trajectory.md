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
  * scm.plams.trajectories.trajectory

# Source code for scm.plams.trajectories.trajectory
[code]
    #!/usr/bin/env python
    
    from weakref import WeakValueDictionary
    from ..core.settings import Settings
    from ..core.errors import PlamsError
    from ..tools.kftools import KFFile
    from ..interfaces.adfsuite.amsanalysis import AMSAnalysisJob
    from .rkffile import RKFTrajectoryFile
    from .rkfhistoryfile import RKFHistoryFile
    
    __all__ = ['Trajectory']
    
    [[docs]](../../../../components/trajectory.html#scm.plams.trajectories.trajectory.Trajectory)class Trajectory :
            """
            Class representing an AMS trajectory
    
            It creates molecule objects along the trajectory in a list-like fashion.
            It can also perform analysis tasks.
    
            Basic use of the |Trajectory| class works as follows:
    
                >>> from scm.plams import Trajectory
    
                >>> trajec = Trajectory('ams.rkf')
                >>> nsteps = len(trajec)
    
                >>> mol100 = trajec[100]
                >>> for i,mol in enumerate(trajec):
                ...     if i == 100:
                ...         print (mol is mol100)
                ...
                True
    
            As with a regular list, accessing the same element twice yields the same instance of the molecule.
    
            A trajectory may consist of multiple RKF files, for instance after a restarted MD run.
    
                >>> trajec = Trajectory(['md1.results/ams.rkf','md2.results/ams.rkf'])
                >>> nsteps = len(trajec)
                >>> print ('NSteps in each file: ',trajec.lengths)
                NSteps in each file:  [181, 19]
    
            Otherwise the object behaves the same, and iteration occurs over the concatenated files.
    
            .. note::
    
                    It is possible to change the molecule objects once they are loaded, but this will not change the underlying files.
                    When the altered molecule objects have been garbage collected, and the same frame is read anew, this frame
                    will have the original molecule attributes.
    
                        >>> import gc
                        >>> from scm.plams import Trajectory
    
                        >>> trajec = Trajectory('ams.rkf')
                        >>> mol = trajec[100]
                        >>> print (mol.properties.charge)
                        0.0
                        >>> mol.properties.charge = 10000.
                        >>> print (trajec[100].properties.charge)
                        1000.0
            
                        >>> # remove the reference
                        >>> mol = None
                        >>> gc.collect()
                        >>> print (trajec[100].properties.charge)
                        0.
    
            The |Trajectory| object can also be used to perform analysis, using |AMSAnalysisJob| behind the scenes.
           
                >>> from scm.plams import Settings, Trajectory
                >>> from scm.plams import init, finish
     
                >>> trajec = Trajectory('ams.rkf')
    
                >>> # Define the type of analysis
                >>> settings = Settings()
                >>> settings.input.Task = 'RadialDistribution'
                >>> settings.input.RadialDistribution.AtomsFrom.Element = ['O']
                >>> settings.input.RadialDistribution.AtomsTo.Element = ['O']
    
                >>> # Run the analysis
                >>> init()
                >>> plots = trajec.run_analysis(settings)
                >>> finish()
    
                >>> # Store the plot in human readable format
                >>> for plot in plots :
                ...     plot.write('%s'%(plot.name+'.txt'))
    
            This results in a text file named RadialDistribution_1.txt, which contains data organized in columns.
            """
            def __init__ (self, filenames) :
                    """
                    Initiates instance of an AMS trajectory object
    
                    * ``filenames`` -- List of filepaths of RKF trajectory files or single filepath for RKF file
    
                    .. note::
    
                            The corresponding file needs to remain on disc while the object is alive
    
                    """
                    if isinstance(filenames,str):
                            filenames = [filenames]
    
                    # Ceck is RKFHistoryFile needs to be used
                    classes = []
                    for fn in filenames :
                            if not fn.split('.')[-1] == 'rkf' :
                                    raise PlamsError('Files need to be RKF')
                            kf = KFFile(fn)
                            if kf.reader is None :
                                    raise PlamsError('RKF file %s not found'%(fn))
                            kf.reader._create_index()
                            if not 'History' in kf.reader._sections.keys() :
                                    raise PlamsError('%s is not a trajectory file'%(fn))
                            if 'SystemVersionHistory' in kf.reader._sections.keys() :
                                    classes.append(RKFHistoryFile)
                            else :
                                    classes.append(RKFTrajectoryFile)
    
                    # Store the file objects and associated data for each file
                    self.files = [classes[i](fn) for i,fn in enumerate(filenames)]
                    self.molecules = [rkf.get_plamsmol() for rkf in self.files]
                    self.lengths = [len(rkf) for rkf in self.files]
    
                    # Store the items that have been read as a weak reference
                    self.weakrefs = WeakValueDictionary()
    
            def __len__ (self) :
                    """
                    Magic method that returns the length of the trajectory
                    """
                    return sum(self.lengths)
    
            def __iter__ (self) :
                    """
                    Iterates over molecule objects
                    """
                    for irkf,rkf in enumerate(self.files) :
                            mol = self.molecules[irkf]
                            for istep in range(self.lengths[irkf]) :
                                    i = self._get_index(irkf,istep)
                                    if i in self.weakrefs.keys() :
                                            yield self.weakrefs[i]
                                            continue
                                    crd,cell = rkf.read_frame(istep,molecule=mol)
                                    m = mol.copy()
                                    self.weakrefs[i] = m
                                    yield m
    
            def __getitem__ (self, s) :
                    """
                    Returns Molecule object
    
                    * ``s`` -- Python slice object
                    """
                    is_slice = False
                    if isinstance(s,int) :
                            s = slice(s)
                            start, stop, step = s.indices(len(self))
                            indices = range(stop,stop+1)
                    elif isinstance(s,slice) :
                            is_slice = True
                            start, stop, step = s.indices(len(self))
                            indices = range(start,stop,step)
                    mols = []
                    for i in indices :
                            if i in self.weakrefs.keys() :
                                    mol = self.weakrefs[i]
                            else :
                                irkf, istep = self._get_filenum_and_stepnum(i)
                                # This is always the first molecule
                                mol = self.molecules[irkf].copy()
                                crd,cell = self.files[irkf].read_frame(istep,molecule=mol)
                                self.weakrefs[i] = mol
                            mols.append(mol)
                    if not is_slice :
                            mols = mols[0]
                    return mols
    
    [[docs]](../../../../components/trajectory.html#scm.plams.trajectories.trajectory.Trajectory.run_analysis)        def run_analysis (self, settings, steprange=None) :
                    """
                    Calls the AMS analysis tool behind the scenes
    
                    * ``settings``  -- PLAMS Settings object
                      Example :
    
                        >>> settings = Settings()
                        >>> settings.input.Task = 'AutoCorrelation' 
                        >>> settings.input.AutoCorrelation.Property = 'Velocities'
                        >>> settings.input.AutoCorrelation.MaxFrame = 2000
    
                    * ``steprange`` -- Start frame, end frame, and stepsize. The default (None) corresponds to all frames in the object
    
                    Returns a list of AMSAnalysisPlot objects.
                    Main attributes of the AMSAnalysisPlot objects are :
    
                    * ``name``    -- The name of the plot
                    * ``x``       -- A list of lists containing the values of the coordinate system
                      If the coordinate system is 1D, then it is a list containing a single list of values
                      x = [[x1,x2,x3,x4,...,xn]]
                    * ``y``       -- A list containing the function values
                    * ``write()`` -- A method returning a string containing all plot info
                    """
                    #First get all the indices
                    s = slice(steprange)
                    start,stop,step = s.indices(len(self))
                    indices = range(start,stop,step)
                    if steprange is not None :
                            if len(steprange) == 1 :
                                    indices = range(stop,stop+1)
                    stepnums = {}
                    for i in indices :
                            irkf,istep = self._get_filenum_and_stepnum(i)
                            if not irkf in stepnums :
                                    stepnums[irkf] = []
                            stepnums[irkf].append(istep)
                    ranges = []
                    for irkf,values in stepnums.items() :
                            ranges.append((values[0]+1,values[-1]+1,step))
                    print ('ranges: ',ranges)
                    
                    # Now completel the settings object
                    trajecsettings = []
                    for ikf,rkf in enumerate(self.files) :
                            s = Settings()
                            s.Trajectory.KFFilename = self.files[0].file_object.path
                            s.Trajectory.Range = '%i %i %i'%(ranges[irkf][0],ranges[irkf][1],ranges[irkf][2])
                            trajecsettings.append(s)
                    settings.input.TrajectoryInfo = trajecsettings
    
                    # Run the analysis job and extract the plots
                    job = AMSAnalysisJob(settings=settings)
                    result = job.run()
                    plots = result.get_all_plots()
                    return plots
    
            #################
            # Private methods
            #################
    
            def _get_filenum_and_stepnum (self, i) :
                    """
                    Connects a filenumber and a stepnumber to index i
                    """
                    irkf,istep = (-1,-1)
                    counter = 0
                    for il,length in enumerate(self.lengths) :
                            if i < counter+length :
                                    irkf = il
                                    istep = i-counter
                                    break
                            counter += length
                    if irkf < 0 :
                            raise KeyError('Index out of range')
                    return irkf, istep
    
            def _get_index (self, irkf, istep) :
                    """
                    Connects the index i to a filenumber and a stepnumber
                    """
                    return sum([l for l in self.lengths[:irkf]]) + istep
    
    def make_recursively_immutable (obj,verbose=False) :
            """
            Return a new object that is immutable
    
            Note: Any recursive objects are NOT affected. For example, if obj is an instance of Molecule,
                  then this function will return an instance of _Molecule, but new_obj.atoms[0].mol is still the original Molecule.
            """
            # Find all the branches of this object tree
            branchlist = [branch for branch in get_branches(obj)]
            if verbose:
                    print ('Tree: ')
                    for branch in branchlist :
                            print ([n[0] for n in branch])
    
            # Find length of longest branch
            maxlength = max([len(branch) for branch in branchlist])
            for i in range(maxlength-1,0,-1) :
                    if verbose: print ('Level: ',i)
                    # Find all objects at this level, and theit parent
                    for branch in branchlist :
                            if len(branch) > i :
                                    current_obj = branch[i][1]
                                    current_name = branch[i][0]
                                    # Now make immutable. Take care to do this only once for an object
                                    if current_obj.__class__.__name__[0] == '_' or isinstance(current_obj,tuple) : continue
                                    current_obj = make_immutable(current_obj)
                                    parent_obj = branch[i-1][1]
                                    if isinstance(parent_obj,list) :
                                            parent_obj[current_name] = current_obj
                                    elif isinstance(parent_obj,dict) :
                                            parent_obj[current_name] = current_obj
                                    else :
                                            parent_obj.__dict__[current_name] = current_obj
    
            # Now do the top layer
            current_obj = make_immutable(obj, add_self=True)
            return current_obj
    
    def make_immutable (obj, add_self=False) :
            """
            Make this object immutable
    
            Note: This is specifically written for a Molecule object
            """
            def trytosetattr(self, name, value):
                    """
                    A setattr function that does not write attributes
                    """
                    #raise AttributeError("Cannot change object")
                    if hasattr(self, name):
                        raise AttributeError("Cannot reassign members")
                    self.__dict__[name] = value
    
            def trytosetitem(self, name, value) :
                    """
                    A setitem function for a dictionary that returns an exception
                    """
                    raise AttributeError("Cannot change object")
    
            def mutable_copy(obj, atoms=None) :
                    """
                    Returns a copy of self, but one that is mutable
                    """
                    if hasattr(obj,'__dict__') :
                            if '_orig' in obj.__dict__ :
                                    return obj._orig
                            else :
                                    return None
                    elif '_orig' in obj :
                            return obj['_orig']
                    else :
                            return None
    
            # If the object is a built-in object, all the below does not work
            if isinstance(obj,list) :
                    return (tuple(obj))
            # There will be dictionaries (Settings objects). How to make those immutable?
    
            # Lets get the name of the class
            classname = obj.__class__.__name__
    
            # Lets get all the instance variables of the input object
            attribs = []
            values = []
            if hasattr(obj,'__dict__') :
                    attribs = [key for key in obj.__dict__.keys()]
                    values = [obj.__dict__[key] for key in attribs]
    
            # Create a new class which is derived from the objects class
            ImmutableClass = type('_'+classname, (obj.__class__,), {})
    
            # Now create an instance of the new class with the same instance variables
            im_obj = ImmutableClass.__new__(ImmutableClass)
            if isinstance (obj, dict) :
                    # This is for a dictionary or PLAMS Settings object
                    for key,value in obj.items() :
                            im_obj[key] = value
            else :
                    for key,value in zip(attribs,values) :
                            setattr(im_obj,key,value)
    
            # Add its original self, for copying purposes
            if add_self :
                    im_obj._orig = obj
                    setattr(ImmutableClass,'copy',mutable_copy)
    
            # Now set the method that makes overwriting attributes impossible
            if isinstance(obj,dict) :
                    setattr(ImmutableClass,'__setitem__',trytosetitem)
            else :
                    setattr(ImmutableClass,'__setattr__',trytosetattr)
    
            return im_obj
    
    def get_branches (obj, subpath=None) :
            """
            Search recursively through instance variables of object until an immutable one is met
            """
            tree = dictionary_from_object(obj)
            if subpath is None :
                    subpath = (('top',obj),)
            # Identify immutable objects and circular objects (they are leafs)
            prev_objects = [node[1] for node in subpath]
            im_objs = []
            for n,o in tree.items() :
                    if is_immutable(o) :
                            im_objs.append(n)
                    # Avoid circular crap
                    elif True in [o is po for po in prev_objects] :
                            im_objs.append(n)
            # The branch ends if the tree contains only immutable objects
            if len(im_objs) == len(tree) :
                    yield subpath
            else:
                    for n, o in tree.items():
                            if n in im_objs : continue
                            for path in get_branches(o, subpath+((n,o),)):
                                    yield path
    
    def is_immutable (obj) :
            """
            Check if this object is immutable
    
            Note: This is a first incomplete implementation
            """
            typelist = [int,float,tuple,str,bool] # This does not take into account numpy integers etc
            immutable = False
            if obj is None :
                    immutable = True
            for t in typelist :
                    if isinstance(obj,t) :
                            immutable = True
                            break
            return immutable
    
    def dictionary_from_object (obj) :
            """
            Get the dicrtionary of object attributes
            """
            if hasattr(obj,'__dict__') :
                    tree = obj.__dict__
            elif isinstance(obj,dict) :
                    tree = obj
            elif hasattr(obj,'__iter__') :
                    tree = {}
                    for i,v in enumerate(obj) :
                            tree[i] = v
            else :
                    raise Exception('What is this object?',type(obj))
            return tree
    
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
