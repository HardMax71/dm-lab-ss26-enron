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

## `title_supplement.csv`

A small follow-up layer that fills in some of the people Shetty-Adibi left blank.
`enrich_people.py` applies it only to owners whose Shetty-Adibi title is `N/A`,
so the original annotation is never overwritten. It fills 11 of the 32 blanks
and leaves the other 21 as `N/A` rather than guess.

Each row carries its own `title_source` and a `title_note` giving the precise
title and the evidence behind it. Two kinds of evidence were used, in this order
of preference:

- **`corpus-signature`**: the role the person states in their own sent-mail
  signature (for example Marie Heard signs "Senior Legal Specialist" 117 times,
  Kim Ward "Manager, West Gas Origination" 22 times). This is self-stated and
  needs no external lookup, so it is the most reliable source for the obscure
  owners.
- **`web`**: a publicly documented role for the few people who have one (Gerald
  Nemec's Senior Counsel ENA bio, Kimberly Watson's pipeline-journal profile).
  Used only where the person is clearly identifiable; common names with no
  disambiguation were left `N/A`.

The `title` column itself stays in the same nine-bucket vocabulary as
Shetty-Adibi (the precise wording lives in `title_note`), so the cross-tabs that
read `title` are unaffected. One row is an identity correction as much as a
title: owner `whalley-l` sends entirely as `liz.taylor@enron.com` and signs on
behalf of Greg Whalley, so it is Whalley's assistant Liz Taylor, not Greg
Whalley himself (who is owner `whalley-g`).
