#!/usr/bin/env bash
# Install Signature so it works in any session on this computer.
#
#   ./install.sh --all                 Claude Code, Codex and the note below
#   ./install.sh --claude              the skill and the /restyle commands, for Claude Code and the desktop app
#   ./install.sh --codex               the skill, for Codex (use it as $jed-writing-style)
#   ./install.sh --global-note         a short note in ~/.claude/CLAUDE.md (and ~/.codex/AGENTS.md if Codex is
#                                      installed), so every session knows to use it
#   ./install.sh --project DIR         the same note, in one project's CLAUDE.md (and its AGENTS.md if it has one)
#   ./install.sh --uninstall           remove everything this script installed
#   ./install.sh --dry-run ...         say what would happen, change nothing
#
# It only copies files and edits one marked block. Run it again to update. It never touches anything else
# in CLAUDE.md or AGENTS.md. Folders can be moved with CLAUDE_HOME and CODEX_HOME.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_SRC="$HERE/skills/jed-writing-style"
CMD_SRC="$HERE/docs/personal-commands"
CLAUDE_HOME="${CLAUDE_HOME:-$HOME/.claude}"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
START="<!-- signature:start -->"
END="<!-- signature:end -->"

DO_CLAUDE=0; DO_CODEX=0; DO_NOTE=0; DO_UNINSTALL=0; DRY=0; PROJECT=""

usage() { sed -n '2,15p' "$0" | sed 's/^# \{0,1\}//'; }

while [ $# -gt 0 ]; do
  case "$1" in
    --all) DO_CLAUDE=1; DO_CODEX=1; DO_NOTE=1 ;;
    --claude) DO_CLAUDE=1 ;;
    --codex) DO_CODEX=1 ;;
    --global-note) DO_NOTE=1 ;;
    --project) shift; [ $# -gt 0 ] || { echo "install.sh: --project needs a folder" >&2; exit 2; }; PROJECT="$1" ;;
    --uninstall) DO_UNINSTALL=1 ;;
    --dry-run) DRY=1 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "install.sh: unknown option $1" >&2; usage >&2; exit 2 ;;
  esac
  shift
done

if [ $DO_CLAUDE$DO_CODEX$DO_NOTE$DO_UNINSTALL = 0000 ] && [ -z "$PROJECT" ]; then usage; exit 0; fi
[ -d "$SKILL_SRC" ] || { echo "install.sh: cannot find $SKILL_SRC. Run this from a clone of the repo." >&2; exit 2; }

say() { if [ $DRY = 1 ]; then echo "would: $*"; else echo "$*"; fi; }
run() { [ $DRY = 1 ] || "$@"; }

note_block() {
  cat <<'EOF'
<!-- signature:start -->
## Writing and restyling (Signature)

Anything written under Jed's name follows the `jed-writing-style` skill. It lives in
`~/.claude/skills/jed-writing-style` or `~/.codex/skills/jed-writing-style`. Load it before drafting, and
run its `scripts/ai_check.py` on finished drafts.

To bring a project's writing into Jed's style, or to make one change across all its files (Word,
PowerPoint, HTML, notebooks, Markdown, code comments), use `/restyle`, or `$jed-writing-style` in Codex. It
writes `STYLE_PLAN.md` and stops. Apply only what Jed approves, with `/restyle-apply`.

Change `.docx` and `.pptx` files only with the skill's `scripts/apply_edits.py`, never by saving them with a
library. Check them with `scripts/verify_office.py`. `references/office.md` says what to do in a session that
can't open Word or PowerPoint, or has no shell.

If the skill isn't installed here, run `git clone --depth 1 https://github.com/jedlwk/Signature /tmp/signature`
and follow `/tmp/signature/skills/jed-writing-style/SKILL.md`.
<!-- signature:end -->
EOF
}

# Remove our marked block from a file, leaving everything else as it was.
remove_block() {
  local f="$1"
  [ -f "$f" ] || return 0
  grep -qF "$START" "$f" || return 0
  say "remove the Signature note from $f"
  if [ $DRY = 0 ]; then
    awk -v s="$START" -v e="$END" 'index($0, s) {skip=1} !skip {print} index($0, e) {skip=0}' "$f" > "$f.signature.tmp"
    mv "$f.signature.tmp" "$f"
    # a file that is now only blank lines was ours alone, so remove it
    if ! grep -q '[^[:space:]]' "$f"; then rm -f "$f"; fi
  fi
}

add_block() {
  local f="$1"
  remove_block "$f" >/dev/null
  say "add the Signature note to $f"
  if [ $DRY = 0 ]; then
    mkdir -p "$(dirname "$f")"
    [ -s "$f" ] && printf '\n' >> "$f"
    note_block >> "$f"
  fi
}

is_ours() { [ -f "$1/SKILL.md" ] && grep -q '^name: jed-writing-style' "$1/SKILL.md"; }

copy_skill() {
  local dest="$1/skills/jed-writing-style"
  if [ -e "$dest" ] && ! is_ours "$dest"; then
    echo "install.sh: $dest exists and is not Signature's skill. Leaving it alone." >&2
    return 1
  fi
  say "copy the skill to $dest"
  if [ $DRY = 0 ]; then
    mkdir -p "$1/skills"
    rm -rf "$dest"
    cp -R "$SKILL_SRC" "$dest"
    find "$dest" -name __pycache__ -prune -exec rm -rf {} +
  fi
}

remove_skill() {
  local dest="$1/skills/jed-writing-style"
  if [ -e "$dest" ]; then
    if is_ours "$dest"; then say "remove $dest"; run rm -rf "$dest"
    else echo "install.sh: $dest is not Signature's skill. Leaving it alone." >&2; fi
  fi
}

if [ $DO_UNINSTALL = 1 ]; then
  remove_skill "$CLAUDE_HOME"
  remove_skill "$CODEX_HOME"
  for f in "$CMD_SRC"/*.md; do
    t="$CLAUDE_HOME/commands/$(basename "$f")"
    if [ -f "$t" ] && grep -q 'jed-writing-style' "$t"; then say "remove $t"; run rm -f "$t"; fi
  done
  remove_block "$CLAUDE_HOME/CLAUDE.md"
  remove_block "$CODEX_HOME/AGENTS.md"
  [ -z "$PROJECT" ] || { remove_block "$PROJECT/CLAUDE.md"; remove_block "$PROJECT/AGENTS.md"; }
  echo "Done. Restart your sessions."
  exit 0
fi

if [ $DO_CLAUDE = 1 ]; then
  copy_skill "$CLAUDE_HOME"
  say "copy the /restyle commands to $CLAUDE_HOME/commands"
  if [ $DRY = 0 ]; then mkdir -p "$CLAUDE_HOME/commands"; cp "$CMD_SRC"/*.md "$CLAUDE_HOME/commands/"; fi
fi
[ $DO_CODEX = 1 ] && copy_skill "$CODEX_HOME"
if [ $DO_NOTE = 1 ]; then
  add_block "$CLAUDE_HOME/CLAUDE.md"
  if [ $DO_CODEX = 1 ] || [ -d "$CODEX_HOME" ]; then add_block "$CODEX_HOME/AGENTS.md"; fi
fi
if [ -n "$PROJECT" ]; then
  [ -d "$PROJECT" ] || { echo "install.sh: $PROJECT is not a folder" >&2; exit 2; }
  add_block "$PROJECT/CLAUDE.md"
  [ ! -f "$PROJECT/AGENTS.md" ] || add_block "$PROJECT/AGENTS.md"
fi
echo "Done. Start a new session to pick it up."
