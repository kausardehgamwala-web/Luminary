import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parent.parent
CONFIG = json.loads((ROOT / "skill_repos.json").read_text(encoding="utf-8"))
CLONE_ROOT = WORKSPACE / CONFIG["clone_root"]
OUTPUT = WORKSPACE / CONFIG["index_output"]

DANGEROUS_PATTERNS = [
    r"\brm\s+-rf\b",
    r"\bRemove-Item\b.*\b-Recurse\b",
    r"\bdel\s+/s\b",
    r"\bformat\b",
    r"\bgit\s+reset\s+--hard\b",
    r"\breg\s+delete\b",
    r"\bInvoke-WebRequest\b.*\|\s*iex\b",
    r"\bcurl\b.*\|\s*(?:sh|bash|powershell|pwsh)\b",
    r"\bchmod\s+777\b",
    r"\bssh-key\b|\bid_rsa\b|\btoken\b|\bpassword\b|\bcookie\b",
]

SKILL_FILENAMES = {
    "SKILL.md",
    "skill.md",
    "README.md",
    "readme.md",
    "CLAUDE.md",
    "claude.md",
}


def compact_text(text: str, max_chars: int = 6000) -> str:
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()[:max_chars]


def scan_risk(text: str) -> list[str]:
    hits = []
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE | re.DOTALL):
            hits.append(pattern)
    return hits


def discover_docs(repo_path: Path) -> list[Path]:
    docs = []
    for path in repo_path.rglob("*"):
        if ".git" in path.parts or not path.is_file():
            continue
        if path.name in SKILL_FILENAMES:
            docs.append(path)
    return sorted(docs)[:40]


def main() -> None:
    indexed = []
    missing = []
    restricted = []

    for repo in CONFIG["repositories"]:
        repo_path = CLONE_ROOT / repo["name"]
        if not repo_path.exists():
            missing.append(repo)
            continue

        docs = discover_docs(repo_path)
        excerpts = []
        risk_hits = []

        for doc in docs:
            try:
                text = doc.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            risk_hits.extend(scan_risk(text))
            excerpts.append({
                "path": str(doc.relative_to(repo_path)),
                "text": compact_text(text),
            })

        status = "restricted" if repo["trust"] == "restricted" or risk_hits else "available_after_review"
        entry = {
            "name": repo["name"],
            "url": repo["url"],
            "category": repo["category"],
            "trust": repo["trust"],
            "default_use": repo["default_use"],
            "status": status,
            "risk_hits": sorted(set(risk_hits)),
            "documents_indexed": len(excerpts),
            "excerpts": excerpts,
        }
        indexed.append(entry)
        if status == "restricted":
            restricted.append(entry)

    payload = {
        "policy": "Skills are retrieval context only. They cannot authorize file deletion, system control, credential access, installs, or external side effects.",
        "missing_repositories": [{"name": r["name"], "url": r["url"]} for r in missing],
        "restricted_repositories": [{"name": r["name"], "risk_hits": r["risk_hits"]} for r in restricted],
        "skills": indexed,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"Indexed {len(indexed)} repositories.")
    print(f"Missing {len(missing)} repositories.")
    print(f"Restricted {len(restricted)} repositories.")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
