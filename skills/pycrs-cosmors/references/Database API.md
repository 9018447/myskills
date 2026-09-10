---
title: "Database"
source: "https://www.scm.com/doc/COSMO-RS/pyCRS/Database.html"
author:
published: 2023-05-23
created: 2026-04-10
description: "Software for Chemistry & Materials"
tags:
  - "clippings"
---
## Database

The submodule contain several class for providing an interface to a sql database for managing COSKF files and physical properties.

*class* pyCRS.Database.COSKFDatabase(*path: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")*) [¶](Database%20API.md#pyCRS.Database.COSKFDatabase)

A class provide an interface to a sql database containing the following tables.

| Table name | Description |
| --- | --- |
| **Compound** | Unique compounds with COSKF files by CAS number or identifier. |
| **Conformer** | Multiple conformers with corresponding COSKF files. |
| **PhysicalProperty** | User-defined physical properties. |
| **PropPred** | Estimated properties using QSPR methods from SMILES. |

Parameters:

**path** ([`str`](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")) – Path to the database file. Created if it doesn’t exist.

Example:

```python
db = COSKFDatabase("my_coskf_db.db")
db.add_compound("Water.coskf")
db.add_compound("Benzene.coskf",cas="71-43-2")
db.add_physical_property("Benzene", "meltingpoint", 278.7)
db.add_physical_property("Benzene", "hfusion", 9.91, unit="kJ/mol")
db.estimate_physical_property("Benzene")
```

add\_compound(*coskf\_file: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")*, *name: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)") | [None](https://docs.python.org/3.8/library/constants.html#None "(in Python v3.8)") = None*, *cas: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)") | [None](https://docs.python.org/3.8/library/constants.html#None "(in Python v3.8)") = None*, *identifier: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)") | [None](https://docs.python.org/3.8/library/constants.html#None "(in Python v3.8)") = None*, *coskf\_path: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)") | [None](https://docs.python.org/3.8/library/constants.html#None "(in Python v3.8)") = None*, *smiles: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)") | [None](https://docs.python.org/3.8/library/constants.html#None "(in Python v3.8)") = None*, *nring: [int](https://docs.python.org/3.8/library/functions.html#int "(in Python v3.8)") | [None](https://docs.python.org/3.8/library/constants.html#None "(in Python v3.8)") = None*, *ignore\_smiles\_check: [bool](https://docs.python.org/3.8/library/functions.html#bool "(in Python v3.8)") = False*, *ignore\_duplicates: [bool](https://docs.python.org/3.8/library/functions.html#bool "(in Python v3.8)") = False*) [¶](Database%20API.md#pyCRS.Database.COSKFDatabase.add_compound)

Adds a new **.coskf** file to the database.

Parameters:

**coskf\_file** ([`str`](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")) – a path to the **.coskf** file, or alternatively, the file name of the **.coskf** file if the `coskf_path` is provided.

Keyword Arguments:

- **name** (`str, optional`) – Compound name. Default to IUPAC name, CAS number, identifier, or **.coskf** file name if not specified. Can be set via keyword argument or read from the **.coskf** file.
- **cas** (`str, optional`) – CAS number. If not provided, it will attempt to use the value from the **.coskf** file if available.
- **identifier** (`str, optional`) – Chemical identifier of the compound.
- **coskf\_path** (`str, optional`) – Directory containing the **.coskf** file. Defaults to ADFCRS-2018 database path.
- **smiles** (`str, optional`) – SMILES string. Defaults to the value in the **.coskf** file if available.
- **nring** (`int, optional`) – Numbr of ring atoms. Defaults to the value from the **.coskf** file.
- **ignore\_smiles\_check** (`bool, optional`) – If True, skips identity check via SMILES generation. Defaults to Fasle.
- **ignore\_duplicates** (`bool, optional`) – If True, skips duplicate recognition using UniqueConformersCrest in AMSConformer tool. Default to False.

> [!note] Note
> - Each compound must have an unique CAS number or identifier.
> - During **add\_compound**, CAS and identifier are checked for uniqueness in the database.
> - An error is raised if multiple compounds share the same CAS number and identifier.
> - The example below is invalid because both compounds use the same identifier, CRS0001.

```python
db.add_compound("Benzene.coskf",cas="71-43-2",identifier="CRS0001")
db.add_compound("Ethanol.coskf",cas="64-17-5",identifier="CRS0001")
```

add\_physical\_property(*identifier: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")*, *attribute: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")*, *value: [float](https://docs.python.org/3.8/library/functions.html#float "(in Python v3.8)") | [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")*, *unit: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)") | [None](https://docs.python.org/3.8/library/constants.html#None "(in Python v3.8)") = None*) [¶](Database%20API.md#pyCRS.Database.COSKFDatabase.add_physical_property)

Add a value of a physical property to the PhysicalProperty TABLE in the database using compound’s identifier

Parameters:

- **identifier** ([`str`](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")) – CAS number, identifier or compound name.
- **attribute** ([`str`](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")) – Name of the physical property (eg. meltingpoint or hfusion).
- **value** (`float or str`) – Value of the physical property.
- **unit** (`str, optional`) – the unit of the input value. The default units are **K**, **kcal/mol** and **kcal/mol-K**. The following units are accepted and will be automatically converted to the default units: - Temperature: K, C - Enthalpy: kcal/mol, kJ/mol, cal/g, J/g - Heat capacity: kcal/mol-K, kJ/mol-K, cal/g-K, J/g-K - pvap: bar, atm, Pa, mmHg

> [!note] Note
> The **vp\_equation** accepts only parameters for pressure in **bar** and temperature in **Kelvin**.

```python
db.add_physical_property("Benzene", "meltingpoint", 278.7)
db.add_physical_property("Benzene", "hfusion", 9.91, unit="kJ/mol")
db.add_physical_property("Benzene", "vp_equation", "Antoine")
db.add_physical_property("Benzene", "vp_params", "4.72583, 1660.652, -1.461")
db.add_physical_property("Benzene", "flashpoint", -11.63, unit="C")
#Vapor pressure at 353.25K is 1.01325 bar
db.add_physical_property("Benzene", "tvap", 353.25)
db.add_physical_property("Benzene", "pvap", 1.01325)
```

clear\_physical\_property(*identifier: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)") | [List](https://docs.python.org/3.8/library/typing.html#typing.List "(in Python v3.8)") \[[str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")\] | [None](https://docs.python.org/3.8/library/constants.html#None "(in Python v3.8)") = None*, *attribute: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)") | [List](https://docs.python.org/3.8/library/typing.html#typing.List "(in Python v3.8)") \[[str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")\] | [None](https://docs.python.org/3.8/library/constants.html#None "(in Python v3.8)") = None*) [¶](Database%20API.md#pyCRS.Database.COSKFDatabase.clear_physical_property)

Clears the value of a physical property in PhysicalProperty TABLE in the database by compound’s identifier

Parameters:

- **identifier** (`str or List[str], optional`) – CAS number, chemical identifier or compound name as a string or a list of strings. If None, all compound are selected.
- **attribute** (`str or List[str], optional`) – Specific property to clear as a string or a list of strings. If None, all properties are cleared.

```python
db.clear_physical_property(["water", "benzene"])
```

del\_row(*dbrow: | [Dict](https://docs.python.org/3.8/library/typing.html#typing.Dict "(in Python v3.8)") \[[str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)"), [List](https://docs.python.org/3.8/library/typing.html#typing.List "(in Python v3.8)") \[\]\]*) [¶](Database%20API.md#pyCRS.Database.COSKFDatabase.del_row)

Remove a compound from the database and delete the corresponding **.coskf** file.

Parameters:

**dbrow** (`CompoundRow or Dict[str, List[CompoundRow]]`) – the row to remove from the database

del\_row\_by\_conformer\_id(*conformer\_id: [int](https://docs.python.org/3.8/library/functions.html#int "(in Python v3.8)")*) [¶](Database%20API.md#pyCRS.Database.COSKFDatabase.del_row_by_conformer_id)

Remove the conformer from the database.

Parameters:

**conformer\_id** ([`int`](https://docs.python.org/3.8/library/functions.html#int "(in Python v3.8)")) – A integer of intergers representing the conformer in the CONFORMER TABLE.

```python
db.del_row_by_conformer_id(1)
```

del\_rows(*dbrows: [List](https://docs.python.org/3.8/library/typing.html#typing.List "(in Python v3.8)") \[\] | [Dict](https://docs.python.org/3.8/library/typing.html#typing.Dict "(in Python v3.8)") \[[str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)"), [List](https://docs.python.org/3.8/library/typing.html#typing.List "(in Python v3.8)") \[\]\]*) [¶](Database%20API.md#pyCRS.Database.COSKFDatabase.del_rows)

Remove multiple compounds from the database and delete the corresponding **.coskf** files.

Parameters:

**dbrows** (`List[CompoundRow] or Dict[str, List[CompoundRow]]]`) – the rows to remove from the database.

```python
db.del_rows(db.get_compounds('benzene'))
```

estimate\_physical\_property(*identifier: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)") | [List](https://docs.python.org/3.8/library/typing.html#typing.List "(in Python v3.8)") \[[str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")\] | [None](https://docs.python.org/3.8/library/constants.html#None "(in Python v3.8)") = None*, *compound\_id: [int](https://docs.python.org/3.8/library/functions.html#int "(in Python v3.8)") | [List](https://docs.python.org/3.8/library/typing.html#typing.List "(in Python v3.8)") \[[int](https://docs.python.org/3.8/library/functions.html#int "(in Python v3.8)")\] | [None](https://docs.python.org/3.8/library/constants.html#None "(in Python v3.8)") = None*) [¶](Database%20API.md#pyCRS.Database.COSKFDatabase.estimate_physical_property)

Estimate the physical properties using the property prediction tool and add the values to the PropPred TABLE in the database

Keyword Arguments:

- **identifier** (`str or List[str], optioanl`) – CAS number, chemical identifier or compound name as a string or a list of strings.
- **compound\_id** (`int or List[int], optional`) – an integer or a list representing the compound ID(s).

> [!note] Note
> The QSPR descriptor used in the property prediction tool is determined from the SMILES string. The selection priority of SMILES is as follows: (1) User-provided SMILES via the `add_compound()` method. (2) SMILES read from the **.coskf** file. (3) SMILES generated by OpenBabel using the compound’s coordinates in the **.coskf** file. Please note that the automatically resolved SMILES may be incorrect for some molecules, for instance when bond orders cannot be automatically determined and species with charges.

```python
db.estimate_physical_property("Benzene")
```

get\_all\_compounds() → [List](https://docs.python.org/3.8/library/typing.html#typing.List "(in Python v3.8)") \[\] [¶](Database%20API.md#pyCRS.Database.COSKFDatabase.get_all_compounds)

Retrive all compounds in the database

Returns:

The full list of CompoundRow instances in the database

Return type:

List\[\]

get\_all\_conformers() → [List](https://docs.python.org/3.8/library/typing.html#typing.List "(in Python v3.8)") \[\] [¶](Database%20API.md#pyCRS.Database.COSKFDatabase.get_all_conformers)

Retrives all conformers in the database

Returns:

The full list of ConformerRow instances in the database.

Return type:

List\[\]

get\_all\_physical\_properties(*source: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)") = 'PhysicalProperty'*) → [List](https://docs.python.org/3.8/library/typing.html#typing.List "(in Python v3.8)") \[\] | [List](https://docs.python.org/3.8/library/typing.html#typing.List "(in Python v3.8)") \[\] [¶](Database%20API.md#pyCRS.Database.COSKFDatabase.get_all_physical_properties)

Retrive all physical properties in the database

Parameters:

**source** (`str, optional`) – Source of the properties. - ‘PhysicalProperty’ (default): Returns properties from the **PhysicalProperty** table. - ‘PropPred’: Returns estimated properties from the **PropPred** table.

Returns:

A list of PhysicalPropertyRow instances or PropPredRow instances in the database.

Return type:

List() or List()

get\_attribute\_by\_compound\_id(*attributes: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)") | [List](https://docs.python.org/3.8/library/typing.html#typing.List "(in Python v3.8)") \[[str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")\]*, *compound\_id: [int](https://docs.python.org/3.8/library/functions.html#int "(in Python v3.8)") | [List](https://docs.python.org/3.8/library/typing.html#typing.List "(in Python v3.8)") \[[int](https://docs.python.org/3.8/library/functions.html#int "(in Python v3.8)")\]*, *source: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)") | [List](https://docs.python.org/3.8/library/typing.html#typing.List "(in Python v3.8)") \[[str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")\] | [None](https://docs.python.org/3.8/library/constants.html#None "(in Python v3.8)") = None*) [¶](Database%20API.md#pyCRS.Database.COSKFDatabase.get_attribute_by_compound_id)

Retrieve the list of values for compounds with specified compound\_id(s) in the database

Parameters:

- **attributes** (`str or List[str]`) – Attribute(s) to be retrieved.
- **compound\_id** (`int or List[int]`) – A integer or a list of intergers used to search for compounds in the COMPOUND TABLE.
- **source** (`str or List[str], optional`) – The table used in the search. Default is COMPOUND TABLE and PhysicalProperty TABLE

Returns:

A list of tuples containing the values of the specified attributes for the compounds.

Return type:

[list](https://docs.python.org/3.8/library/stdtypes.html#list "(in Python v3.8)") of attributes

```python
db.get_attribute_by_compound_id("name", 1)
db.get_attribute_by_compound_id(["name", "cas", "hfusion"] 1)
db.get_attribute_by_compound_id(["name", "hfusion"], 1, source=["COMPOUND","PropPred"])
```

get\_compounds(*identifier: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)") | [List](https://docs.python.org/3.8/library/typing.html#typing.List "(in Python v3.8)") \[[str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")\]*) → [Dict](https://docs.python.org/3.8/library/typing.html#typing.Dict "(in Python v3.8)") \[[str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)"), \] [¶](Database%20API.md#pyCRS.Database.COSKFDatabase.get_compounds)

Retrieves compounds from the COMPOUND TABLE in the database by matching CAS number, chemical identifier, or name.

Parameters:

**identifier** (`str or List[str]`) – CAS number, chemical identifier or compound name as a string or a list of strings.

Returns:

A dictionary where each key is an input identifier and its corresponding value is the **CompoundRow** instances.

Return type:

Dict\[[str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)"), \]

get\_compounds\_id(*identifier: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)") | [List](https://docs.python.org/3.8/library/typing.html#typing.List "(in Python v3.8)") \[[str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")\]*) → [List](https://docs.python.org/3.8/library/typing.html#typing.List "(in Python v3.8)") \[[int](https://docs.python.org/3.8/library/functions.html#int "(in Python v3.8)") | [None](https://docs.python.org/3.8/library/constants.html#None "(in Python v3.8)")\] [¶](Database%20API.md#pyCRS.Database.COSKFDatabase.get_compounds_id)

Retrieves compound id from the COMPOUND TABLE in the database by matching CAS number, chemical identifier, or name.

Parameters:

**identifier** (`str or List[str]`) – CAS number, chemical identifier or compound name as a string or a list of strings.

Returns:

A list of compound IDs corresponding to the input identifier. If a name is not found, None is returned at the corresponding position.

Return type:

List\[Optional\[[int](https://docs.python.org/3.8/library/functions.html#int "(in Python v3.8)")\]\]

get\_conformers(*identifier: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)") | [List](https://docs.python.org/3.8/library/typing.html#typing.List "(in Python v3.8)") \[[str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")\]*) → [Dict](https://docs.python.org/3.8/library/typing.html#typing.Dict "(in Python v3.8)") \[[str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)"), \] [¶](Database%20API.md#pyCRS.Database.COSKFDatabase.get_conformers)

Retrieves conformers from the CONFORMER TABLE in the database by matching CAS number, chemical identifier, or name.

Parameters:

**identifier** (`str or list`) – CAS number, chemical identifier or compound name as a string or a list of strings.

Returns:

A list of ConformerRow instances that match the search criteria.

Return type:

Dict\[[str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)"), \]

get\_physical\_properties(*identifier: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)") | [List](https://docs.python.org/3.8/library/typing.html#typing.List "(in Python v3.8)") \[[str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")\] | [None](https://docs.python.org/3.8/library/constants.html#None "(in Python v3.8)") = None*, *compound\_id: [int](https://docs.python.org/3.8/library/functions.html#int "(in Python v3.8)") | [List](https://docs.python.org/3.8/library/typing.html#typing.List "(in Python v3.8)") \[[int](https://docs.python.org/3.8/library/functions.html#int "(in Python v3.8)")\] | [None](https://docs.python.org/3.8/library/constants.html#None "(in Python v3.8)") = None*, *source: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)") = 'PhysicalProperty'*) → [List](https://docs.python.org/3.8/library/typing.html#typing.List "(in Python v3.8)") \[\] | [List](https://docs.python.org/3.8/library/typing.html#typing.List "(in Python v3.8)") \[\] [¶](Database%20API.md#pyCRS.Database.COSKFDatabase.get_physical_properties)

Retrive physical properties in the database by matching CAS number, chemical identifier, name or compound id.

Parameters:

- **identifier** (`str or List[str], optional`) – CAS number, chemical identifier or compound name as a string or a list of strings. If None, `compound_id` must be provided.
- **compound\_id** (`int or List[int], optional`) – Compound ID as an integer or a list of integers. If None, `identifier` must be provided.
- **source** (`str, optional`) – Source of the properties. - ‘PhysicalProperty’ (default): Returns properties from the **PhysicalProperty** table. - ‘PropPred’: Returns estimated properties from the **PropPred** table.

Returns:

A list of **PhysicalPropertyRow** or **PropPredRow** instances, depending on the source.

Return type:

List\[\] or List\[\]

modify\_attribute\_by\_compound\_id(*attribute: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")*, *value: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)") | [int](https://docs.python.org/3.8/library/functions.html#int "(in Python v3.8)")*, *compound\_id: [int](https://docs.python.org/3.8/library/functions.html#int "(in Python v3.8)")*) [¶](Database%20API.md#pyCRS.Database.COSKFDatabase.modify_attribute_by_compound_id)

Modifies the value of a specified attribute for a given compound ID.

Parameters:

- **attribute** ([`str`](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")) – Attribute to modify. It can be one of the following: ‘name’, ‘cas’, ‘identifier’, ‘smiles’, ‘nring’.
- **value** (`str or int`) – the new value of the specified attribute.
- **compound\_id** ([`int`](https://docs.python.org/3.8/library/functions.html#int "(in Python v3.8)")) – an integer representing the compound ID.

```python
db.modify_attribute_by_compound_id("identifier","InChI=1S/C6H6/c1-2-4-6-5-3-1/h1-6H", 0)
```

update\_compound\_by\_conformer\_id(*compound\_id: [int](https://docs.python.org/3.8/library/functions.html#int "(in Python v3.8)")*, *conformer\_id: [int](https://docs.python.org/3.8/library/functions.html#int "(in Python v3.8)")*) [¶](Database%20API.md#pyCRS.Database.COSKFDatabase.update_compound_by_conformer_id)

Update the data for a compound ID row in the COMPOUND TABLE using the data from a conformer ID row in the CONFORMER TABLE.

Parameters:

- **compound\_id** ([`int`](https://docs.python.org/3.8/library/functions.html#int "(in Python v3.8)")) – A integer representing compound id corresponding to a specific row in the COMPOUND TABLE of the database
- **conformer\_id** ([`int`](https://docs.python.org/3.8/library/functions.html#int "(in Python v3.8)")) – A integer representing conformer id corresponding to a specific row in the CONFORMER TABLE of the database

update\_compound\_by\_lowestE(*compound\_id: [int](https://docs.python.org/3.8/library/functions.html#int "(in Python v3.8)") | [List](https://docs.python.org/3.8/library/typing.html#typing.List "(in Python v3.8)") \[[int](https://docs.python.org/3.8/library/functions.html#int "(in Python v3.8)")\] | [None](https://docs.python.org/3.8/library/constants.html#None "(in Python v3.8)") = None*) [¶](Database%20API.md#pyCRS.Database.COSKFDatabase.update_compound_by_lowestE)

Update the data for a compound ID row in the COMPOUND TABLE using the data from a conformer ID row with the lowest energy having the same compound ID in the CONFORMER TABLE.

Keyword Arguments:

**compound\_id** (`int or List[int], optional`) – Compound ID as an integer or a list of integers. If None, updates all compounds in the database.

visualize\_conformers(*compound\_id: [int](https://docs.python.org/3.8/library/functions.html#int "(in Python v3.8)") | [None](https://docs.python.org/3.8/library/constants.html#None "(in Python v3.8)") = None*, *identifier: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)") | [None](https://docs.python.org/3.8/library/constants.html#None "(in Python v3.8)") = None*) [¶](Database%20API.md#pyCRS.Database.COSKFDatabase.visualize_conformers)

Visualize conformers in ascending order of conformers IDs.

Parameters:

- **compound\_id** (`int, optional`) – Compound ID for which conformers are visualized.
- **identifier** (`str, optional`) – CAS number, chemical identifier or compound name.

*class* pyCRS.Database.CompoundRow(*compound\_id: [int](https://docs.python.org/3.8/library/functions.html#int "(in Python v3.8)")*, *conformer\_id: [int](https://docs.python.org/3.8/library/functions.html#int "(in Python v3.8)")*, *name: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")*, *cas: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")*, *identifier: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")*, *smiles: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")*, *resolved\_smiles: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")*, *coskf: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")*, *Egas: [float](https://docs.python.org/3.8/library/functions.html#float "(in Python v3.8)")*, *Ecosmo: [float](https://docs.python.org/3.8/library/functions.html#float "(in Python v3.8)")*, *nring: [int](https://docs.python.org/3.8/library/functions.html#int "(in Python v3.8)")*) [¶](Database%20API.md#pyCRS.Database.CompoundRow)

A data class to represent the contents of a row in a COMPOUND TABLE in `COSKFDatabase`

compound\_id [¶](Database%20API.md#pyCRS.Database.CompoundRow.compound_id)

A unique identifer for a specific row in the COMPOUND TABLE of the database

Type:

[`int`](https://docs.python.org/3.8/library/functions.html#int "(in Python v3.8)")

conformer\_id [¶](Database%20API.md#pyCRS.Database.CompoundRow.conformer_id)

A unique identifer for a specific row in the CONFORMER TABLE of the database

Type:

[`int`](https://docs.python.org/3.8/library/functions.html#int "(in Python v3.8)")

name [¶](Database%20API.md#pyCRS.Database.CompoundRow.name)

The name associated with the row in the COMPOUND TABLE

Type:

[`str`](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")

cas [¶](Database%20API.md#pyCRS.Database.CompoundRow.cas)

The CAS number associated with the row, i.e., the compound

Type:

[`str`](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")

identifier [¶](Database%20API.md#pyCRS.Database.CompoundRow.identifier)

The chemical identifier associated with the row, i.e., the compound

Type:

[`str`](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")

smiles [¶](Database%20API.md#pyCRS.Database.CompoundRow.smiles)

The SMILES string provided by user

Type:

[`str`](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")

resolved\_smiles [¶](Database%20API.md#pyCRS.Database.CompoundRow.resolved_smiles)

The derived SMILES string obtained using OpenBabel from the coordinates in the COSKF file.

Type:

[`str`](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")

coskf [¶](Database%20API.md#pyCRS.Database.CompoundRow.coskf)

The filename of the `.coskf` file stored in the local `SCM_PYCRS_COSKF_DB` directory

Type:

[`str`](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")

Egas [¶](Database%20API.md#pyCRS.Database.CompoundRow.Egas)

The gas phase bond energy rounded to 3 decimal places in kcal/mol

Type:

[`float`](https://docs.python.org/3.8/library/functions.html#float "(in Python v3.8)")

Ecosmo [¶](Database%20API.md#pyCRS.Database.CompoundRow.Ecosmo)

The bond energy in a perfect conductor rounded to 3 decimal places in kcal/mol

Type:

[`float`](https://docs.python.org/3.8/library/functions.html#float "(in Python v3.8)")

nring [¶](Database%20API.md#pyCRS.Database.CompoundRow.nring)

The number of ring atoms

Type:

[`int`](https://docs.python.org/3.8/library/functions.html#int "(in Python v3.8)")

db\_path [¶](Database%20API.md#pyCRS.Database.CompoundRow.db_path)

The path to the `.coskf` file directory

Type:

[`str`](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")

get\_full\_coskf\_path() [¶](Database%20API.md#pyCRS.Database.CompoundRow.get_full_coskf_path)

Returns the full path of the corresponding `.coskf` file

read\_coskf() [¶](Database%20API.md#pyCRS.Database.CompoundRow.read_coskf)

Opens the `.coskf` file corresponding to the database entry and returns a scm.plams.KFFile instance

*class* pyCRS.Database.ConformerRow(*conformer\_id: [int](https://docs.python.org/3.8/library/functions.html#int "(in Python v3.8)")*, *compound\_id: [int](https://docs.python.org/3.8/library/functions.html#int "(in Python v3.8)")*, *name: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")*, *cas: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")*, *identifier: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")*, *smiles: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")*, *resolved\_smiles: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")*, *coskf: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")*, *Egas: [float](https://docs.python.org/3.8/library/functions.html#float "(in Python v3.8)")*, *Ecosmo: [float](https://docs.python.org/3.8/library/functions.html#float "(in Python v3.8)")*, *nring: [int](https://docs.python.org/3.8/library/functions.html#int "(in Python v3.8)")*) [¶](Database%20API.md#pyCRS.Database.ConformerRow)

A data class to represent the contents of a row in a CONFORMER TABLE in `COSKFDatabase`

conformer\_id [¶](Database%20API.md#pyCRS.Database.ConformerRow.conformer_id)

A unique identifer for a specific row in the CONFORMER TABLE of the database

Type:

[`int`](https://docs.python.org/3.8/library/functions.html#int "(in Python v3.8)")

compound\_id [¶](Database%20API.md#pyCRS.Database.ConformerRow.compound_id)

A unique identifer for a specific row in the COMPOUND TABLE of the database

Type:

[`int`](https://docs.python.org/3.8/library/functions.html#int "(in Python v3.8)")

name [¶](Database%20API.md#pyCRS.Database.ConformerRow.name)

The name associated with the row in the CONFORMER TABLE

Type:

[`str`](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")

cas [¶](Database%20API.md#pyCRS.Database.ConformerRow.cas)

The CAS number associated with the row, i.e., the compound

Type:

[`str`](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")

identifier [¶](Database%20API.md#pyCRS.Database.ConformerRow.identifier)

The chemical identifier associated with the row, i.e., the compound

Type:

[`str`](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")

smiles [¶](Database%20API.md#pyCRS.Database.ConformerRow.smiles)

The SMILES string provided by user

Type:

[`str`](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")

resolved\_smiles [¶](Database%20API.md#pyCRS.Database.ConformerRow.resolved_smiles)

The derived SMILES string obtained using OpenBabel from the coordinates in the COSKF file

Type:

[`str`](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")

coskf [¶](Database%20API.md#pyCRS.Database.ConformerRow.coskf)

The filename of the `.coskf` file stored in the local `SCM_PYCRS_COSKF_DB` directory

Type:

[`str`](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")

Egas [¶](Database%20API.md#pyCRS.Database.ConformerRow.Egas)

The gas phase bond energy rounded to 3 decimal places in kcal/mol

Type:

[`float`](https://docs.python.org/3.8/library/functions.html#float "(in Python v3.8)")

Ecosmo [¶](Database%20API.md#pyCRS.Database.ConformerRow.Ecosmo)

The bond energy in a perfect conductor rounded to 3 decimal places in kcal/mol

Type:

[`float`](https://docs.python.org/3.8/library/functions.html#float "(in Python v3.8)")

nring [¶](Database%20API.md#pyCRS.Database.ConformerRow.nring)

The number of ring atoms

Type:

[`int`](https://docs.python.org/3.8/library/functions.html#int "(in Python v3.8)")

db\_path [¶](Database%20API.md#pyCRS.Database.ConformerRow.db_path)

The path to the `.coskf` file directory

Type:

[`str`](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")

get\_full\_coskf\_path() [¶](Database%20API.md#pyCRS.Database.ConformerRow.get_full_coskf_path)

Returns the full path of the corresponding `.coskf` file

read\_coskf() [¶](Database%20API.md#pyCRS.Database.ConformerRow.read_coskf)

Opens the `.coskf` file corresponding to the database entry and returns a scm.plams.KFFile instance

*class* pyCRS.Database.PhysicalPropertyRow(*compound\_id: [int](https://docs.python.org/3.8/library/functions.html#int "(in Python v3.8)")*, *meltingpoint: [float](https://docs.python.org/3.8/library/functions.html#float "(in Python v3.8)")*, *hfusion: [float](https://docs.python.org/3.8/library/functions.html#float "(in Python v3.8)")*, *cpfusion: [float](https://docs.python.org/3.8/library/functions.html#float "(in Python v3.8)")*, *boilingpoint: [float](https://docs.python.org/3.8/library/functions.html#float "(in Python v3.8)")*, *density: [float](https://docs.python.org/3.8/library/functions.html#float "(in Python v3.8)")*, *flashpoint: [float](https://docs.python.org/3.8/library/functions.html#float "(in Python v3.8)")*, *dielectricconstant: [float](https://docs.python.org/3.8/library/functions.html#float "(in Python v3.8)")*, *vp\_equation: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")*, *vp\_params: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")*, *tvap: [float](https://docs.python.org/3.8/library/functions.html#float "(in Python v3.8)")*, *pvap: [float](https://docs.python.org/3.8/library/functions.html#float "(in Python v3.8)")*, *Mn: [float](https://docs.python.org/3.8/library/functions.html#float "(in Python v3.8)")*) [¶](Database%20API.md#pyCRS.Database.PhysicalPropertyRow)

A data class to represent the contents of a row in a PhysicalProperty TABLE in `COSKFDatabase`

compound\_id [¶](Database%20API.md#pyCRS.Database.PhysicalPropertyRow.compound_id)

A unique identifer for a specific row in the COMPOUND TABLE of the database

Type:

[`int`](https://docs.python.org/3.8/library/functions.html#int "(in Python v3.8)")

meltingpoint [¶](Database%20API.md#pyCRS.Database.PhysicalPropertyRow.meltingpoint)

melting temperature (K)

Type:

[`float`](https://docs.python.org/3.8/library/functions.html#float "(in Python v3.8)")

hfusion [¶](Database%20API.md#pyCRS.Database.PhysicalPropertyRow.hfusion)

enthalpy of husion (kcal/mol)

Type:

[`float`](https://docs.python.org/3.8/library/functions.html#float "(in Python v3.8)")

cpfusion [¶](Database%20API.md#pyCRS.Database.PhysicalPropertyRow.cpfusion)

heat capacity of fusion (kcal/mol-K) calculated as the difference between the heat capacity in the liquid state and the heat capacity in the solid state.

Type:

[`float`](https://docs.python.org/3.8/library/functions.html#float "(in Python v3.8)")

boilingpoint [¶](Database%20API.md#pyCRS.Database.PhysicalPropertyRow.boilingpoint)

boiling pointK (K)

Type:

[`float`](https://docs.python.org/3.8/library/functions.html#float "(in Python v3.8)")

density [¶](Database%20API.md#pyCRS.Database.PhysicalPropertyRow.density)

liquid density (kg/L)

Type:

[`float`](https://docs.python.org/3.8/library/functions.html#float "(in Python v3.8)")

flashpoint [¶](Database%20API.md#pyCRS.Database.PhysicalPropertyRow.flashpoint)

flash point (K)

Type:

[`float`](https://docs.python.org/3.8/library/functions.html#float "(in Python v3.8)")

dielectricconstant [¶](Database%20API.md#pyCRS.Database.PhysicalPropertyRow.dielectricconstant)

dielectric constant

Type:

`flash`

vp\_equation [¶](Database%20API.md#pyCRS.Database.PhysicalPropertyRow.vp_equation)

The vapor pressure equation to use. Unit in bar. Options include: ANTOINE, VPM1 and DIPPR101

Type:

[`str`](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")

vp\_params [¶](Database%20API.md#pyCRS.Database.PhysicalPropertyRow.vp_params)

Parameters for the vp\_equation, expressed as “A, B, C, D, E”

Type:

[`str`](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")

tvap [¶](Database%20API.md#pyCRS.Database.PhysicalPropertyRow.tvap)

Temperature(K) at pvap

Type:

[`float`](https://docs.python.org/3.8/library/functions.html#float "(in Python v3.8)")

pvap [¶](Database%20API.md#pyCRS.Database.PhysicalPropertyRow.pvap)

Pressure(bar) at tvap

Type:

[`float`](https://docs.python.org/3.8/library/functions.html#float "(in Python v3.8)")

Mn [¶](Database%20API.md#pyCRS.Database.PhysicalPropertyRow.Mn)

polymer average molecular weight (g/mol)

Type:

[`float`](https://docs.python.org/3.8/library/functions.html#float "(in Python v3.8)")

Vapor Pressure Equations:

ANTOINE:

log10(P) = A - B/(C+T)

DIPPR101:

ln(P) = A + B/T + C\*ln(T) + D\*T\*\*E

VPM1:

ln(P) = A/T + B\*ln(T) + C\*T + D

*class* pyCRS.Database.PropPredRow(*compound\_id: [int](https://docs.python.org/3.8/library/functions.html#int "(in Python v3.8)")*, *adopt\_smiles: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")*, *meltingpoint: [float](https://docs.python.org/3.8/library/functions.html#float "(in Python v3.8)")*, *hfusion: [float](https://docs.python.org/3.8/library/functions.html#float "(in Python v3.8)")*, *boilingpoint: [float](https://docs.python.org/3.8/library/functions.html#float "(in Python v3.8)")*, *density: [float](https://docs.python.org/3.8/library/functions.html#float "(in Python v3.8)")*, *flashpoint: [float](https://docs.python.org/3.8/library/functions.html#float "(in Python v3.8)")*, *dielectricconstant: [float](https://docs.python.org/3.8/library/functions.html#float "(in Python v3.8)")*, *vp\_equation: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")*, *vp\_params: [str](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")*) [¶](Database%20API.md#pyCRS.Database.PropPredRow)

A data class to represent the contents of a row in a PropPred TABLE in `COSKFDatabase`

compound\_id [¶](Database%20API.md#pyCRS.Database.PropPredRow.compound_id)

A unique identifer for a specific row in the COMPOUND TABLE of the database

Type:

[`int`](https://docs.python.org/3.8/library/functions.html#int "(in Python v3.8)")

adopt\_smiles [¶](Database%20API.md#pyCRS.Database.PropPredRow.adopt_smiles)

The SMILES used for QSPR method

Type:

[`str`](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")

meltingpoint [¶](Database%20API.md#pyCRS.Database.PropPredRow.meltingpoint)

melting temperature (K)

Type:

[`float`](https://docs.python.org/3.8/library/functions.html#float "(in Python v3.8)")

hfusion [¶](Database%20API.md#pyCRS.Database.PropPredRow.hfusion)

enthalpy of husion (kcal/mol)

Type:

[`float`](https://docs.python.org/3.8/library/functions.html#float "(in Python v3.8)")

boilingpoint [¶](Database%20API.md#pyCRS.Database.PropPredRow.boilingpoint)

boiling pointK (K)

Type:

[`float`](https://docs.python.org/3.8/library/functions.html#float "(in Python v3.8)")

density [¶](Database%20API.md#pyCRS.Database.PropPredRow.density)

liquid density (kg/L)

Type:

[`float`](https://docs.python.org/3.8/library/functions.html#float "(in Python v3.8)")

flashpoint [¶](Database%20API.md#pyCRS.Database.PropPredRow.flashpoint)

flash point (K)

Type:

[`float`](https://docs.python.org/3.8/library/functions.html#float "(in Python v3.8)")

dielectricconstant [¶](Database%20API.md#pyCRS.Database.PropPredRow.dielectricconstant)

dielectric constant

Type:

`flash`

vp\_equation [¶](Database%20API.md#pyCRS.Database.PropPredRow.vp_equation)

The vapor pressure equation to use. Unit in bar. VPM1

Type:

[`str`](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")

vp\_params [¶](Database%20API.md#pyCRS.Database.PropPredRow.vp_params)

Parameters for the vp\_equation, expressed as “A, B, C, D, E”

Type:

[`str`](https://docs.python.org/3.8/library/stdtypes.html#str "(in Python v3.8)")