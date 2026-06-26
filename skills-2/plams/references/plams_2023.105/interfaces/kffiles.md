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
      * [ASE Calculator for AMS](amscalculator.html)
      * [Quick jobs](quickjobs.html)
      * [Analysis tools: Densf, FCF, analysis](postadf.html)
      * KF files
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
  * KF files

# KF files¶

KF is the main format for storing binary data used in all Amsterdam Modeling Suite programs. All `TAPEXX` and `.rkf` files are KF files. PLAMS offers a dictionary-like interface to KF format which allows for reading, writing, modifying and creating KF files efficiently.

_class _`KFFile`(_path_ , _autosave =True_)[[source]](../_modules/scm/plams/tools/kftools.html#KFFile)¶
    
A class for reading and writing binary files in KF format.

This class acts as a wrapper around `KFReader` collecting all the data written by user in some “temporary zone” and using Fortran binaries `udmpkf` and `cpkf` to write this data to the physical file when needed.

The constructor argument _path_ should be a string with a path to an existing KF file or a new KF file that you wish to create. If a path to existing file is passed, new `KFReader` instance is created allowing to read all the data from this file.

When `write()` method is used, the new data is not immediately written to a disk. Instead of that, it is temporarily stored in `tmpdata` dictionary. When method `save()` is invoked, contents of that dictionary are written to a physical file and `tmpdata` is emptied.

Other methods like `read()` or `delete_section()` are aware of `tmpdata` and work flawlessly, regardless if `save()` was called or not.

By default, `save()` is automatically invoked after each `write()`, so physical file on a disk is always “actual”. This behavior can be adjusted with _autosave_ constructor parameter. Having autosave enabled is usually a good idea, however, if you need to write a lot of small pieces of data to your file, the overhead of calling `udmpkf` and `cpkf` after _every_ `write()` can lead to significant delays. In such a case it is advised to disable autosave and call `save()` manually, when needed.

Dictionary-like bracket notation can be used as a shortcut to read and write variables:
[code] 
    mykf = KFFile('someexistingkffile.kf')
    #all three below are equivalent
    x = mykf['General%Termination Status']
    x = mykf[('General','Termination Status')]
    x = mykf.read('General','Termination Status')
    
    #all three below are equivalent
    mykf['Geometry%xyz'] = somevariable
    mykf[('Geometry','xyz')] = somevariable
    mykf.write('Geometry','xyz', somevariable)
    
[/code]

`__init__`(_path_ , _autosave =True_)[[source]](../_modules/scm/plams/tools/kftools.html#KFFile.__init__)¶
    
Initialize self. See help(type(self)) for accurate signature.

`read`(_section_ , _variable_ , _return_as_list =False_)[[source]](../_modules/scm/plams/tools/kftools.html#KFFile.read)¶
    
Extract and return data for a _variable_ located in a _section_.

By default, for single-value numerical or boolean variables returned value is a single number or bool. For longer variables this method returns a list of values. For string variables a single string is returned. This behavior can be changed by setting _return_as_list_ parameter to `True`. In that case the returned value is always a list of numbers (possibly of length 1) or a single string.

`write`(_section_ , _variable_ , _value_ , _value_type =None_)[[source]](../_modules/scm/plams/tools/kftools.html#KFFile.write)¶
    
Write a _variable_ with a _value_ in a _section_ . If such a variable already exists in this section, the old value is overwritten.

`save`()[[source]](../_modules/scm/plams/tools/kftools.html#KFFile.save)¶
    
Save all changes stored in `tmpdata` to physical file on a disk.

`delete_section`(_section_)[[source]](../_modules/scm/plams/tools/kftools.html#KFFile.delete_section)¶
    
Delete the entire _section_ from this KF file.

`sections`()[[source]](../_modules/scm/plams/tools/kftools.html#KFFile.sections)¶
    
Return a list with all section names, ordered alphabetically.

`read_section`(_section_)[[source]](../_modules/scm/plams/tools/kftools.html#KFFile.read_section)¶
    
Return a dictionary with all variables from a given _section_.

Note

Some sections can contain very large amount of data. Turning them into dictionaries can cause memory shortage or performance issues. Use this method carefully.

`keys`()[[source]](../_modules/scm/plams/tools/kftools.html#KFFile.keys)¶
    
Returns all sections in the current instance

`get_skeleton`()[[source]](../_modules/scm/plams/tools/kftools.html#KFFile.get_skeleton)¶
    
Return a dictionary reflecting the structure of this KF file. Each key in that dictionary corresponds to a section name of the KF file with the value being a set of variable names.

`__getitem__`(_name_)[[source]](../_modules/scm/plams/tools/kftools.html#KFFile.__getitem__)¶
    
Allow to use `x = mykf['section%variable']` or `x = mykf[('section','variable')]` instead of `x = kf.read('section', 'variable')`.

`__setitem__`(_name_ , _value_)[[source]](../_modules/scm/plams/tools/kftools.html#KFFile.__setitem__)¶
    
Allow to use `mykf['section%variable'] = value` or `mykf[('section','variable')] = value` instead of `kf.write('section', 'variable', value)`.

`__iter__`()[[source]](../_modules/scm/plams/tools/kftools.html#KFFile.__iter__)¶
    
Iteration yields pairs of section name and variable name.

`__contains__`(_arg_)[[source]](../_modules/scm/plams/tools/kftools.html#KFFile.__contains__)¶
    
Implements Python `in` operator for KFFiles. _arg_ can be a single string with a section name or a pair of strings (section, variable).

_static _`_split`(_name_)[[source]](../_modules/scm/plams/tools/kftools.html#KFFile._split)¶
    
Ensure that a key used in bracket notation is of the form `'section%variable'` or `('section','variable')`. If so, return a tuple `('section','variable')`.

_static _`_str`(_val_)[[source]](../_modules/scm/plams/tools/kftools.html#KFFile._str)¶
    
Return a string representation of _val_ in the form that can be understood by `udmpkf`.

_class _`KFReader`(_path_ , _blocksize =4096_, _autodetect =True_)[[source]](../_modules/scm/plams/tools/kftools.html#KFReader)¶
    
A class for efficient Python-native reader of binary files in KF format.

This class offers read-only access to any fragment of data from a KF file. Unlike other Python KF readers, this one does not use the Fortran binary `dmpkf` to process KF files, but instead reads and interprets raw binary data straight from the file, on Python level. That approach results in significant speedup (by a factor of few hundreds for large files extracted variable by variable).

The constructor argument _path_ should be a string with a path (relative or absolute) to an existing KF file.

_blocksize_ indicates the length of basic KF file block. So far, all KF files produced by any of Amsterdam Modeling Suite programs have the same block size of 4096 bytes. Unless you’re doing something _very_ special, you should not touch this value.

Organization of data inside KF file can depend on a machine on which this file was produced. Two parameters can vary: the length of integer (32 or 64 bit) and endian (little or big). These parameters have to be determined before any reading can take place, otherwise the results will have no sense. If the constructor argument _autodetect_ is `True`, the constructor attempts to automatically detect the format of a given KF file, allowing to read files created on a machine with different endian or integer length. This automatic detection is enabled by default and it is advised to leave it that way. If you wish to disable it, you should set `endian` and `word` attributes manually before reading anything (see the code for details).

Note

This class consists of quite technical, low level code. If you don’t need to modify or extend `KFReader`, you can safely ignore all private methods, all you need is `read()` and occasionally `__iter__()`

`__init__`(_path_ , _blocksize =4096_, _autodetect =True_)[[source]](../_modules/scm/plams/tools/kftools.html#KFReader.__init__)¶
    
Initialize self. See help(type(self)) for accurate signature.

`read`(_section_ , _variable_)[[source]](../_modules/scm/plams/tools/kftools.html#KFReader.read)¶
    
Extract and return data for a _variable_ located in a _section_.

For single-value numerical or boolean variables returned value is a single number or bool. For longer variables this method returns a list of values. For string variables a single string is returned.

`variable_type`(_section_ , _variable_)[[source]](../_modules/scm/plams/tools/kftools.html#KFReader.variable_type)¶
    
Return the integer code of the variable’s type (int:1, float:2, string:3, bool:4)

`__iter__`()[[source]](../_modules/scm/plams/tools/kftools.html#KFReader.__iter__)¶
    
Iteration yields pairs of section name and variable name.

`_autodetect`()[[source]](../_modules/scm/plams/tools/kftools.html#KFReader._autodetect)¶
    
Try to automatically detect the format (int size and endian) of this KF file.

`_read_block`(_f_ , _pos_)[[source]](../_modules/scm/plams/tools/kftools.html#KFReader._read_block)¶
    
Read a single block of binary data from posistion _pos_ in file _f_.

`_parse`(_block_ , _format_)[[source]](../_modules/scm/plams/tools/kftools.html#KFReader._parse)¶
    
Translate a _block_ of binary data into list of values in specified _format_.

_format_ should be a list of pairs _(a,t)_ where _t_ is one of the following characters: `'s'` for string (bytes), `'i'` for 32-bit integer, `'q'` for 64-bit integer and _a_ is the number of occurrences (or length of a string).

For example, if _format_ is equal to `[(32,'s'),(4,'i'),(2,'d'),(2,'i')]`, the contents of _block_ are divided into 72 bytes (32*1 + 4*4 + 2*8 + 2*4 = 72) chunks (possibly droping the last one, if it’s shorter than 72 bytes). Then each chunk is translated to a 9-tuple of bytes, 4 ints, 2 floats and 2 ints. List of such tuples is the returned value.

`_get_data`(_datablock_ , _vtype_)[[source]](../_modules/scm/plams/tools/kftools.html#KFReader._get_data)¶
    
Extract all data of a given type from a single data block. Returned value is a list of values (int, float, or bool) or a single “bytes” object.

`_create_index`()[[source]](../_modules/scm/plams/tools/kftools.html#KFReader._create_index)¶
    
Find and parse relevant index blocks of KFFile to extract the information about location of all sections and variables.

Two dictionaries are populated during this process. `_data` contains, for each section, a list of triples describing how logical blocks of data are mapped into physical ones. For example, `_data['General'] = [(3,6,12), (9,40,45)]` means that logical blocks 3-8 of section `General` are located in physical blocks 6-11 and logical blocks 9-13 in physical blocks 40-44. This list is always sorted via first tuple elements allowing efficient access to arbitrary logical block of each section.

The second dictionary, `_sections`, is used to locate each variable within its section. For each section, it contains another dictionary of each variable of this section. So `_section[sec][var]` contains all information needed to extract variable `var` from section `sec`. This is a 4-tuple containing the following information: variable type, logic block in which the variable first occurs, position within this block where its data start and the length of the variable. Combining this information with mapping stored in `_data` allows to extract each single variable.

_static _`_datablocks`(_lst_ , _n =1_)[[source]](../_modules/scm/plams/tools/kftools.html#KFReader._datablocks)¶
    
Transform a tuple of lists `([x1,x2,...], [(a1,b1),(a2,b2),...])` into an iterator over `range(a1,b1)+range(a2,b2)+...` Iteration starts from nth element of this list.

_class _`KFHistory`(_kf_ , _section_)[[source]](../_modules/scm/plams/tools/kftools.html#KFHistory)¶
    
A class for reading “History” sections of files in the KF format.

This class acts as a wrapper around `KFReader` enabling convenient iteration over entries (frames) of History sections.

The constructor argument _kf_ should be a `KFReader` instance attached to an existing KF file. The _section_ argument then holds a name of the desired History-like section, such as “History” or “MDHistory”.

The `read_all()` method can be used used to easily read all values of a particular history item into a single numpy array.

To iterate over the frames in a history section, use `iter()` or `iter_optional()`. The former raises an exception if the selected variable is not present in the history, while the latter returns a given default value instead.

Usage:
[code] 
    kf = KFReader('somefile.rkf')
    mdhistory = KFHistory(kf, 'MDHistory')
    
    for T, p in mdhistory.iter('Temperature'), mdhistory.iter_optional('Pressure', 0):
        print(T, p)
    
[/code]

`__init__`(_kf_ , _section_)[[source]](../_modules/scm/plams/tools/kftools.html#KFHistory.__init__)¶
    
Initialize self. See help(type(self)) for accurate signature.

`read_all`(_name_)[[source]](../_modules/scm/plams/tools/kftools.html#KFHistory.read_all)¶
    
Return a numpy array containing the values of history item _name_ from all frames.

`iter`(_name_)[[source]](../_modules/scm/plams/tools/kftools.html#KFHistory.iter)¶
    
Iterate over the values of history item _name_.

`iter_optional`(_name_ , _default =None_)[[source]](../_modules/scm/plams/tools/kftools.html#KFHistory.iter_optional)¶
    
Iterate over the values of history item _name_ , returning _default_ if the item is not present.

[Next ](crs.html "COSMO-RS") [ Previous](postadf.html "Analysis tools: Densf, FCF, analysis")

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
