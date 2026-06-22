# pred-2 thread-annotation schema

This is the contract every annotator (a subagent) must follow when turning one
reconstructed email thread into one structured row. The goal is a table that can
be mined, so the fields are mostly categorical and
every one of them must be supported by the thread text.

## The unit

One row per `thread_id` from the **summarizable set**: genuine multi-party
exchanges with at least two real messages, where "real" means the pipeline flags
`body_empty_after_clean == False`, `body_is_boilerplate == False`, and the pc5
`auto` (newsletter/automated) classifier is `False`. That set is 21,803 threads.
Selection, assembly and the deterministic meta fields are produced by
`build_threads.py`; the annotator only fills the model fields below.

## Input the annotator sees

A JSON object per thread: `thread_id`, `subject`, a `meta` block (precomputed,
do not change it), and `text`, the cleaned message bodies in `thread_position`
order, each prefixed with the sender (resolved name and job title where known).
Over-long threads are truncated to a character budget and marked
`meta.truncated = true`.

## Output: the model fields

```json
{
  "thread_id": 258,
  "category": "legal-regulatory",
  "secondary": "trading-risk",
  "one_line": "one sentence, <= 30 words, what the thread is about and where it lands",
  "summary": "2-4 sentences. Who wants what, what is decided, what is left open. Extractive only.",
  "has_request": true,
  "has_decision": true,
  "outcome": "open",
  "participants": [
    {"ref": "taylor-m", "name": "Mark Taylor", "title": "VP & General Counsel", "role": "proposer", "is_executive": false},
    {"ref": "John Lavorato", "name": "John Lavorato", "title": "CEO (trading)", "role": "approver", "is_executive": true}
  ],
  "entities": ["EnronOnline", "Dynegy", "Canadian power index"],
  "topics": ["market manipulation", "trading-platform compliance"],
  "confidence": "high"
}
```

### Field rules

- **category** (one, required), from this controlled set, grounded in the
  measured subject terms:
  `deal-contract` (ISDA, master agreement, confirmation, swap, counterparty),
  `trading-risk` (positions, books, credit, prices, indices),
  `legal-regulatory` (FERC, filings, litigation, compliance, privilege),
  `california-energy` (the California crisis, PX/ISO, refunds, WSPP),
  `scheduling-logistics` (meetings, calls, travel, calendars),
  `report-fyi` (status updates, forwarded news, no action asked),
  `internal-admin` (HR, IT, expenses, org/process),
  `social` (personal, congratulations, lunch).
  Pick the dominant purpose. `secondary` is optional and free-text-from-the-set.
- **one_line**: a single sentence, at most ~30 words.
- **summary**: 2 to 4 sentences. Name the people and the concrete thing at
  stake. Do not add facts that are not in the text.
- **has_request**: true if anyone asks anyone to do something (a question, a
  "please", a review/approve ask).
- **has_decision**: true if a decision is reached or explicitly deferred.
- **outcome**: `resolved` (the thread states a conclusion), `open` (it ends
  mid-discussion or is deferred/escalated), `unknown` (cannot tell). The corpus
  is one-sided, so `unknown` and `open` will be common. Never invent a
  resolution to make a thread look finished.
- **participants**: the people who matter, senders and important mentions. `ref`
  is the resolved owner handle when given in the input, otherwise the address or
  the name as written. Copy `name`/`title`/`is_executive` from the input when
  present; for a mentioned person not in the input, fill what the text supports
  and leave the rest null. `role` is free text (asker, proposer, approver,
  reviewer, fyi, escalation).
- **entities**: organisations, deals, agencies, systems, named documents. Short
  noun phrases, no sentences.
- **topics**: 1 to 3 short tags.
- **confidence**: `high` / `medium` / `low`. Use `low` when the thread is
  fragmentary, the subject is generic, or `meta.truncated` is true.

## Validation gate (mandatory)

The fields above are enforced by a Pydantic model in `annotation_model.py`.
After writing an output shard, the annotator must run

```
uv run --with pydantic python pred-2/validate_annotations.py \
  pred-2/work/out_NNN.jsonl pred-2/work/shards/shard_NNN.jsonl
```

and fix the file until it prints `PASS`. The gate fails (exit 1) on malformed
JSON, missing/typed/enum field errors, and on any thread_id that is missing,
duplicated, or not from the shard. A long `one_line` is only a warning. The same
model re-validates every line at merge, so nothing malformed reaches the parquet.

## Faithfulness rules (the whole point)

1. Extractive only. Every value must be defensible from the thread text.
2. When the text does not say, use `unknown` / null, not a guess.
3. Do not resolve outcomes that the thread leaves hanging.
4. Keep the summary about this thread, not about Enron in general.

## Deterministic meta fields (added at merge, not by the annotator)

`n_messages`, `n_real`, `n_senders`, `span_days`, `date`, `involves_keep_owner`,
`involves_executive`, `generic_subject`, `external_party`, `truncated`. These
come from the pipeline and carry the per-thread quality caveats into the final
table, so the model never has to compute them.

## Worked examples

`thread_id=258` ("limit order wash trades") and `thread_id=256` ("legal support
for swapco") are the reference annotations; see the pilot output in
`pred-2/work/out_000.jsonl` once it exists.
