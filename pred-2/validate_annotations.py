"""Validate one annotator output shard against the Pydantic model, and (if given
the matching input shard) check the thread_id set is exactly covered.

    uv run --with pydantic python pred-2/validate_annotations.py OUT.jsonl [SHARD.jsonl]

Exit 0 = PASS (clean, safe to merge), exit 1 = FAIL (hard errors listed). Soft
style issues (e.g. a long one_line) are warnings and do not fail the gate.
"""
import sys, json
from pathlib import Path
from pydantic import ValidationError
from annotation_model import Annotation


def main() -> int:
    out = Path(sys.argv[1])
    shard = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    hard, warn, ids = [], [], []

    if not out.exists():
        print(f"FAIL: {out} does not exist")
        return 1

    for n, line in enumerate(open(out), 1):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as e:
            hard.append(f"line {n}: invalid JSON ({e})")
            continue
        try:
            a = Annotation.model_validate(obj)
        except ValidationError as e:
            err = e.errors()[0]
            hard.append(f"line {n} (thread {obj.get('thread_id', '?')}): "
                        f"{e.error_count()} error(s); first: {list(err['loc'])} -> {err['msg']}")
            continue
        ids.append(a.thread_id)
        if len(a.one_line.split()) > 30:
            warn.append(f"thread {a.thread_id}: one_line is {len(a.one_line.split())} words (>30)")

    if shard and shard.exists():
        want = [json.loads(l)["thread_id"] for l in open(shard) if l.strip()]
        ws, gs = set(want), set(ids)
        if len(ids) != len(set(ids)):
            hard.append(f"{len(ids) - len(set(ids))} duplicate thread_id(s)")
        if ws - gs:
            hard.append(f"missing {len(ws - gs)} thread_id(s), e.g. {sorted(ws - gs)[:5]}")
        if gs - ws:
            hard.append(f"{len(gs - ws)} unexpected thread_id(s), e.g. {sorted(gs - ws)[:5]}")

    if hard:
        print(f"FAIL: {out.name}: {len(ids)} valid rows but {len(hard)} hard error(s):")
        for h in hard[:25]:
            print("  -", h)
        return 1
    print(f"PASS: {out.name}: {len(ids)} valid annotations"
          + (f", {len(warn)} warning(s)" if warn else ""))
    for w in warn[:8]:
        print("  ~", w)
    return 0


if __name__ == "__main__":
    sys.exit(main())
