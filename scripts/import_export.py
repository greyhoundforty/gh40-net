"""One-off converter: gh40-export/*.md (bearblog export) -> src/pages/posts/*.mdx."""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

SLUGS = [
    "2024-homelab-recap",
    "homelab-monitoring",
    "default-apps-2025",
    "expose-local-services-to-your-tailnet-and-beyond-with-serve-and-funnel",
    "claude-oco",
    "claude-mcp-cookiecutter",
    "ibmcloud-vpc-mcp",
    "tg-ssh-manager",
    "new-project-kylfuskofu",
    "seven-songs-the-beths",
    "thanks-i-hate-it",
    "today-i-found-volume-2",
    "today-i-found-volume-3",
    "today-i-found-volume-2025-01-03",
    "today-i-found-volume-2025-01-09",
    "today-i-found-volume-2025-03-03",
]
TAG_RENAMES = {"today-i-found": "todayifound"}

INLINE_CODE = re.compile(r"(`+[^`\n]*`+)")
# a "<" that does not start a tag, closing tag, comment, or autolink
BARE_LT = re.compile(r"<(?!/?[A-Za-z][^>\n]*>|!--)")
# MDX has no <https://...> autolinks; turn them into markdown links
AUTOLINK = re.compile(r"<(https?://[^>\s]+)>")


def parse(text: str) -> tuple[dict, str]:
    _, fm, body = text.split("---\n", 2)
    meta = {}
    for line in fm.splitlines():
        if ": " in line or line.rstrip().endswith(":"):
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip()
    return meta, body.lstrip("\n")


def plain_first_line(body: str, limit: int = 160) -> str:
    for line in body.splitlines():
        line = line.strip()
        if not line or line.startswith(("---", "```", "!", "<")):
            continue
        line = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", line)
        line = re.sub(r"[#*_`>]", "", line).strip()
        if line:
            if len(line) <= limit:
                return line
            return line[:limit].rsplit(" ", 1)[0].rstrip(",;:-") + "…"
    return ""


def escape_segment(seg: str) -> str:
    seg = AUTOLINK.sub(r"[\1](\1)", seg)
    seg = seg.replace("{", r"\{").replace("}", r"\}")
    return BARE_LT.sub("&lt;", seg)


def escape_body(body: str) -> str:
    out, fence = [], None
    for line in body.split("\n"):
        marker = re.match(r"\s*(```|~~~)", line)
        if marker:
            fence = None if fence == marker.group(1) else (fence or marker.group(1))
            out.append(line)
        elif fence:
            out.append(line)
        else:
            parts = INLINE_CODE.split(line)
            out.append(
                "".join(p if i % 2 else escape_segment(p) for i, p in enumerate(parts))
            )
    return "\n".join(out)


def convert_text(text: str) -> str:
    meta, body = parse(text)
    date = datetime.fromisoformat(meta["published_date"])
    description = meta.get("meta_description") or plain_first_line(body)
    tags = [t.strip() for t in meta.get("tags", "").split(",") if t.strip()]
    tags = [TAG_RENAMES.get(t, t) for t in tags]
    lines = [
        "---",
        'layout: "@/layouts/BlogPost"',
        f"title: {json.dumps(meta['title'], ensure_ascii=False)}",
        f"publishDate: {date.strftime('%d %B %Y')}",
        f"description: {json.dumps(description, ensure_ascii=False)}",
    ]
    if tags:
        lines.append(f"tags: {json.dumps(tags)}")
    lines += ["---", "", escape_body(body).rstrip("\n"), ""]
    return "\n".join(lines)


def main(export_dir: str, out_dir: str) -> int:
    src, dst = Path(export_dir), Path(out_dir)
    existing = [s for s in SLUGS if (dst / f"{s}.mdx").exists()]
    if existing:
        print("refusing to overwrite:", ", ".join(existing), file=sys.stderr)
        return 1
    for slug in SLUGS:
        (dst / f"{slug}.mdx").write_text(convert_text((src / f"{slug}.md").read_text()))
        print("wrote", slug)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
