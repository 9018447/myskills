# OpenAlex Filters Reference

Filters are passed to the `list` command using the `--filter` argument.
Format: `attribute:value`.
Multiple filters can be combined with commas (AND logic).

## Common Filters

### Works
- `type:article` - Filter by work type (article, book-chapter, dataset, etc.)
- `publication_year:2023` - Published in a specific year.
- `publication_year:>2020` - Published after 2020.
- `is_oa:true` - Is Open Access.
- `has_fulltext:true` - Has full text available.
- `author.id:A5045981348` - By a specific author.
- `institutions.id:I161046081` - From a specific institution.
- `primary_location.source.id:S106296714` - Published in a specific source (journal/conference).

### Authors
- `works_count:>100` - Authors with more than 100 works.
- `last_known_institution.id:I161046081` - Affiliated with a specific institution.
- `h_index:>50` - High H-index.

### Institutions
- `country_code:US` - Institutions in the US.
- `type:education` - Universities/Colleges.

### Operators
- `attribute:value` - Equal.
- `attribute:!value` - Not equal.
- `attribute:>value` - Greater than.
- `attribute:<value` - Less than.

See https://docs.openalex.org/how-to-use-the-api/get-lists-of-entities/filter-entity-lists for full documentation.
