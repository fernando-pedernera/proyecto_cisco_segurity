"""Render ```mermaid blocks in Markdown files to PNG (via mermaid.ink) and embed them.

Each mermaid block is replaced by a clickable image (opens full size for zooming)
plus a collapsible <details> section that keeps the original Mermaid source.

Idempotent: already-rendered sections are detected and re-rendered from the
source kept in <details>, so editing that source and re-running updates the PNG.

Usage:  python tools\\render_diagrams.py
"""
import base64
import pathlib
import re
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "diagrams"
IMG_WIDTH = 1600  # px; higher = sharper when zooming

# Matches either a raw mermaid block, or a previously rendered section
# (optional clickable image + <details> wrapper around the mermaid block).
SECTION = re.compile(
    r"(?:\[?!\[[^\]]*\]\(diagrams/[^)]+\)(?:\]\(diagrams/[^)]+\))?\n\n"
    r"<details>\n<summary>Mermaid source</summary>\n\n)?"
    r"```mermaid\n(.*?)```"
    r"(?:\n\n</details>)?",
    re.S,
)


def render(code: str, target: pathlib.Path) -> None:
    payload = base64.urlsafe_b64encode(code.encode("utf-8")).decode("ascii")
    url = f"https://mermaid.ink/img/{payload}?type=png&bgColor=FFFFFF&width={IMG_WIDTH}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read()
    if not data.startswith(b"\x89PNG"):
        raise RuntimeError(f"Unexpected response for {target.name}: {data[:200]!r}")
    target.write_bytes(data)


def process(path: pathlib.Path) -> None:
    text = path.read_text(encoding="utf-8")
    counter = 0

    def replace(match: re.Match) -> str:
        nonlocal counter
        counter += 1
        code = match.group(1)
        img = f"diagrams/{path.stem}_diagram{counter}.png"
        render(code, ROOT / img)
        print(f"  rendered {img}")
        return (
            f"[![Diagram {counter} (click to enlarge)]({img})]({img})\n\n"
            f"<details>\n<summary>Mermaid source</summary>\n\n"
            f"```mermaid\n{code}```\n\n</details>"
        )

    new_text = SECTION.sub(replace, text)
    if counter:
        path.write_text(new_text, encoding="utf-8")
    print(f"{path.name}: {counter} diagram(s)")


def main() -> int:
    OUT_DIR.mkdir(exist_ok=True)
    for path in sorted(ROOT.glob("*.md")):
        process(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
