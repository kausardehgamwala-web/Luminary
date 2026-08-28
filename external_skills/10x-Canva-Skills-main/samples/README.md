# Samples & Reference Library

This folder contains your personal design preferences, samples, and references that the Canva skills use to understand your style and create consistent outputs.

## Folder Structure

```
samples/
├── images/                    # Image design samples
│   ├── social-media/          # Instagram, Facebook, Twitter posts
│   ├── posters/               # Poster designs
│   ├── logos/                 # Logo designs
│   └── banners/               # Banner and cover designs
│
├── presentations/             # Presentation samples
│   ├── pitch-decks/           # Business pitch decks
│   ├── reports/               # Report presentations
│   └── educational/           # Educational slides
│
├── videos/                    # Video design samples
│   ├── reels/                 # Short-form videos (Reels, TikTok)
│   ├── ads/                   # Advertisement videos
│   └── intros/                # Intro/outro sequences
│
├── brand-kits/                # Brand identity files
│   ├── brand-config.json      # Main brand configuration
│   ├── colors.json            # Color palette
│   ├── typography.json        # Font specifications
│   └── logos/                 # Brand logos
│
├── color-palettes/            # Color palette references
│
├── fonts/                     # Font preference files
│
└── templates/                 # Custom templates
```

## How to Add Your Samples

### Adding Image Samples

1. Export or screenshot your favorite designs from Canva
2. Place them in the appropriate subfolder (e.g., `images/social-media/`)
3. Optionally add a `_caption.txt` file with the same name containing the text used
4. The more samples you add, the better the AI learns your style

**Example:**
```
images/social-media/
├── summer_sale_post.png
├── summer_sale_post_caption.txt    # Contains the caption text
├── product_launch.png
├── product_launch_caption.txt
└── style_notes.txt                 # General style preferences
```

### Adding Presentation Samples

1. Export presentation slides as images (one per slide)
2. Or export the full presentation as PDF
3. Add notes about your presentation style preferences

**Example:**
```
presentations/pitch-decks/
├── startup_pitch/
│   ├── slide_01_cover.png
│   ├── slide_02_problem.png
│   ├── slide_03_solution.png
│   └── outline.txt
└── style_notes.txt
```

### Adding Video References

1. Export thumbnail/keyframes from your favorite videos
2. Note your preferred style elements
3. Include examples of text overlays, transitions you like

### Setting Up Brand Kit

Create a `brand-config.json` in `brand-kits/`:

```json
{
  "brand_name": "Your Brand Name",
  "tagline": "Your Tagline",
  "colors": {
    "primary": "#2E86AB",
    "secondary": "#F4D35E",
    "accent": "#EE6352",
    "background": "#FFFFFF",
    "text": "#1A1A1A"
  },
  "fonts": {
    "heading": "Montserrat",
    "body": "Open Sans"
  },
  "voice": {
    "tone": "professional yet friendly",
    "style": "modern, clean, minimal"
  }
}
```

## Style Notes Files

Create `style_notes.txt` in any folder to describe your preferences:

```txt
# My Social Media Style Preferences

## Colors
- Prefer bright, vibrant colors
- Always use brand blue (#2E86AB) as accent
- White or light gray backgrounds

## Typography
- Headlines: Bold, uppercase
- Body: Regular weight, sentence case
- Max 2 fonts per design

## Layout
- Clean, minimal layouts
- Plenty of white space
- Left-aligned text preferred

## Imagery
- High contrast photos
- Prefer lifestyle over product shots
- Occasional use of illustrations

## Emojis
- Use sparingly
- Only at beginning or end of captions
- Prefer: ✨ 🚀 💡 🎯

## Hashtags
- 10-15 per Instagram post
- Mix of broad and niche tags
- Always include brand hashtag
```

## How Skills Use These Samples

1. **canva-content-generator**: Analyzes your caption styles, tone, and hashtag usage
2. **canva-image-editor**: References your color and layout preferences
3. **canva-presentation**: Uses your slide structure and design patterns
4. **canva-brand-kit**: Loads your brand configuration for consistency
5. **canva-video**: References your video style preferences

## Tips for Better Results

1. **Add More Samples**: The AI learns better with more examples (10+ per category)
2. **Include Variations**: Show different styles you use for different purposes
3. **Be Specific in Notes**: The more detail, the better the AI understands
4. **Update Regularly**: Add new favorites as your style evolves
5. **Organize by Purpose**: Separate work vs. personal, client A vs. client B

## Sharing This Plugin

When sharing this plugin with others:
- The `samples/` folder is YOUR personal preferences
- Others should populate their own samples
- Include example structure but not your actual designs
- Consider creating a `samples-template/` for reference

---

*Add your designs and preferences to make this skill truly yours!*
