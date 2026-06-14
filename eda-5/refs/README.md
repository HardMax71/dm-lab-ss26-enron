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

A follow-up layer that fills in the people Shetty-Adibi left blank.
`enrich_people.py` applies it only to owners whose Shetty-Adibi title is `N/A`,
so the original annotation is never overwritten. It fills **all 32** blanks, so
every one of the 149 owners now has a title. The hardest case, `merriss-s`, has
only 13 messages in his mailbox because he was a brand-new hire: his own mail
says "I just started in realtime a couple weeks ago", and the corpus records
"Steve Merriss has joined the Real Time group", placing him on the West real-time
power desk.

Each row carries its own `title_source` and a `title_note` with the precise
title and the evidence. The sources, in order of confidence:

- **`corpus-signature`**: the role the person states in their own sent-mail
  signature (Marie Heard signs "Senior Legal Specialist" 117 times, Kim Ward
  "Manager, West Gas Origination" 22 times, Stacey White "Director, Power Risk
  Management"). Self-stated, no external lookup, the most reliable source.
- **`corpus-mention`**: how other people introduce them in the corpus, when it
  is explicit and repeated ("Bill Rapp, an ETS attorney", "Mike McConnell,
  President and CEO of Enron Global Markets", staff calling "my manager, Chris
  Stokley"). Reliable when several independent mentions agree.
- **`corpus-context`**: a desk-level inference from softer evidence, where a
  precise title was not stated ("trader on the West desk", "more origination
  experience than trading"). These rows are marked tentative in the note and
  are the ones to treat with most caution.
- **`web`**: appended where a public bio confirms the corpus reading (Gerald
  Nemec's Senior Counsel ENA bio, Kimberly Watson's pipeline-journal profile).
  The obscure majority have no usable web footprint, so the web only ever
  confirms, it never carries a fill on its own.

The `title` column stays in the same nine-bucket vocabulary as Shetty-Adibi (the
precise wording lives in `title_note`), so the cross-tabs that read `title` are
unaffected. Filter on `title_source` to drop the lower-confidence tiers if a
cross-tab needs only firm titles.

Two rows are identity findings as much as titles:
- `whalley-l` sends entirely as `liz.taylor@enron.com` and signs on behalf of
  Greg Whalley, so it is his assistant **Liz Taylor**, not Greg Whalley (who is
  owner `whalley-g`).
- `mcconnell-m` is 77% `mike.mcconnell@enron.com`, **Mike McConnell**, President
  and CEO of Enron Global Markets, though the mailbox also carries some mail
  from a Mark McConnell on the Transwestern desk. The display name still reads
  "Mark McConnell" from the original annotation.

## `title_corrections.csv`

A handful of owners carry a Shetty-Adibi title that the corpus flatly
contradicts. `enrich_people.py` applies this file last, overriding the title for
the listed owners (unlike the supplement, which only fills `N/A`). Because it
overwrites a vetted value, it lives in its own file, each row's `title_note`
records what Shetty-Adibi had, and the raw annotation in
`enron_employeelist.csv` is never edited.

Nine corrections, all backed by the person's own repeated signature plus
independent third-party mentions:

| owner | Shetty-Adibi | corrected to | evidence |
|---|---|---|---|
| `dasovich-j` | Employee | Vice President | signs "Vice President, Business Development" 40x |
| `taylor-m` | Employee | Vice President | signs "Vice President and General Counsel" 87x |
| `kaminski-v` | Manager | Managing Director | "Managing Director, Research" (head of Research) |
| `derrick-j` | In House Lawyer | Vice President | Executive VP and General Counsel, Enron Corp |
| `cash-m` | Employee | In House Lawyer | Assistant General Counsel, ENA |
| `mann-k` | Employee | In House Lawyer | Senior Counsel, ENA |
| `lokay-m` | Employee | Director | "Account Director, Transwestern Commercial" 37x |
| `forney-j` | Manager | Director | "Director, ERCOT / East Power Trading" |
| `baughman-d` | Trader | Manager | "Commercial Manager, Enron Power Marketing" |
| `beck-s` | Employee | Managing Director | MD Global Risk Management Ops, named COO of Enron Net Works |

These are corrections the corpus makes unavoidable (Jeff Dasovich and Mark
Taylor both sign as Vice President dozens of times, yet were annotated
"Employee"). The reconciliation was deliberately conservative: many apparent
mismatches were rejected as noise, such as a confidentiality disclaimer matching
"counsel", an assistant's title bleeding into their manager's mailbox, or
"Vice President Al Gore" appearing in a quote in Skilling's mail.

The file also carries two rows that leave the title unchanged but add a note,
flagging a mailbox that is run by an executive's assistant rather than the
executive. An identity sweep (dominant sender address versus the owner's
surname) found that `lay-k` is 94% `rosalee.fleming@` (Ken Lay's assistant) and
`skilling-j` is 79% `sherri.sera@` (Jeff Skilling's assistant), the same pattern
as `whalley-l` being Liz Taylor. The titles stay CEO, since the mailboxes belong
to Lay and Skilling, but their sent-mail behaviour is largely the assistant's.
