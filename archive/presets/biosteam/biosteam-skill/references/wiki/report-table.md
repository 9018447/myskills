# report-table

## Overview

Directory-based community: biosteam/report

- **Size**: 32 nodes
- **Cohesion**: 0.0856
- **Dominant Language**: python

## Members

| Name | Kind | File | Lines |
|------|------|------|-------|
| plot_cost_summary | Function | /media/smh/d/4-latex/2-MDPHDS/codespace/biosteam/biosteam/report/plot.py | 16-62 |
| _stream_key | Function | /media/smh/d/4-latex/2-MDPHDS/codespace/biosteam/biosteam/report/table.py | 34-37 |
| _reformat | Function | /media/smh/d/4-latex/2-MDPHDS/codespace/biosteam/biosteam/report/table.py | 39-42 |
| FOCTableBuilder | Class | /media/smh/d/4-latex/2-MDPHDS/codespace/biosteam/biosteam/report/table.py | 46-72 |
| __init__ | Function | /media/smh/d/4-latex/2-MDPHDS/codespace/biosteam/biosteam/report/table.py | 49-52 |
| entry | Function | /media/smh/d/4-latex/2-MDPHDS/codespace/biosteam/biosteam/report/table.py | 54-57 |
| table | Function | /media/smh/d/4-latex/2-MDPHDS/codespace/biosteam/biosteam/report/table.py | 59-72 |
| voc_table | Function | /media/smh/d/4-latex/2-MDPHDS/codespace/biosteam/biosteam/report/table.py | 76-202 |
| getsubdct | Function | /media/smh/d/4-latex/2-MDPHDS/codespace/biosteam/biosteam/report/table.py | 91-96 |
| reformat | Function | /media/smh/d/4-latex/2-MDPHDS/codespace/biosteam/biosteam/report/table.py | 339-342 |
| lca_characterization_factor_table | Function | /media/smh/d/4-latex/2-MDPHDS/codespace/biosteam/biosteam/report/table.py | 204-293 |
| set_value | Function | /media/smh/d/4-latex/2-MDPHDS/codespace/biosteam/biosteam/report/table.py | 403-408 |
| lca_inventory_table | Function | /media/smh/d/4-latex/2-MDPHDS/codespace/biosteam/biosteam/report/table.py | 295-390 |
| lca_displacement_allocation_table | Function | /media/smh/d/4-latex/2-MDPHDS/codespace/biosteam/biosteam/report/table.py | 392-502 |
| lca_property_allocation_factor_table | Function | /media/smh/d/4-latex/2-MDPHDS/codespace/biosteam/biosteam/report/table.py | 504-526 |
| lca_displacement_allocation_factor_table | Function | /media/smh/d/4-latex/2-MDPHDS/codespace/biosteam/biosteam/report/table.py | 528-550 |
| environmental_impacts_table | Function | /media/smh/d/4-latex/2-MDPHDS/codespace/biosteam/biosteam/report/table.py | 552-568 |
| tables_to_excel | Function | /media/smh/d/4-latex/2-MDPHDS/codespace/biosteam/biosteam/report/table.py | 572-602 |
| unit_reaction_tables | Function | /media/smh/d/4-latex/2-MDPHDS/codespace/biosteam/biosteam/report/table.py | 606-622 |
| unit_result_tables | Function | /media/smh/d/4-latex/2-MDPHDS/codespace/biosteam/biosteam/report/table.py | 624-684 |
| cost_table | Function | /media/smh/d/4-latex/2-MDPHDS/codespace/biosteam/biosteam/report/table.py | 686-723 |
| heat_utility_tables | Function | /media/smh/d/4-latex/2-MDPHDS/codespace/biosteam/biosteam/report/table.py | 725-768 |
| power_utility_table | Function | /media/smh/d/4-latex/2-MDPHDS/codespace/biosteam/biosteam/report/table.py | 771-791 |
| other_utilities_table | Function | /media/smh/d/4-latex/2-MDPHDS/codespace/biosteam/biosteam/report/table.py | 793-827 |
| stream_tables | Function | /media/smh/d/4-latex/2-MDPHDS/codespace/biosteam/biosteam/report/table.py | 845-857 |
| stream_table | Function | /media/smh/d/4-latex/2-MDPHDS/codespace/biosteam/biosteam/report/table.py | 859-933 |
| water_mass_balance_table | Function | /media/smh/d/4-latex/2-MDPHDS/codespace/biosteam/biosteam/report/table.py | 935-936 |
| mass_balance_table | Function | /media/smh/d/4-latex/2-MDPHDS/codespace/biosteam/biosteam/report/table.py | 938-1060 |
| feed_ | Function | /media/smh/d/4-latex/2-MDPHDS/codespace/biosteam/biosteam/report/table.py | 962-971 |
| recycle_ | Function | /media/smh/d/4-latex/2-MDPHDS/codespace/biosteam/biosteam/report/table.py | 973-982 |
| lost_ | Function | /media/smh/d/4-latex/2-MDPHDS/codespace/biosteam/biosteam/report/table.py | 984-993 |
| reacted_ | Function | /media/smh/d/4-latex/2-MDPHDS/codespace/biosteam/biosteam/report/table.py | 995-1007 |

## Execution Flows

- **water_mass_balance_table** (criticality: 0.37, depth: 2)

## Dependencies

### Outgoing

- `append` (48 edge(s))
- `sum` (33 edge(s))
- `sorted` (33 edge(s))
- `len` (26 edge(s))
- `set` (18 edge(s))
- `enumerate` (15 edge(s))
- `items` (15 edge(s))
- `DataFrame` (14 edge(s))
- `any` (14 edge(s))
- `isa` (10 edge(s))
- `tuple` (8 edge(s))
- `isempty` (8 edge(s))
- `replace` (7 edge(s))
- `get_CF` (7 edge(s))
- `from_tuples` (6 edge(s))

### Incoming

- `/media/smh/d/4-latex/2-MDPHDS/codespace/biosteam/biosteam/report/table.py` (32 edge(s))
- `/media/smh/d/4-latex/2-MDPHDS/codespace/biosteam/biosteam/report/plot.py` (1 edge(s))
