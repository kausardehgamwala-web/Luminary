# Input Folder

Place files here that you want to upload to Canva.

## Purpose

This folder is the staging area for:
- Images to upload to your Canva asset library
- Videos to add to your Canva account
- Audio files for video projects
- Any media files for batch uploads

## Supported File Types

### Images
- PNG, JPG/JPEG (up to 25MB)
- SVG (up to 3MB)
- GIF, WebP, HEIC (up to 25MB)

### Videos
- MP4, MOV, WebM, M4V (up to 1GB)

### Audio
- MP3, WAV, M4A, OGG (up to 250MB)

## Folder Structure

Organize your uploads by type:

```
input/
├── images/           # Images to upload
│   ├── logos/
│   ├── photos/
│   └── graphics/
├── videos/           # Videos to upload
├── audio/            # Audio files to upload
└── urls.txt          # List of URLs for URL-based uploads
```

## Usage

### Single File Upload
```bash
python scripts/upload_asset.py --file input/my-image.png
```

### Batch Upload
```bash
python scripts/batch_upload.py --folder input/images/ --pattern "*.png"
```

### URL-Based Upload
Create a `urls.txt` file with one URL per line:
```
https://example.com/image1.png
https://example.com/image2.jpg
```

Then run:
```bash
python scripts/batch_url_upload.py --urls-file input/urls.txt
```

## Notes

- Files are NOT automatically deleted after upload
- Large files may take time to process
- Check `output/uploads/` for upload logs and status
