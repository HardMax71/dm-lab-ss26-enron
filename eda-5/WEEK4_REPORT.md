<p>This page reports the tasks and outcomes of week 4.</p>

<h3 data-nh-numbering="1.1.1. ">Leftovers from last week</h3>

<p>The week-three review left a punch list of things to fix rather than new questions to open. The 24-hour activity heatmap was coloured in a way that made low-volume years look empty and empty cells look busy. The social plots keyed on raw e-mail addresses, so one person who wrote from several spellings of their address was scattered across the charts as if they were several people. The two co-occurrence word charts for California and EES were drawn on independent x-axes, so equal-length bars in the two panels stood for very different counts. We had counted deleted mail per mailbox but said nothing about when it was deleted or what it was about, and there was an open guess that people leaving the company might be what drove deletion. Underneath all of this sat a question the earlier notebooks had skipped: when we say the corpus holds 517,401 messages, how many distinct e-mails is that really, and which header fields can we actually trust?</p>

<p>Answering these properly meant the raw cache from week two was no longer good enough, because half of those 517,401 files are duplicate copies and the bodies still carried the full quoted history of every reply. So before the analysis we cleaned the whole corpus into two deduplicated, body-cleaned, thread-aware tables under <code>eda-5/clean/</code> (252,022 distinct messages and 1,372,596 recipient rows), documented step by step in <code>eda-5/DATASET_CLEANING.md</code>. Every figure this week runs on that cleaned data, and where a clean number disagrees with a week-three number, the clean one is the one we keep.</p>

<h4 data-nh-numbering="1.1.1.1. ">Tasks of this week</h4>

<p>Plot Creation - Max</p>

<p>Writing of Report, Creation of Presentation, Presentation - Len</p>

<h4 data-nh-numbering="1.1.1.2. ">Results/Findings/Outcomes</h4>

<p><strong>The 24-hour activity plot, fixed.</strong> The old heatmap asked one picture to answer two questions on one colour bar, and coloured zero as dark, so quiet years read as empty and empty grids read as full. We split it into two honest rows. The top row, in blue, holds all four years on one shared scale of real message counts; the bottom row, in green, rescales each year to its own busiest hour. A different colour map on each row keeps them from being read as the same scale, and an empty cell is white on both.</p>

<p><img src="https://raw.githubusercontent.com/HardMax71/dm-lab-ss26-enron/main/eda-5/plots/a1_weekday_hour_dual.png" alt="Weekday-by-hour activity, shared count scale over per-year shape scale" /></p>

<p>The volume gap is now plain: 2001 is darker everywhere because it simply holds more mail, and 1999 is pale because it is a tenth the size, not because it was idle. On the per-year row the daily shape is the same story every year, a single weekday block from roughly 14:00 to 23:00 UTC, which is mid-morning to late afternoon in Houston, with white weekends. The one exception is 2002, whose weekday block is thinner and shifted, the tail of a company that was being wound down.</p>

<p><strong>How complete is the dataset.</strong> Two files are the same message when they share a sender, a subject, an exact send time and recipient counts. By that test only 252,022 of the 517,401 files are distinct, so 51% of the corpus is duplication: about 203,000 copies are the same message filed twice inside one mailbox, and about 63,000 are one message sitting in several mailboxes of people who were all on it.</p>

<p><img src="https://raw.githubusercontent.com/HardMax71/dm-lab-ss26-enron/main/eda-5/plots/b1_dedup_waterfall.png" alt="Deduplication waterfall from 517k files to 252k distinct messages" /></p>

<p>Two week-three statements turn out to be artifacts of counting files instead of messages. The folder mix inverts: project and topic folders are not the largest block at 37%, they are mostly where people re-file copies they already hold in <code>inbox</code> or <code>sent</code>, and once each message is counted once <code>topic/project</code> collapses to about 11% while <code>sent</code> and <code>inbox</code> become the real bulk. Mailbox size re-ranks too: the raw largest mailbox was <code>kaminski-v</code> at 28,465 files, but after dedup the largest is <code>dasovich-j</code> and <code>kaminski-v</code> drops to second.</p>

<p><img src="https://raw.githubusercontent.com/HardMax71/dm-lab-ss26-enron/main/eda-5/plots/b1b_dedup_corrections.png" alt="Folder mix and mailbox ranking before and after deduplication" /></p>

<p>One point the left panel is worth being explicit about, since it reads oddly at first glance: those bars are each folder's <em>share</em> of the corpus, not a count. No folder ends up with more messages than files. Every folder's absolute count falls after deduplication (<code>sent</code>, for instance, drops from 126,058 files to 97,059 messages); <code>sent</code> and <code>inbox</code> only climb as a percentage because <code>topic/project</code>, which was overwhelmingly duplicate copies, is stripped out and shrinks the total the shares are measured against. The plot carries this note inline so the rising bars are not misread as growth.</p>

<p>The fields that say who sent what and when are essentially complete: a sender on every file, a usable timestamp on 99.9%, a subject on 96%. The fields that would reconstruct conversations are gone. Message-ID reads as 100% present, but the values are machine-generated placeholders with no link to what they reply to, and In-Reply-To and References were stripped before release. That is the single biggest gap in the data.</p>

<p><img src="https://raw.githubusercontent.com/HardMax71/dm-lab-ss26-enron/main/eda-5/plots/b2_metadata_coverage.png" alt="Header field coverage across the corpus" /></p>

<p>The messages themselves are small: the median file is about 1.5 KB, the 95th percentile under 8 KB, and the long tail up to roughly 2 MB is the few mails carrying large quoted threads or inline tables. Usable mail runs from 1999 to the end of 2002, with the build-up through 2000 and the spike around the autumn-2001 collapse. Only 605 files (0.1%) carry a date the parser could not trust, most stamped 1 January 1980, the zero point a mail client falls back to when the real date is missing, so the timeline is complete with a known, tiny hole rather than a silent one.</p>

<p><img src="https://raw.githubusercontent.com/HardMax71/dm-lab-ss26-enron/main/eda-5/plots/b3_size_and_timespan.png" alt="Message size distribution and activity over time" /></p>

<p>The 150 released mailboxes are a keyhole. Counting only Enron-internal addresses, about 33,000 distinct accounts appear as recipients, and only about 17% of them have a mailbox of their own in the release. For the rest we see one side of the conversation at best. This is the main caveat behind every network number below: the graph is dense and complete among the 150 and increasingly partial as it reaches everyone else.</p>

<p><img src="https://raw.githubusercontent.com/HardMax71/dm-lab-ss26-enron/main/eda-5/plots/b4_recipient_coverage.png" alt="Share of internal correspondents that have their own mailbox" /></p>

<p><strong>Mailboxes are not people.</strong> The same individual sends as <code>vince.kaminski@enron.com</code>, <code>j.kaminski@enron.com</code>, <code>vkamins@enron.com</code> and so on, and the week-three plots scattered those across separate rows. We resolve addresses to people using each owner's own sent-mail folders, sense-checked against <code>WHOS_WHO.md</code>. One clarification on the feedback wording: in this corpus a mailbox really does equal a person. The only repeated surnames (mckay, ring, whalley) are each two different people, so nothing needs merging at the folder level; the multiplicity lives entirely in the addresses.</p>

<p><img src="https://raw.githubusercontent.com/HardMax71/dm-lab-ss26-enron/main/eda-5/plots/c1_addresses_per_person.png" alt="Number of sending addresses per mailbox owner" /></p>

<p>Of the 150 owners, 104 write from a single Enron address, 31 from two, and only six from three or four; nine never send from an address containing their surname and are left unresolved by the conservative rule. The multi-address cases are not extra accounts but messy formatting of one name, heaviest for Vince Kaminski (<code>kaminski</code>, <code>j.kaminski</code>, <code>j..kaminski</code>). Smaller than the raw scatter suggested, but the reviewer's point holds, and the next plots collapse each person to one row.</p>

<p><strong>Round-trips and a cluster that cycles mail, on people.</strong> With addresses resolved to people, each round-trip pair is one row no matter how many spellings the two used, and a balance figure (the smaller direction as a share of the larger) shows whether a link is genuinely two-way.</p>

<p><img src="https://raw.githubusercontent.com/HardMax71/dm-lab-ss26-enron/main/eda-5/plots/d1_roundtrip_people.png" alt="Top reciprocal correspondent pairs, addresses resolved to people" /></p>

<p>The heaviest links are the California government-affairs pairs around Jeff Dasovich (with Richard Shapiro and Steve Kean) and the ENA legal pairs (Tana Jones with Mark Taylor and Sara Shackleton). The balance column shows that the very largest links are not all even: a high total can still be one heavy sender plus a lighter reply stream. Drawing the whole reciprocal graph, where a line means the two people mail each other in both directions, the headline is that it is dense, but not structureless.</p>

<p><img src="https://raw.githubusercontent.com/HardMax71/dm-lab-ss26-enron/main/eda-5/plots/d2_reciprocal_cluster.png" alt="Full reciprocal social graph of the 150 mailbox owners" /></p>

<p>A modularity split separates five communities, and each maps onto a real part of the company: the trading floor with research and risk (Kaminski, Buy, Arnold, Delainey, Beck); the West-power and real-time desk that ran the California positions (Forney, Presto, Campbell); the ENA legal department with the East gas desk it served (Jones, Mann, Shackleton, Haedicke, Germany, Nemec); the pipelines and utility-operations group (Lokay, Hayslett, McConnell, Scott, Watson); and the small executive and government-affairs core that ties the rest together (Lay, Skilling, Whalley, Dasovich, Kean, Shapiro, Steffes, Derrick).</p>

<p>Each community is drawn on its own graph below so the membership is legible.</p>

<p><img src="https://raw.githubusercontent.com/HardMax71/dm-lab-ss26-enron/main/eda-5/plots/d3_1.png" alt="Community 1: trading floor and research/risk desk" /></p>

<p><img src="https://raw.githubusercontent.com/HardMax71/dm-lab-ss26-enron/main/eda-5/plots/d3_2.png" alt="Community 2: West-power and real-time desk" /></p>

<p><img src="https://raw.githubusercontent.com/HardMax71/dm-lab-ss26-enron/main/eda-5/plots/d3_3.png" alt="Community 3: ENA legal and East gas desk" /></p>

<p><img src="https://raw.githubusercontent.com/HardMax71/dm-lab-ss26-enron/main/eda-5/plots/d3_4.png" alt="Community 4: pipelines and utility operations" /></p>

<p><img src="https://raw.githubusercontent.com/HardMax71/dm-lab-ss26-enron/main/eda-5/plots/d3_5.png" alt="Community 5: executives and government affairs" /></p>

<p><strong>California and EES word charts, on one scale.</strong> Put on a single shared x-axis, the two co-occurrence charts become comparable, which is the whole reason to show them together. This now runs on the full corpus rather than the 25,628-row sample week three used, about 12,500 cleaned bodies mentioning California against about 3,900 for EES.</p>

<p><img src="https://raw.githubusercontent.com/HardMax71/dm-lab-ss26-enron/main/eda-5/plots/e1_california_ees_samescale.png" alt="California and EES co-occurring words on one shared scale" /></p>

<p>On a shared scale the gap is plain: California is the far heavier topic, and its companion words are the regulatory and power-market vocabulary of the 2000-2001 crisis (power, energy, state, market, price). The EES panel is shorter, and its words are the internal, organisational language of the retail-services unit. Because the bodies are cleaned, the words are the writers' own and not quoted history, and flagged signatures and disclaimers are excluded so they cannot crowd the top.</p>

<p><strong>What gets deleted, and when.</strong> Deleted-folder mail grows with overall volume and peaks in the same late-2001 window as everything else, so in raw counts deletion just tracks how much mail there was. The rate line, deletion as a share of that month's mail, is the telling series: it is uneven month to month and does not jump at any single collapse date. Deletion is a steady habit that scales with traffic, not a one-off purge.</p>

<p><img src="https://raw.githubusercontent.com/HardMax71/dm-lab-ss26-enron/main/eda-5/plots/f1_deletion_over_time.png" alt="Deleted-mail volume and deletion rate over time" /></p>

<p>Deletion is strongly topic-dependent. The clean base rate is about 14% of messages (up from the raw 10%, because the kept folders held more of the duplicates dedup removed). The words far above that line (<code>proceeds</code>, <code>donate</code>, <code>stock</code>, <code>demand</code>, <code>ken</code>, <code>lay</code>) belong to one mass-protest campaign, thousands of near-identical messages demanding Ken Lay donate his stock-sale proceeds, dumped into his mailbox after the collapse and swept straight into deleted items. The rest of the over-deleted list is automated traffic (<code>headlines</code>, over-quota <code>mailbox</code> warnings). The under-deleted words are deal and counterparty vocabulary people kept (<code>nda</code>, <code>raptor</code>, <code>abb</code>, <code>allegheny</code>, <code>brokerage</code>). Employees discarded noise and protest and filed the business, so deleted folders are not a random sample.</p>

<p><img src="https://raw.githubusercontent.com/HardMax71/dm-lab-ss26-enron/main/eda-5/plots/f2_deletion_topic_preference.png" alt="Subjects deleted more and less often than the base rate" /></p>

<p><strong>Did people leaving drive deletion?</strong> The corpus records no termination dates, so we use a proxy: the last month a mailbox shows any activity stands in for when the person stopped using it, and we ask whether deletions bunch into a mailbox's final stretch more than its ordinary mail does.</p>

<p><img src="https://raw.githubusercontent.com/HardMax71/dm-lab-ss26-enron/main/eda-5/plots/g1_departure_vs_deletion.png" alt="Deletion concentration in the last active window per mailbox" /></p>

<p>On its face the signal points the reviewer's way: across 119 testable mailboxes the median concentration ratio is 1.65, and 76% delete a larger share of their mail in their last sixty active days than they send or receive there. But it cannot be read cleanly, because <code>deleted_items</code> is a live buffer that users empty periodically, so whatever survives to the 2002 snapshot is disproportionately recent deletions while older ones were already purged. That alone produces an end-loaded pattern whether or not anyone left. The honest verdict: the data is consistent with departures prompting a clean-out, but the rolling-buffer artefact explains it equally well, and these headers cannot separate the two.</p>

<p><strong>Conversation threads, now that we can build them.</strong> The release has no In-Reply-To or References headers, so week three could not look at conversations at all. The cleaning step reconstructs threads from a shared normalised subject plus an overlapping participant within a 30-day window, giving 40,306 multi-message threads.</p>

<p><img src="https://raw.githubusercontent.com/HardMax71/dm-lab-ss26-enron/main/eda-5/plots/h1_threads.png" alt="Reply latency and thread-size distributions" /></p>

<p>Enron mail was answered fast: half of all replies land within about three hours, a quarter within twenty minutes, and three quarters inside a day, with a long tail of slow-burn threads that resume after a pause. Thread sizes follow the usual heavy skew, mostly single back-and-forth pairs falling off steeply, with only a few thousand running long. The one thread over a thousand messages is the post-collapse protest campaign, a blast rather than a conversation.</p>

<h4 data-nh-numbering="1.1.1.3. ">Discussion/Challenges/Special remarks</h4>

<p>The biggest challenge was that the raw corpus could not be trusted at face value, and most of the week's effort went into the cleaning before any plot could be drawn. Half the files are duplicates, so any count taken on raw files silently double-counts broadcasts and carefully filed memos; two of the week-three headline numbers (the 37% project-folder share and the largest-mailbox ranking) turned out to be exactly this kind of artifact. Body text was the second trap: every reply carried the full quoted history of the thread, so a naive word count repeats the same sentence down a chain. An early version of the body cleaner over-corrected here, treating bare divider lines as quote boundaries and destroying around 8,900 genuine newsletters; the fix was to cut only on header-anchored reply markers and leave plain dividers alone.</p>

<p>Thread reconstruction is a heuristic by necessity, since the headers that would do it properly are gone. Grouping on subject and participant with no time bound chained dozens of unrelated short notes that happened to share a subject like "fyi" across three years, so we added a 30-day gap constraint, which removed the over-merged threads. The cost is that a genuine slow-burn exchange resuming after more than a month is split into two, which barely affects reply-speed and thread-size description but would matter for any per-thread narrative.</p>

<p>A few smaller remarks worth recording. Timestamps are uniformly in Pacific time in the headers, while Enron sat in Houston (Central), so any "business hours" reading is off by a couple of hours and we describe the daily block in UTC to avoid the trap. The Bcc field in the parsed data is byte-identical to Cc in every message we checked, a parser artifact rather than real blind copies, so Bcc was dropped. And the densely connected social core is partly a property of the release itself: these 150 mailboxes were captured because the people were central to the FERC investigation, so they are far more connected to each other than a random 150 employees would be.</p>

<h4 data-nh-numbering="1.1.1.4. ">Open Ends</h4>

<p>The threading headers are gone for good, so the reconstructed threads will stay a heuristic; the reply-speed and size numbers are sound for description but should not be pushed into per-conversation claims. The departure-versus-deletion question is effectively unanswerable with these headers, because the deleted-items buffer and the lack of real termination dates both confound it, and would need an external source of leaving dates to settle. Coverage is the standing caveat for everything downstream: only about a sixth of the internal people the 150 mailboxes correspond with have a mailbox of their own, so every network and rate figure describes a hand-picked core rather than the company. With the dataset now deduplicated, body-cleaned and thread-aware under <code>eda-5/clean/</code>, the natural next step is to move from describing the corpus to predictive work on it, which is where the schedule turns next.</p>
