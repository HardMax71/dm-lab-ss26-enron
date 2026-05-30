# Cleaning and streamlining the Enron corpus

This note records how the raw Enron release was turned into a deduplicated,
body-cleaned, thread-aware dataset, what each step achieved, and where it fell
short. The whole pipeline is one script, `eda-5/clean_dataset.py`, run with

```
uv run eda-5/clean_dataset.py
```

It reads the raw maildir (`enron_mail/`) and the cached header tables in
`eda-2/cache/`, and writes three files into `eda-5/clean/`:

| File | Rows | Size | One row is |
|------|------|------|------------|
| `messages_clean.parquet` | 252,022 | 74 MB | one unique message, with cleaned body |
| `recipients_clean.parquet` | 1,372,596 | 7.7 MB | one (message, recipient) pair |
| `clean_stats.json` | n/a | <1 KB | the run statistics quoted below |

The whole run takes about 70 seconds on this machine.

## Why the raw corpus needs cleaning

The week-four completeness audit (section B of `enron_eda_week4.ipynb`) turned
up four problems that make the raw 517,401 files awkward to work with:

1. **Duplication.** Half the files are copies. The same message is filed in
   several folders of one mailbox, and broadcast mail sits in every recipient's
   mailbox. A naive count therefore overstates everything.
2. **Quoted history in bodies.** A reply or forward carries the entire prior
   conversation pasted underneath it (`-----Original Message-----`,
   `---- Forwarded by ... ----`, `>` quote chains, `On <date> X wrote:`). The
   same sentence reappears dozens of times across the corpus, and any text
   analysis double-counts it.
3. **Transfer-encoding artifacts.** Messages sent as quoted-printable still
   carry `=20`, `=3D` and soft line-break `=` characters; Lotus Notes leaves
   control bytes such as `\x01,` where a curly apostrophe should be.
4. **Useless columns and a phantom field.** The cached tables carry derived
   helper columns, raw-string copies, and a `bcc_count` that is just a
   duplicate of `cc_count` (a known parser artifact in this release, so Bcc
   carries no real signal).

The pipeline addresses each in turn. Threading is a fifth, separate problem,
discussed in its own section.

## Step 1: Deduplicate files into unique messages

Two files are treated as the same message when they agree on **sender**,
**subject**, **exact send time**, and **recipient counts** (To and Cc). Before
relying on that key, it was validated by hashing the decoded bodies of 40
randomly chosen multi-copy groups: in all 40, every copy in the group was
byte-for-byte identical, so the key does not merge messages that merely look
alike.

For each group one **canonical** copy is kept. The copy is chosen by folder
preference (a copy in the sender's `sent` folder wins, then `inbox`, then the
project, discussion, calendar and deleted folders), with the file path as a
deterministic tie-breaker. Each surviving message records how many copies it
stood for (`n_copies`) and how many mailboxes it appeared in (`n_mailboxes`),
so no information about the duplication is thrown away, only the redundant rows.

**Result.** 517,401 files collapse to **252,022 unique messages**; 265,379
copies (51.3%) are removed. **Success.**

## Step 2: Parse and clean the message bodies

The cached `body_sample.parquet` holds only 25,628 bodies, so the bodies had to
be read fresh from the raw maildir for all 252,022 canonical messages. Python's
`email` parser decodes each file, which transparently handles quoted-printable
and base64, and the body text then passes through a cleaner that:

- repairs Lotus Notes and CP-1252 control bytes (`\x01,` and friends become the
  apostrophe or dash they stand for), and as a safety net undoes any
  quoted-printable that slipped through undecoded;
- **cuts quoted history.** The first time a quote *header* appears everything
  from that point to the end of the message is dropped, because it is the
  previous message pasted below. The markers are deliberately limited to the
  ones that reliably signal a quote boundary: `-----Original Message-----`,
  `---- Forwarded by ----`, an Outlook/Notes header block (a `From:` line
  followed within a few lines by a second header field such as `Sent:`, `To:`,
  `Date:` or `Reply-To:`), a Notes `name@host on <date>` line, and an
  `... wrote:` line;
- removes lines beginning with `>`;
- strips confidentiality and legal disclaimers;
- **reduces HTML to text** when a "plain-text" part is actually raw markup (a
  few percent of messages were HTML-only, so the decoder returned `<table>`,
  `<style>`, `<font>` and the like). Script and style blocks are dropped, block
  tags become line breaks, remaining tags are removed, and entities such as
  `&nbsp;` are unescaped, leaving readable text;
- removes attachment placeholders the mail client left behind
  (`(See attached file: x.doc)`, `<<file.doc>>`, `[IMAGE]`);
- collapses runs of spaces and blank lines.

A message whose body was shortened this way is flagged with `body_was_trimmed`.

**What was deliberately *not* used as a cut marker, and why.** A first version
also treated bare divider rules (a line of 20+ `=`, 10+ `_`, or 5+ `-`) as
quote boundaries. An audit showed this was wrong about half the time: those
rules are also how newsletters separate their sections and how mail clients
fence a signature (`Sent from my BlackBerry`, MSN/Hotmail footers). Cutting at
them deleted real content. Comparing the two versions on a sample, the
divider-based rules were destroying the *entire* body of roughly **8,900
messages** that were not quoted replies at all: a Super Bowl merchandise
mailer, marketing and unsubscribe newsletters, a daily-devotional list, whose
whole content simply happened to sit under a divider line. Those rules were
removed. The lesson is that a divider is not a quote boundary; only an actual
pasted header is, so only headers are cut.

**Result.** 115,890 messages (46%) had quoted history, a disclaimer, HTML or an
attachment placeholder trimmed, and total body text shrank by **48%**. That is the
scale of the duplication and markup that lived inside the bodies rather than
across files. A broad residual-junk audit of all 233,010 non-empty cleaned
bodies finds every artifact class reduced to a handful of rare one-off formats:
zero `>` quote lines, 3 dashed "Original Message" fragments, 5 stray HTML tags,
31 `<<attachment>>` remnants, 9 quoted-printable leftovers and 15 surviving
header fragments, each at or below **0.01%**. **Success.**

**Caveat: the empty bodies (correct, but worth understanding).** 19,012
messages (7.5%) clean to an **empty** body. These are *not* a glitch, and they
are not a Bcc or rerouting trick. Bcc is dropped separately as a parser
artifact (step 3). They are messages where the sender forwarded or replied
**without typing anything of their own**: the file genuinely had content (the
median such file is 1.8 KB), but every word of it was the quoted original, so
once the history is removed nothing is left. The split is about 45% explicit
`FW:` forwards, 9% `Re:` replies, and 46% forwards whose subject was not
prefixed (common in Lotus Notes); 62% sit in a `sent` folder, i.e. someone
forwarding a colleague's mail onward with no comment. The content itself is not
lost: it lives in the *original* message's own row, so emptying these removes
a duplicate, not information. Every such row is flagged `body_empty_after_clean`
so a later step can keep them (when "who forwarded what to whom" matters) or
drop them (when only authored text matters).

**Near-duplicate bodies the exact dedup cannot catch.** Step 1 dedups on
sender + subject + time, so the *same text* resent under a different subject or
by a different person survives as separate rows. The most common are signature
blocks (`Sara Shackleton / Enron North America Corp. ...` appears verbatim in
134 distinct messages), confidentiality disclaimers, and recurring newsletters.
The cleaner hashes the whitespace-normalised body and records `body_dup_count`,
how many distinct messages share that exact text; `body_is_boilerplate` marks
the **2,113** messages whose body is a substantial block (≥120 characters)
shared by five or more messages. The length floor is deliberate: a bare "FYI"
also recurs hundreds of times, but that is real content, not a reused block, so
it is not flagged. A topic or text model should treat the boilerplate like a
stopword block; the flag makes that one line of code rather than a research
project. Nothing is removed.

## Step 2b: Normalise addresses and flag bad ones

A close look at the addresses turned up a systematic artifact of how the corpus
was originally processed: names like `Lastname, F.` were converted into local
parts with stray and doubled dots, so the same person shows up as
`j..kaminski@enron.com`, `.kaminski@enron.com`, and `j.kaminski@enron.com`.
About **12,800 messages (5%)** have a mangled sender address of this kind, and
on the recipient side the same pattern appears on tens of thousands of edges.

A `norm_addr` step lowercases the address, strips wrapping quotes, collapses
runs of dots, and trims leading/trailing dots, producing `from_addr_norm` and
`recipient_addr_norm` columns **alongside** the originals (nothing is
overwritten). Normalisation also blanks the unrecoverable cases (a `no_address`
sentinel, an address with no `@`, or a parser-mangled string with two `@` signs)
which are then flagged rather than silently kept.

**Result.** Dot-normalisation merges **540 distinct recipient identities** and a
handful of senders that were previously split across spellings, which matters
for any identity or network analysis. The mangling is otherwise *consistent* (a
given person is almost always mangled the same way), so it fragments fewer
identities than its raw frequency suggests. Two flag columns, `from_addr_valid`
and `recipient_addr_valid`, mark the **758** sender and **50** recipient
addresses that cannot be resolved to a well-formed address at all, and
`from_addr_mangled` marks the dot-mangled ones. **Success**. The bad addresses
are now labelled and a clean form is available, without discarding the originals.

## Step 3: Rebuild the recipient list

Recipients are taken from the cached edge table, restricted to the canonical
messages, and to the **To** and **Cc** channels only. Bcc is dropped on purpose:
in this release the parser copied Cc into Bcc, so every Bcc is a phantom
duplicate and keeping it would invent recipients. This was not taken on faith.
The pipeline now checks it: of the 59,563 canonical messages that carry both a
Cc and a Bcc, the two address sets are **identical 100% of the time**. That is
the proof that Bcc is a copy, so it is dropped. Exact duplicate
(message, recipient, channel) rows are also removed.

**Result.** 1,372,596 clean recipient edges, and per-message counts
(`to_count`, `cc_count`, `recipient_count`, `external_recipient_count`)
recomputed from them so they agree with the edge table. **Success.**

## Step 3b: Flag the things that distort counts but should not be deleted

Three patterns skew any count or graph built on this data, but none should be
removed: they are real mail. So each is **flagged** and left in place.

- **Distribution-list recipients.** 3,799 recipient edges go to a list or role
  address (`all.worldwide@enron.com`, `controllers.dl-ets@enron.com`,
  `shift.dl-portland@enron.com`). One such recipient stands for many real
  people, and the corpus gives no membership list to expand it, so a network
  built on raw recipients both understates true reach and treats the list as if
  it were a single person. The `recipient_is_list` flag (and the per-message
  `has_list_recipient` / `list_recipient_count`) lets that mail be handled
  separately.
- **Self-addressed mail.** 20,996 edges (1.5%) are a message to its own sender,
  a to-self reminder or a self-Cc. Harmless, but it inflates reciprocity and
  round-trip metrics, so it is flagged `is_self`.
- **Sent, but not by the mailbox owner.** 4,081 messages in a `sent` folder have
  a from-address that does not contain the owner's surname: an assistant
  sending on an executive's behalf, a shared role mailbox, or simply misfiled
  mail. It matters for attribution (who *actually* sent it), so it is flagged
  `sent_not_by_owner`.

**Result.** Five flag columns added across the two tables; zero rows removed.
**Success.**

## Step 4: Reconstruct conversation threads

This is the step that cannot be done the normal way, and the report is explicit
about it. Email threads are normally rebuilt from the `In-Reply-To` and
`References` headers, but **this release has neither**. Both are absent on
every file, and the `Message-ID` values are synthetic
`<...JavaMail.evans@thyme>` strings minted when the corpus was processed, with
no link to the messages they reply to. There is no header trail to follow.

Threads are therefore **reconstructed**, not recovered. Two messages are placed
in the same thread when their subjects match after stripping reply and forward
prefixes (`Re:`, `Fw:`, stacked combinations) and lowercasing, **and** they
share at least one participant (sender or recipient). The grouping is
transitive (if A links to B and B links to C, all three form one thread),
implemented with a union-find structure. Each message receives a `thread_id`,
the `thread_size`, its `thread_position` in send-time order, and an
`is_thread_root` flag for the earliest message.

Two messages join a thread only when they share **all three** of: a normalised
subject, a participant (matched on the normalised address from step 2b, so
dotty spellings of one person do not split a thread), **and a send time within
30 days** of another message already in the chain. The subject group is walked
in date order, and the "last seen" message per participant is refreshed as we
go, so a quiet gap longer than the window starts a fresh conversation.

**Why the time bound matters: and what it caught.** A first version had only
subject + participant, with no time limit. Auditing its largest threads exposed
a clear failure: a single "fyi" thread chained **45 different people's unrelated
notes across nearly three years** into one bogus conversation, linked only
because they shared the throwaway subject and the legal team kept appearing on
each other's mail. That thread had eight gaps of more than a month, which a real
reply chain never has. In total, **807 multi-message threads ran for more than a
year**, and a per-thread check showed each had glued together an average of
**3.4 distinct conversations**. Adding the 30-day bound fixes this at the
source: those 807 over-merged threads drop to **zero**, the bad "fyi" thread
splits back into 88 short threads (the largest now 11 messages), and the change
touches only about 11% of threads; the other 89%, whose messages already sit
within a day or two of each other, are untouched. The `thread_maybe_overmerged`
flag remains as a tripwire but now fires on nothing.

**Result.** 163,883 threads, of which 40,306 hold more than one message;
128,445 messages (51%) sit in a real multi-message thread. The median thread is
a single message, the mean size is 1.5, and 81% of multi-message threads have a
median inter-message gap of a day or less. The largest thread, 1,123 messages,
is correctly the post-collapse protest campaign demanding Ken Lay donate his
stock proceeds: 1,116 different senders on one subject over a **single day** in
January 2002, exactly the kind of same-day blast the method should keep whole.

**Honest limits.** Thread integrity is exact: every thread has exactly one root
and no impossible positions. The remaining weakness is the mirror image of the
one just fixed: the 30-day bound will **split** a genuinely slow-burn
conversation (a contract negotiation that goes quiet for six weeks and resumes
under the same subject becomes two threads). With the threading headers gone
there is no way to tell that resumption from a fresh same-subject mail, so a
time bound is the standard trade-off, and it is set to err toward splitting
rather than the far more damaging over-merging seen above. Empty-subject
messages (about 3%) are left as singletons. So `thread_id` is a strong, useful
approximation for descriptive work, not a guaranteed reconstruction of the true
reply tree.

## Step 5: Streamline the columns

The cached `rich_header_features` table carries 43 columns, many of them
modelling helpers (`file_size_log`, `recipient_count_log`, `path_depth`), raw
duplicates (`subject` alongside `subject_norm` and `date_raw`), the phantom
`bcc_count`, and Lotus bookkeeping (`x_origin`, `x_folder`, `x_filename`). The
clean message table keeps **37 columns**: the message identity and timing, the
sender (raw and normalised, with the quality flags), the cleaned subject and its
normalised form, the recomputed recipient counts, the list/self flags, the
cleaned body with its provenance and boilerplate flags, the duplication counts,
and the thread fields. Everything kept is either a fact about the message or a
flag describing what the cleaning found or did.

**Result.** A 37-column message table and a 10-column recipient table, both
written with Zstandard compression. **Success.**

## Data-quality audit: edge cases checked and what was found

Beyond the headline cleaning, the dataset was swept for the kinds of corruption
that hide in a 20-year-old corpus: typos, mangled fields, missing or excess
data, impossible values. Each row below is a class that was checked; most are
either correct-by-design or now flagged in the data.

| Checked | Count | Verdict |
|---------|------:|---------|
| Sender address dot-mangled (`j..kaminski`) | 12,793 (5.1%) | flagged `from_addr_mangled`; clean form in `from_addr_norm` |
| Sender unresolvable to a valid address | 758 (0.3%) | flagged `from_addr_valid = false` |
| Recipient address malformed (quotes, double-`@`, X.500 DN leak) | 50 edges | flagged `recipient_addr_valid = false` |
| Distinct identities merged by dot-normalisation | 540 recip. + 11 send. | merged in the `_norm` columns |
| Messages with **zero** recipients | 8,588 (3.4%) | **correct**: all had To = Cc = 0 in the original headers (Bcc-only or header-less); no recipient was lost |
| Implausible send date (1980 epoch, 2004 spam, 2044) | 356 of 252k unique (605 of 517k raw) | flagged `date_plausible = false`; see the date investigation below |
| Empty subject | 8,694 (3.4%) | genuine; left as thread singletons |
| Body empty after cleaning | 19,012 (7.5%) | no-comment forwards (see step 2); flagged |
| Threads spanning > 1 year (over-merged) | 807 → **0** | fixed by the 30-day thread gap; `thread_maybe_overmerged` now fires on nothing |
| `is_internal_sender` vs `enron.com` domain | 1,209 (0.5%) | **not a bug**: these are subdomains (`mailman.`, `postmaster.`, `exchange.enron.com`), i.e. list/system servers the source table deliberately treats as non-personal |
| Thread integrity (one root, valid positions) | 0 errors | every thread has exactly one root and no impossible positions |
| `from_domain` vs address domain | 0 mismatches | consistent |
| Near-duplicate bodies (recurring ≥120-char block) | 2,113 msgs | flagged `body_is_boilerplate`; `body_dup_count` on every row |
| Distribution-list recipients | 3,799 edges | flagged `recipient_is_list` / `has_list_recipient` |
| Self-addressed mail | 20,996 edges (1.5%) | flagged `is_self` |
| Sent mail not from the mailbox owner | 4,081 (4.2% of sent) | flagged `sent_not_by_owner` |
| Bcc identical to Cc (artifact check) | 59,563 with both, **100% identical** | confirms Bcc is a copy; dropped |
| Mojibake / broken encoding in bodies | 3 | negligible; left as-is |
| Non-ASCII characters in bodies | 2,371 (0.9%) | legitimate accents/symbols, not corruption |
| Empty subject **and** empty body | 320 | near-contentless; covered by existing flags |
| Large file (>50 KB) but tiny body (<200 ch) | 64 | attachments/encoded blobs correctly stripped |

The one finding that *looked* like a pipeline bug (a handful of messages
seeming to lose a real To/Cc recipient) turned out to be an artifact of a
looser diagnostic key during the audit itself. Re-checking with the exact
dedup key confirmed **zero** recipient loss: every zero-recipient message
genuinely had no To/Cc recipient in its original header.

### A closer look at the dates

Dates earned their own investigation, because a wrong timestamp is invisible:
it parses fine and silently lands in the wrong month. Four checks were run.

**The implausible dates are correctly flagged, and they are real junk.** In the
deduplicated dataset 356 messages are flagged (605 across all 517k raw files
before dedup), and reading their raw `Date:` headers explains every one. The
283 stamped 1 Jan 1980 all carry `Mon, 31 Dec 1979 16:00:00 -0800`, which is the
Unix epoch in Pacific time, the zero value a mail client writes when it has no
real date, so the parse is right and the data is genuinely absent. The 71 dated
2004 and later are not Enron mail at all: they are marketing blasts
(`lists.adversend.com`, `autobytel.com`, Shrek gift-set and holiday-shopping
subjects) that arrived in a few mailboxes long after the company collapsed. The
far-future 2012/2020/2044 handful are similar client-clock garbage. None of
these belong in the working data, and all are already marked
`date_plausible = false`.

**No silent corruption among the "plausible" dates.** The real corpus runs from
1999 to mid-2002; volume falls off a cliff after July 2002 (76 messages in
July, then single digits) and the last genuine message is 21 Dec 2002. The
~200 messages dated 1997-1998 are real: they belong to `kean-s` and `taylor-m`,
who were at the company early, and carry ordinary `-0700/-0800` timestamps.

**Cross-checking dates against the archive-folder names found nothing wrong.**
Many Enron folders embed a snapshot date (`Steven_Kean_Dec2000`), and 81,000
messages are dated about a year *before* their folder, which is exactly right,
because an archive folder holds older mail filed into it. Mail dated *after* its
folder would be the suspicious direction; the few dozen that appeared so turned
out to be the year-regex catching a project code (`GRI-J`, `Keyex`) in the
folder name rather than a real archive date. The dates themselves were fine.

**Timezones are uniform and parsed correctly.** Every one of the 517,401 raw
`Date:` headers carries a `-0700` or `-0800` offset (the FERC processing
normalised all mail to US Pacific time regardless of where the sender actually
was) and all 517,401 parse cleanly to timezone-aware UTC with zero failures and
zero missing offsets. One consequence worth noting for any hour-of-day analysis:
because the wall-clock was forced to Pacific, "business hours" in these
timestamps are Pacific, not the Central time of Enron's Houston headquarters, so
a true local-time reading would shift everything two hours later. The stored
`date` column is correct UTC; only the interpretation needs that caveat.

The existing `date_outlier` column in the source table agrees exactly with
`date_plausible` (both mark the same 605 raw files), so the two are consistent.

## Outcome

| Quantity | Raw | Clean |
|----------|-----|-------|
| Rows (messages) | 517,401 files | 252,022 unique messages |
| Duplication | 51% redundant | 0 (one row per message) |
| Quoted history in bodies | pervasive | removed (48% of body text) |
| Quote / HTML / attachment junk | common | ~0 (every class ≤0.01%) |
| Threading | none (headers gone) | reconstructed, 40,306 multi-msg threads, time-bounded |
| Mangled addresses | unflagged | normalised + flagged (`_norm`, `_valid`) |
| Boilerplate / lists / self-mail | unmarked | flagged, not removed |
| Columns | 43, with phantom Bcc | 37, no phantom fields, with quality flags |

The dataset is now one row per real message, with bodies that contain only the
text that message actually added, recipients that reflect only real To/Cc
delivery, and a thread label that ties replies together as far as a header-less
corpus permits. What it is **not** is a perfect reconstruction of the original
mail server: 8% of messages legitimately have no body left after their quoted
history is removed, and the thread grouping is a heuristic standing in for
headers that no longer exist. Both limits are recorded in the data itself
(`body_empty_after_clean`, and the thread fields being approximate) so that
later work can account for them rather than trip over them.

## Output schema

`messages_clean.parquet` (one row per unique message):

| Column | Meaning |
|--------|---------|
| `message_id` | synthetic id of the canonical copy (identifies a file, not a thread) |
| `date`, `date_plausible` | send time; flag for the 0.1% with unusable timestamps |
| `from_addr`, `from_addr_norm` | sender address as found, and the dot-normalised canonical form |
| `from_domain`, `is_internal_sender` | sender domain and whether it is an enron.com address |
| `from_addr_mangled`, `from_addr_valid` | sender had dot-mangling; sender resolves to a well-formed address |
| `sent_not_by_owner` | in a `sent` folder but the from-address is not the mailbox owner (assistant / shared / misfiled) |
| `subject`, `canon_subject` | original subject and the prefix-stripped, lowercased form used for threading |
| `to_count`, `cc_count`, `recipient_count` | recipient counts recomputed from clean To/Cc edges |
| `external_recipient_count`, `has_external_recipient` | non-enron.com recipients |
| `list_recipient_count`, `has_list_recipient` | how many recipients are distribution/role lists |
| `mailbox_owner` | which of the 150 released mailboxes the canonical copy came from |
| `folder_group`, `file_size` | folder class of the canonical copy; original file size in bytes |
| `body`, `body_chars` | cleaned body text and its length |
| `body_was_trimmed` | quoted history, disclaimer, HTML or attachment placeholder was removed |
| `body_empty_after_clean` | nothing remained after cleaning (no-comment forward/quote) |
| `body_dup_count`, `body_is_boilerplate` | distinct messages sharing this exact body; flag for a recurring ≥120-char block |
| `n_copies`, `n_mailboxes`, `in_sent` | how many files this message stood for, across how many mailboxes, and whether one was a sent copy |
| `thread_id`, `thread_size`, `thread_position`, `is_thread_root` | reconstructed conversation grouping |
| `thread_span_days`, `thread_maybe_overmerged` | day span of the thread; over-merge tripwire (now 0 after the 30-day gap rule) |

`recipients_clean.parquet` (one row per delivery):

| Column | Meaning |
|--------|---------|
| `message_id` | links back to the message |
| `from_addr` | sender |
| `recipient_addr`, `recipient_addr_norm` | one recipient, as found and dot-normalised |
| `recipient_domain`, `recipient_addr_valid` | recipient domain; whether it resolves to a well-formed address |
| `recipient_is_list` | recipient is a distribution / role list address |
| `is_self` | recipient is the message's own sender (to-self / self-Cc) |
| `channel` | `to` or `cc` |
| `is_internal_recipient` | recipient is an enron.com address |
