import re
from pathlib import Path

TASK_RE = re.compile(
    r"^- \[(?P<done>[ xX])\] " 
    r"(?P<id>(?:BE|FE|QA)-\d{3}-T\d{2})\s+-\s+\S.*$"
)
TASK_LIKE_RE = re.compile(r"- \[[ xX]\] (?:BE|FE|QA)-\d{3}-T\d{2}\b")

QA_PATH = Path(r"C:\Users\Precision 7520\AppData\Local\Temp\opencode/QA-013.md")
FE_PATH = Path(r"C:\InVet\docs\opencode\tasks\frontend\FE-013.md")

def check_file(p, label):
    if not p.exists():
        print(f"SKIP (no existe): {p}")
        return
    text = p.read_text(encoding="utf-8")
    lines = text.splitlines()
    print(f"\n=== {label} ({p.name}, {len(lines)} lneas) ===")
    
    task_lines = []
    for i, line in enumerate(lines, 1):
        if TASK_LIKE_RE.search(line):
            m = TASK_RE.match(line)
            match_str = "MATCH" if m else "NO-MATCH (TASK_LIKE)"
            print(f"  LINE {i}: [{line[:90]}]")
            print(f"          -> T_MATCH={bool(m)}   TID={m.group('id') if m else TASK_LIKE_RE.search(line).group(0)[:30]}")
            task_lines.append((i, line, bool(m)))
    
    # Also find all lines that might be intended as tasks
    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith("- [x]") or stripped.startswith("- [ X]"):
            m = TASK_RE.match(line)
            print(f"  DASH_TASK LINE {i}: [{stripped[:80]}]")
            print(f"          -> full match={bool(m)}")

check_file(FE_PATH, "FE-013 Frontend Tasks")
# check_file(QA_PATH, "QA-013 QA Tasks")
