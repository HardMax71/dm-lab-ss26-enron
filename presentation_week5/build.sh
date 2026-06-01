#!/usr/bin/env bash
# Build the week-5 deck and flag any content that runs out of the slide bounds.
#
# Usage:
#   ./build.sh              compile the clean handout PDF, warn on overflow
#   ./build.sh --strict     also draw a black rule at every overflow, and exit
#                           non-zero if any overflow is found (for CI / gating)
#   ./build.sh --notes      build the presenter version (slide + notes on right)
#                           -> presentation-with-notes.pdf (handout stays clean)
#
# Flags combine, e.g.  ./build.sh --strict --notes
set -euo pipefail
cd "$(dirname "$0")"

TEX=presentation.tex
JOBNAME=presentation
PRETEX=""
STRICT=0
for arg in "$@"; do
  case "$arg" in
    --strict) STRICT=1; PRETEX="${PRETEX}\\def\\strict{1}" ;;
    --notes)  JOBNAME=presentation-with-notes
              PRETEX="${PRETEX}\\PassOptionsToPackage{}{pgfpages}\\AtBeginDocument{\\setbeameroption{show notes on second screen=right}}" ;;
    *) echo "unknown flag: $arg" >&2; exit 2 ;;
  esac
done

run() {
  # inject pre-document TeX (strict/notes) ahead of \input; jobname picks the
  # output file (presentation.pdf, or presentation-with-notes.pdf for --notes)
  pdflatex -interaction=nonstopmode -halt-on-error -file-line-error \
    -jobname="$JOBNAME" "${PRETEX}\\input{${TEX}}"
}

# two passes so the n/N frame numbers resolve
run >/dev/null
run >build.log 2>&1 || { echo "LaTeX error, see build.log"; tail -20 build.log; exit 1; }

# flag out-of-bounds content: any Overfull box wider/taller than 2pt
mapfile -t OVER < <(grep -E 'Overfull \\(hbox|vbox)' build.log | while read -r line; do
  pt=$(printf '%s\n' "$line" | sed -E 's/.*\(([0-9.]+)pt.*/\1/')
  awk -v p="$pt" 'BEGIN{ exit !(p+0 > 2.0) }' && printf '%s\n' "$line"
done)

echo "built ${JOBNAME}.pdf ($(pdfinfo "${JOBNAME}.pdf" | awk '/Pages/{print $2}') pages)"
if [ "${#OVER[@]}" -eq 0 ]; then
  echo "no content out of bounds (>2pt)"
else
  echo "WARNING: ${#OVER[@]} box(es) out of bounds:" >&2
  printf '  %s\n' "${OVER[@]}" >&2
  if [ "$STRICT" -eq 1 ]; then
    echo "strict mode: failing build" >&2
    exit 1
  fi
fi
exit 0
