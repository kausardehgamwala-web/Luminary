"""
luminary_examples.py
====================
Gold-standard example library for few-shot prompting.
Provides the AI with high-quality examples of excellent outputs
to reference when generating its own responses.

Loaded by server.py and injected into AI prompts for relevant tasks.
"""


EXAMPLES = [
    {
        "id": "ex_ferrari_ppt",
        "category": "presentations",
        "trigger_keywords": ["ferrari", "presentation", "deck", "ppt"],
        "prompt": "Create a Ferrari brand presentation deck",
        "reasoning": "Brand presentation = research brand identity first, use exact brand colors, create narrative arc from heritage to innovation to future",
        "output_format": "### Slide N: [Title]\n- Key Takeaway: [bold statement]\n- Data Point: [real statistic]\n- Strategic Execution: [action step]",
        "quality_signals": ["Real brand colors (#E81C23 Ferrari Red, #FFF000 Ferrari Yellow)", "Heritage narrative (1947 founding)", "Racing pedigree data (16 F1 Constructors titles)", "Premium design language"],
        "score": 96,
    },
    {
        "id": "ex_luxury_image",
        "category": "image",
        "trigger_keywords": ["luxury", "car", "automotive", "ferrari", "lambo"],
        "prompt": "Generate a photorealistic image of a red Ferrari SF90 on a mountain road at sunset",
        "reasoning": "Automotive photography = low hero angle, golden hour lighting, depth of field to separate car from background, proper camera specification",
        "output_format": "Red Ferrari SF90 Stradale, glossy Rosso Corsa paint, mountain winding road, golden hour sunset, warm amber light raking across body panels, low hero angle shot, Canon EOS R5 70-200mm f/2.8, shallow depth of field, background bokeh, cinematic color grade, 8K ultra-realistic",
        "quality_signals": ["Specific model name", "Exact color name", "Camera + lens spec", "Lighting setup", "Composition direction"],
        "score": 94,
    },
    {
        "id": "ex_marketing_strategy",
        "category": "text",
        "trigger_keywords": ["strategy", "marketing", "campaign", "brand"],
        "prompt": "Create a marketing strategy for a luxury car dealership",
        "reasoning": "Marketing strategy = audience definition + competitor landscape + channel mix + KPIs + timeline. Use SWOT and AIDA frameworks.",
        "output_format": "# Executive Summary\n## Target Audience\n## Competitive Landscape\n## Channel Strategy\n## Content Pillars\n## KPIs & Metrics\n## 90-Day Action Plan",
        "quality_signals": ["SWOT analysis", "Specific KPIs (CTR, CAC, LTV)", "Platform-specific tactics", "Budget allocation", "Timeline with milestones"],
        "score": 93,
    },
    {
        "id": "ex_instagram_post",
        "category": "social_media",
        "trigger_keywords": ["instagram", "post", "caption", "social media"],
        "prompt": "Write an Instagram post for a luxury watch brand launch",
        "reasoning": "Instagram = hook in first line (stops scroll), emotional connection, aspirational language, 3-5 relevant hashtags, clear CTA",
        "output_format": "Hook line.\n\nBody paragraph (2-3 lines max).\n\nEmotional close or CTA.\n\n#hashtag1 #hashtag2 #hashtag3",
        "quality_signals": ["Scroll-stopping first line", "Brand voice consistency", "Emotional aspiration", "Specific product detail", "Strategic hashtags"],
        "score": 91,
    },
    {
        "id": "ex_financial_spreadsheet",
        "category": "spreadsheets",
        "trigger_keywords": ["spreadsheet", "excel", "financial", "budget", "data"],
        "prompt": "Create a financial projection spreadsheet for a startup",
        "reasoning": "Financial spreadsheet = clear headers, proper number formats, SUM formulas at totals, conditional formatting for positive/negative, freeze pane on headers",
        "output_format": "| Month | Revenue | COGS | Gross Profit | Expenses | Net Income |\n|-------|---------|------|-------------|----------|------------|",
        "quality_signals": ["Column headers in proper format", "Realistic numbers", "Formulas shown", "Professional layout description", "Data types consistent"],
        "score": 92,
    },
    {
        "id": "ex_seo_article",
        "category": "text",
        "trigger_keywords": ["seo", "blog", "article", "write", "content"],
        "prompt": "Write an SEO-optimized article about electric vehicles",
        "reasoning": "SEO article = target keyword in H1 + first 100 words, H2 subheadings every 300 words, internal linking opportunities, meta description, 1500+ words for ranking",
        "output_format": "# [Keyword-Rich H1 Title]\n[Meta: 155-char description]\n\n## Introduction (keyword in para 1)\n## [H2 with secondary keyword]\n## [H2 with related keyword]\n## FAQ Section\n## Conclusion with CTA",
        "quality_signals": ["Keyword in H1", "Meta description", "Proper H2 hierarchy", "Natural keyword density", "FAQ section for featured snippets"],
        "score": 90,
    },
    {
        "id": "ex_investor_deck",
        "category": "presentations",
        "trigger_keywords": ["investor", "pitch", "startup", "funding", "deck"],
        "prompt": "Create a startup investor pitch deck",
        "reasoning": "Investor pitch = problem slide first, solution, market size (TAM/SAM/SOM), traction, business model, team, ask. One idea per slide. Data-heavy.",
        "output_format": "### Slide 1: Problem\n### Slide 2: Solution\n### Slide 3: Market Size ($TAM/$SAM/$SOM)\n### Slide 4: Traction\n### Slide 5: Business Model\n### Slide 6: Team\n### Slide 7: The Ask",
        "quality_signals": ["TAM/SAM/SOM numbers", "Traction metrics", "Clear ask ($X for Y%)", "Team credibility", "Competitive moat"],
        "score": 95,
    },
    {
        "id": "ex_product_image",
        "category": "image",
        "trigger_keywords": ["product", "photo", "image", "shoot"],
        "prompt": "Generate a product photo of a luxury perfume bottle",
        "reasoning": "Product photography = white or gradient background, hero lighting, material callouts (glass, chrome cap), professional studio setup",
        "output_format": "Luxury perfume bottle, clear crystal glass with gold chrome cap, soft white seamless background, studio split lighting creating elegant highlights on glass, product photography style, Canon 100mm macro lens, f/8 aperture, perfectly centered, commercial grade, ultra sharp focus, reflection on surface",
        "quality_signals": ["Material specification", "Lighting setup", "Camera setup", "Background description", "Commercial grade qualifier"],
        "score": 93,
    },
]


def get_relevant_examples(prompt: str, max_examples: int = 2) -> str:
    """
    Returns formatted few-shot examples most relevant to the given prompt.
    Injects them into the AI system prompt for reference.
    """
    prompt_lower = prompt.lower()

    scored = []
    for ex in EXAMPLES:
        match_score = sum(
            1 for kw in ex["trigger_keywords"]
            if kw in prompt_lower
        )
        if match_score > 0:
            scored.append((match_score, ex))

    scored.sort(key=lambda x: -x[0])
    selected = [ex for _, ex in scored[:max_examples]]

    if not selected:
        # Return the single highest-quality general example
        selected = [max(EXAMPLES, key=lambda e: e["score"])]

    parts = ["### GOLD-STANDARD EXAMPLES (Reference these for quality standards):"]
    for ex in selected:
        parts.append(
            f"\n**Example [{ex['category'].upper()}] (Quality Score: {ex['score']}/100)**\n"
            f"Prompt: \"{ex['prompt']}\"\n"
            f"Reasoning: {ex['reasoning']}\n"
            f"Output format used:\n{ex['output_format']}\n"
            f"Quality signals: {', '.join(ex['quality_signals'])}"
        )

    return "\n".join(parts)
