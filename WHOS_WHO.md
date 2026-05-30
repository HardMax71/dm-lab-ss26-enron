# Who is who at Enron

Background for anyone reading the notebooks in this repo. The Enron email
corpus is from a real US company that no longer exists, and a lot of the
analysis only makes sense once you know what the people in the From and To
fields actually did. This page is a short reference: company shape,
divisions, executive hierarchy, named-mailbox profiles for the people who
keep appearing in our plots, and a collapse timeline.

Sources are linked at the bottom. Where this page paraphrases a public
biography (mostly Wikipedia, the FERC release, and the CMU dataset page),
the wording is ours but the facts are theirs.


## The company in one paragraph

Enron Corporation was a Houston-based energy and commodities trading firm
formed in 1985 from the merger of two natural-gas pipeline companies. By
2000 it had grown into one of the largest companies in the United States,
employed around 20,600 people, and reported $101 billion in revenue. It
ran natural gas and electric power across North America and Europe,
operated the EnronOnline electronic trading platform, owned a retail
energy subsidiary (EES), a broadband subsidiary, a water-utility
subsidiary (Azurix), the Northern Natural Gas pipeline system, and
Portland General Electric. In late 2001 it collapsed in an accounting
fraud scandal and filed for Chapter 11 on December 2, 2001, at the time
the largest bankruptcy in US history.


## Business divisions in 2000-2001

The 2000 annual report grouped Enron's operating activity into four
segments. Knowing which segment a sender belonged to is usually enough
to read a message in context.

**Wholesale Services** was the trading business: natural gas, electricity,
weather, paper, metals, coal. This is where most of the corpus's volume
sits. The North American piece traded as Enron North America (ENA), with
sister operations in Europe and Asia. EnronOnline, launched in late 1999,
was its electronic trading platform and by mid-2001 had transacted over
$685 billion gross. Greg Whalley ran Wholesale Services until he was
moved up to corporate president in August 2001.

**Retail Energy Services**, marketed as Enron Energy Services or EES,
sold long-term energy management contracts directly to large
commercial and industrial end-customers in North America and Europe.
Lou Pai was the founding CEO; he had cashed out and left by mid-2001.
EES contracts were being unwound in early 2002, which is why "ees"
spikes so sharply in subject lines that quarter (see eda-3 D1).

**Transportation and Distribution** was the regulated utility piece:
the Northern Natural Gas and Transwestern interstate pipelines, plus
Portland General Electric, the Oregon electric utility Enron acquired
in 1997. The West-coast trading desk in our network plots sits in the
PGE Portland office for tax reasons, even though the traders worked
for Wholesale Services.

**Broadband Services** tried to build a national fibre network and a
market for bandwidth contracts. It never made money and was already
posting losses by Q2 2001. Ken Rice was its CEO.

Outside the four reporting segments were **Enron International** (the
overseas power-plant and infrastructure projects, run by Rebecca Mark
until 2000), **Azurix** (a publicly listed water utility, also under
Mark), the **Enron Renewable Energy Corp.** wind business, and a
handful of methanol and MTBE plants.


## The executive hierarchy

This is the senior structure during the year the corpus heavily covers
(roughly January 2000 through May 2002). Titles and start dates are from
SEC filings and the Wikipedia entries listed at the bottom of this page.

**Office of the Chairman**

- **Kenneth Lay** (`lay-k` in the corpus) — Founder, Chairman and CEO
  from 1985. Stepped down as CEO in February 2001 to make way for
  Skilling, then resumed the CEO role in August 2001 after Skilling
  resigned. Tried unsuccessfully to keep the company solvent through
  the bankruptcy. Convicted on six counts in 2006 and died of a heart
  attack before sentencing.
- **Jeffrey Skilling** (`skilling-j`) — President and COO from 1997,
  CEO February-August 2001. Resigned abruptly on August 14, 2001
  citing personal reasons. Convicted on 19 of 28 counts in 2006 and
  served the bulk of a 24-year sentence.
- **Greg Whalley** (`whalley-g`, `whalley-l`) — President and COO from
  August 2001 to bankruptcy. Came up through Wholesale Services.
  Joined UBS Warburg's post-Enron trading desk in early 2002.

**Finance and accounting**

- **Andrew Fastow** — Chief Financial Officer from 1998 to October
  2001. Architect of the off-balance-sheet partnerships (LJM1, LJM2,
  Raptor) that hid Enron's debt. Pled guilty in 2004, served six
  years. His mailbox is not in the corpus.
- **Jeff McMahon** — Treasurer until 2000, then briefly president of
  Enron Industrial Markets, then CFO from October 2001 to bankruptcy.
- **Richard Causey** — Chief Accounting Officer. Pled guilty in
  December 2005, sentenced to seven years.
- **Rick Buy** (`buy-r`) — Chief Risk Officer.
- **Ben Glisan** — Treasurer after McMahon moved up. Pled guilty in
  2003, sentenced to five years.

**Legal**

- **James Derrick** (`derrick-j`) — General Counsel of Enron Corp.
- **Mark Haedicke** (`haedicke-m`) — General Counsel of Enron
  Wholesale Services, head of the ENA legal department that the
  Shackleton / Taylor / Jones / Mann cluster reports into.

**Division CEOs and senior leaders**

- **John Lavorato** (`lavorato-j`) — President and CEO of Enron
  Americas (the North/South American part of Wholesale Services).
  Received the largest post-bankruptcy retention bonus ($5M).
- **Louise Kitchen** (`kitchen-l`) — President of Enron Online and
  later COO of Enron Americas; widely credited as the driving force
  behind EnronOnline's 1999-2000 launch. $2M retention bonus.
- **Cliff Baxter** — CEO of Enron North America and briefly Vice
  Chairman of Enron Corp. Resigned in May 2001. Killed himself on
  January 25, 2002 during the post-bankruptcy investigations.
- **Lou Pai** — Founding CEO of Enron Energy Services.
- **Ken Rice** — CEO of Enron Broadband Services (and earlier of
  Enron Wholesale Services). Cooperated with prosecutors and was
  sentenced to 27 months.
- **Rebecca Mark-Jusbasche** — CEO of Enron International and
  Azurix until 2000.
- **Mark Frevert** (`frevert-m`) — Chairman of Enron Wholesale
  Services after Whalley moved up.

**Whistleblowers and dissenters**

- **Sherron Watkins** — Vice President of Corporate Development. Sent
  the anonymous warning memo to Lay on August 15, 2001 and a longer
  signed memo a week later. Named Time Person of the Year (jointly)
  for 2002. Her mailbox is not in the corpus.
- **Vince Kaminski** (see below) — repeatedly objected to Fastow's
  partnership structures inside the company and was marginalised for
  it.


## Named-mailbox profiles

These are the people whose addresses, mailboxes, or words appear in the
plots in `eda-2/`, `eda-3/`, and especially `eda-4/`. Alphabetical by
last name. Mailbox handle in backticks where their mailbox is one of
the 150 in the corpus.

**Chris Germany** (`germany-c`) — Trader on the East gas desk in
Houston. One of the most active senders in the corpus throughout
2000-2002 and a recurring top sender in the year-by-year activity
heatmaps.

**Jeff Dasovich** (`dasovich-j`) — Government relations executive
based in California. Liaised between Enron and FERC, the California
Public Utilities Commission, and the state legislature during the
2000-2001 California electricity crisis. The single largest hub in
the eda-3 directed-edges network plot: 106,853 outbound messages on
the top-250 internal pairs alone, all going to a fixed ring of about
a dozen regulatory and PR colleagues.

**Mary Hain** (`hain-m`) — Lawyer in the Wholesale Services legal
department, regulatory side. Appears as a hub in the legal cluster
of the eda-3 graph.

**Tana Jones** (`jones-t`) — Senior legal specialist in the Enron
North America legal department. One of the three pivots (with
Shackleton and Taylor) of the legal cluster in the eda-3 graph.
Among the busiest senders in 1999.

**Vince Kaminski** (`kaminski-v`) — Head of Enron's quantitative
modelling and research group from 1992 to 2002, with roughly fifty
analysts reporting in. Pioneered the risk-management methods Enron
used for its trading book, raised early and repeated objections to
Fastow's off-balance-sheet structures, was sidelined for it but
could not leave because of his contract. His mailbox is the single
largest in the corpus at 28,465 files (the volume reflects both his
role as a senior reviewer and his habit of receiving everyone's
analytical work).

**Paul Kaufman** (`kaufman-p`) — Government relations, paired with
Dasovich on the regulatory ring.

**Stephen Kean** (`kean-s`, also `skean@enron.com`) — Executive
Vice President and Chief of Staff under Lay. Sits in the
receive-heavy outlier list because he appears as a recipient in
many people's mail but his own outbox uses a different address
form (truncated to `skean@enron.com` in many headers).

**Harry Kingerski** (`kingerski-h` is absent, but the address
appears as recipient) — Regulatory affairs.

**Louise Kitchen** (`kitchen-l`) — Trader who built EnronOnline,
later COO of Enron Americas. The "you have 48 hours" subject in
the 2002 hot cells is signed by her, part of the wind-down
communications.

**Kenneth Lay** (`lay-k`) — see executive section above. His
mailbox in 2002 is heavily skewed by inbound protest mail; the
2002 Wed 17 UTC heatmap spike in eda-3 is 770 copies of the
"demand ken lay donate proceeds from enron stock sales" template
landing in his inbox over a single hour and being moved to
`deleted_items` by his assistants.

**Matthew Lenhart** (`lenhart-m`) — Trader.

**Kay Mann** (`mann-k`) — Senior lawyer in the contracts group.
The largest hub on the right-hand side of the eda-3 peer-to-peer
graph (her cluster is contracts and counterparty agreements).

**Susan Mara** (`mara-s` not in the 150, address appears as
recipient) — Government relations, California regulatory side.
Tightly tied to Dasovich.

**Christopher Nicolay** (`nicolay-c` not in corpus as owner) —
Counsel in the Wholesale Services legal department.

**Sarah Novosel** — Regulatory affairs lawyer in the Dasovich
cluster.

**Sara Shackleton** (`shackleton-s`) — Senior counsel in the Enron
North America legal department. Drafted derivatives contracts and
ISDA master agreements. One of the busiest senders across the
entire corpus and an anchor of the legal cluster in the eda-3
graph.

**Richard Shapiro** (`shapiro-r`) — Senior Vice President for
regulatory affairs and government relations. Dasovich's boss in
the org chart.

**James Steffes** (`steffes-j`) — Vice President for government
affairs, the third leg of the Dasovich-Shapiro-Steffes regulatory
cluster.

**Kate Symes** (`symes-k`) — Real-time power-trading associate in
the Portland (Oregon) office, which was Enron's West-coast power
desk for tax reasons even though the traders reported into
Wholesale Services. Hired in April 2001; among the lower-tenure
named mailboxes. Anchors the small but tight West-power triangle
(Symes / Kerri Thompson / Evelyn Metoyer) in the eda-3 round-trip
plot.

**Mark Taylor** (`taylor-m`) — Lawyer in the Enron North America
legal department, derivatives and structured products specialist.
Pairs with Shackleton and Jones on the legal hub.


## Other useful addresses

The plots also surface a number of role accounts that are not
individual people. They show up as send-heavy or receive-heavy
outliers in eda-3 C.3.b.

- `enron.announcements@enron.com`, `announcements.enron@enron.com` —
  Company-wide announcement mailers.
- `outlook.team.cc@enron.com` (often abbreviated) — Distribution-list
  manager for the Outlook team.
- `technology.enron@enron.com` — IT update bot.
- `omaha.helpdesk@enron.com`, `exchange.administrator@enron.com`,
  `mbx_iscinfra@enron.com` — Infrastructure and helpdesk accounts.
- `no.address@enron.com` — Catch-all used by the parser for messages
  with malformed `From:` fields.
- `bob.ambrocik@enron.com` — Reports automation account; 18k+
  outbound and only five inbound on the internal-edge set.
- `all.worldwide@enron.com`, `all.houston@enron.com`,
  `recipients@enron.com` — Distribution-list inboxes; no actual
  person sends from these.


## A note on the receive-only addresses

Eda-3 C.3.b notes that the most "receive-heavy" addresses (1500+ in,
zero out) include normal-looking names like `james.wright`, `mpalmer`,
`beverly.aden`, `gretchen.lotz`, `kevin.hughes`. None of these have
mailboxes in the 150-mailbox CMU release. They appear only as
recipients in other people's sent folders. That asymmetry is a
sampling artefact of the FERC release, not a hierarchy signal. The
release pulled the mailboxes of roughly 150 selected employees; the
several thousand other Enron employees only show up as From or To
addresses in those 150 mailboxes' content.


## Collapse timeline

Reference dates for the scandal-period axvspan used in eda-3 B2 and
D1. Compiled from the Wikipedia "Enron scandal" article.

- **August 14, 2001** — Skilling resigns as CEO after six months,
  citing personal reasons. Lay resumes the role. Stock at $42.
- **August 15-22, 2001** — Sherron Watkins sends Lay an anonymous
  warning memo, then a signed six-page memo detailing the
  accounting issues.
- **October 16, 2001** — Enron announces a $618M Q3 loss and a $1.2B
  reduction in shareholder equity. SEC opens an informal inquiry.
- **October 22, 2001** — SEC inquiry made public; stock falls ~20%.
- **October 25, 2001** — Fastow removed as CFO; McMahon takes over.
- **November 8, 2001** — Enron restates five years of financials,
  reducing reported income by $586M.
- **November 9, 2001** — Dynegy agrees to acquire Enron for ~$8B.
- **November 28, 2001** — Rating agencies cut Enron to junk; Dynegy
  walks away.
- **November 30, 2001** — Enron Europe files for bankruptcy.
- **December 2, 2001** — Enron Corp. files for Chapter 11; at the
  time the largest bankruptcy in US history.
- **January 9, 2002** — Department of Justice opens criminal
  investigation.
- **January 25, 2002** — Cliff Baxter, former Vice Chairman, dies by
  suicide.
- **February 7, 2002** — Skilling testifies before Congress.
- **February 14, 2002** — Lay invokes the Fifth Amendment.
- **June 15, 2002** — Arthur Andersen convicted of obstruction of
  justice (later overturned by the Supreme Court in 2005 on jury
  instruction grounds, by which time the firm had collapsed).
- **January 2006** — Lay and Skilling go on trial.
- **May 25, 2006** — Both convicted. Lay dies of a heart attack on
  July 5, 2006 before sentencing; Skilling sentenced to 24 years
  4 months (later reduced).


## Sources

- [Enron - Wikipedia](https://en.wikipedia.org/wiki/Enron)
- [Enron scandal - Wikipedia](https://en.wikipedia.org/wiki/Enron_scandal)
- [Vincent Kaminski - Wikipedia](https://en.wikipedia.org/wiki/Vincent_Kaminski)
- [Enron Email Dataset - CMU](https://www.cs.cmu.edu/~enron/)
- [Enron Annual Report 2000](https://picker.uchicago.edu/Enron/EnronAnnualReport2000.pdf)
- [The Role of the Board of Directors in Enron's Collapse - US Senate report](https://www.govinfo.gov/content/pkg/CPRT-107SPRT80393/html/CPRT-107SPRT80393.htm)
- [Trader's fortunes rose, fell with Enron power in West - Seattle Times](https://archive.seattletimes.com/archive/20020211/enrontrader11m/traders-fortunes-rose-fell-with-enron-power-in-west)
- [Investigating Enron's email corpus - Linkurious](https://linkurious.com/blog/investigating-the-enron-email-dataset/)
