# External reference data

## `enron_employeelist.csv`

Per-person job titles for the Enron mailbox owners, the annotation published by
**Jitesh Shetty and Jafar Adibi (USC/ISI, 2004)** as part of their MySQL version
of the Enron corpus. One row per mailbox folder, with the person's name, known
e-mail addresses, the folder handle (`Ordner`), and a `status` field giving the
job title (CEO, President, Vice President, Managing Director, Director, Manager,
Trader, In House Lawyer, Employee, or blank for unknown/N-A).

- **Source mirror:** https://github.com/ahr85/enron (`E-Mails-updated.csv`), a
  CSV mirror of the Shetty-Adibi `employeelist` table.
- **Original:** Shetty, J. and Adibi, J. (2004), *The Enron email dataset
  database schema and brief statistical report*, USC Information Sciences
  Institute. See also the Enron Corpus Wikipedia article.
- **Coverage:** 149 rows, one per folder handle, joining 1:1 onto the 149
  resolved mailbox owners in `eda-5/clean/people.parquet` (the folder roster is
  the same list).

### Caveats
The titles are a point-in-time, partly hand-imputed annotation, not an HR
export. About half the people are `Employee` (41) or blank/N-A (32), so the
fine-grained seniority signal only covers the other half. Titles are used here
as an external label to validate and characterise the behavioural clusters, and
are kept strictly separate from the corpus-derived tables; every column that
comes from this file is marked with `title_source` in `people_roles.parquet`.
