---
name: canva
description: Main command for Canva operations. Routes to appropriate skill based on request.
---

# /canva Command

The main entry point for all Canva operations.

## Usage

```
/canva [operation] [options]
```

## Operations

### Explore
View your Canva account contents:
```
/canva explore
/canva explore designs
/canva explore folders
/canva explore assets
```

### Export
Export designs to various formats:
```
/canva export [design-name] --format pdf
/canva export [design-name] --format png --quality high
/canva export-all [folder-name] --format pdf
```

### Edit
Modify designs:
```
/canva edit image [design-name]
/canva edit presentation [design-name]
/canva edit video [design-name]
```

### Organize
Manage folders and organization:
```
/canva organize create-folder [name]
/canva organize move [items] to [folder]
/canva organize cleanup
```

### Upload
Upload assets to Canva:
```
/canva upload [file-path]
/canva upload-folder [folder-path]
/canva upload-url [url]
```

### Brand
Manage brand kit:
```
/canva brand check [design-name]
/canva brand apply [design-name]
/canva brand setup
```

### Content
Generate content:
```
/canva content headlines [topic]
/canva content caption [platform] [topic]
/canva content outline [presentation-type]
```

## Workflow

All operations follow the 3-mode workflow:

1. **PLAN** - Analyze request and create operation plan
2. **CLARIFY** - Ask questions and get user confirmation
3. **IMPLEMENT** - Execute the approved plan

## Examples

### Export a presentation
```
/canva export "Q4 Report" --format pptx
```

### Organize messy folder
```
/canva organize cleanup "Random Designs"
```

### Create Instagram content
```
/canva content caption instagram "New Product Launch"
```

### Check brand consistency
```
/canva brand check "Marketing Materials"
```

## Configuration

Before using, ensure:
1. `.env` file is configured with Canva credentials
2. OAuth flow completed (access token obtained)
3. Required Python packages installed

Run `/canva setup` to check configuration.

## Help

```
/canva help
/canva help [operation]
```
