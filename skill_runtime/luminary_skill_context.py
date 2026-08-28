import json
import re
from pathlib import Path

SKILL_INDEX = Path(__file__).resolve().parent / "luminary_skill_context.json"

BLOCKED_ACTION_PATTERNS = [
    r"\bdelete\b.*\bfile",
    r"\bRemove-Item\b",
    r"\brm\s+-rf\b",
    r"\bformat\b",
    r"\bpassword\b|\btoken\b|\bcookie\b|\bsecret\b|\bssh key\b",
    r"\binstall\b\s+\w+|\bgit clone\b",
    r"\bfirewall\b|\bregistry\b|\badmin\b",
]


def load_skill_index() -> dict:
    if not SKILL_INDEX.exists():
        return {"skills": [], "policy": "No skill index has been built yet."}
    return json.loads(SKILL_INDEX.read_text(encoding="utf-8"))


def requires_approval(prompt: str) -> bool:
    return any(re.search(pattern, prompt, re.IGNORECASE) for pattern in BLOCKED_ACTION_PATTERNS)


def select_skill_context(prompt: str, max_chars: int = 5000) -> str:
    index = load_skill_index()
    prompt_l = prompt.lower()
    chunks = [f"Safety policy: {index.get('policy', '')}"]

    category_keywords = {
        "marketing": ["marketing", "campaign", "seo", "content", "brand", "social", "growth", "funnel"],
        "documents": ["document", "doc", "report", "proposal", "brief"],
        "presentations": ["ppt", "powerpoint", "slides", "deck", "presentation"],
        "research": ["research", "study", "paper", "evidence", "analyze"],
        "testing": ["playwright", "test", "browser", "qa"],
        "sales": ["sales", "lead", "prospect", "objection", "pipeline"],
        "video": ["video", "caption", "editing", "script"],
        "youtube": ["youtube", "shorts", "thumbnail", "channel audit", "video seo"],
        "linkedin": ["linkedin", "linkedin audit", "linkedin post", "linkedin profile"],
        "social_media": ["instagram", "social media", "channel audit", "content calendar", "reels"],
        "blog_writing": ["blog", "article", "post", "seo article", "write a blog"],
        "content_workflow": ["content pipeline", "content workflow", "repurpose", "publishing workflow"],
        "creator_education": ["creator", "creator academy", "audience growth"],
        "prompting": ["prompt", "understand prompt", "execute prompt", "improve prompt"],
        "illustration": ["illustration", "illustrator", "visual asset", "graphic"],
        "report_writing": ["report", "write report", "manuscript", "whitepaper"],
        "cms": ["payload", "cms", "content model"],
        "wordpress": ["wordpress", "generateblocks"],
        "site_audit": ["site audit", "website audit", "seo audit", "audit my website"],
        "spreadsheets": ["excel", "spreadsheet", "xlsx", "csv", "sheet", "data analysis"],
        "skill_runtime": ["skill runtime", "skill directory", "skill search"],
        "verified_skills": ["verified skill", "signed skill", "skill governance"],
        "memory": ["memory", "remember", "chat history", "previous chat", "saved chat", "same user", "account memory"],
        "computer_access": ["computer", "desktop", "operate", "control my pc"],
        "privacy": ["privacy", "pii", "personal data", "redact", "anonymize", "unsafe data", "sensitive data"],
        "skill_security": ["unsafe skill", "malicious skill", "skill security", "audit skill", "permission", "dangerous repo"],
        "knowledge_base": ["knowledge base", "business facts", "luminary offers", "pricing", "clients", "tone", "processes"],
        "vector_search": ["embedding", "embeddings", "vector", "semantic search", "chroma"],
        "citations": ["cite", "citation", "source", "sources", "which repo", "informed"],
        "retrieval": ["rag", "retrieve", "retrieval", "context search"],
        "graphic_design": ["design", "canva", "nano banana", "higgsfield", "color", "typography", "font", "aesthetic", "flyer", "promo"],
        "image_editing": ["edit image", "crop", "remove object", "inpaint", "img2img", "image prompt"],
        "social_publishing": ["publish", "post", "schedule", "pinterest", "youtube", "instagram", "tiktok", "linkedin", "facebook", "twitter", "tweet"]
    }

    selected_categories = {
        category
        for category, keywords in category_keywords.items()
        if any(keyword in prompt_l for keyword in keywords)
    }

    # Sort skills: ones matching selected_categories first, others second
    all_skills = index.get("skills", [])
    relevant_skills = []
    other_skills = []
    
    for skill in all_skills:
        if skill.get("status") == "restricted" and skill.get("category") == "computer_access":
            continue
        if selected_categories and skill.get("category") in selected_categories:
            relevant_skills.append(skill)
        else:
            other_skills.append(skill)
            
    sorted_skills = relevant_skills + other_skills

    for skill in sorted_skills:
        chunks.append(
            f"Skill: {skill.get('name')} | Category: {skill.get('category')} | Use: {skill.get('default_use')}"
        )
        for excerpt in skill.get("excerpts", [])[:2]:
            chunks.append(f"From {skill.get('name')}/{excerpt.get('path')}:\n{excerpt.get('text')}")

        if sum(len(chunk) for chunk in chunks) >= max_chars:
            break

    return "\n\n".join(chunks)[:max_chars]
