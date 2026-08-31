import file_generator
import time
from pathlib import Path
out_dir = Path('generated')
out_dir.mkdir(exist_ok=True)

# Generate DOCX
docx_path = out_dir / f'test_doc_{int(time.time())}.docx'
file_generator.generate_docx('<h1>Test Document</h1><p>Hello world!</p>', str(docx_path), prompt='Test Doc')

# Generate PPTX (with an image to test the unvalidated URL fix!)
pptx_path = out_dir / f'test_ppt_{int(time.time())}.pptx'
markdown_ppt = '''
# Slide 1
This is a test slide.
![Image](https://www.w3.org/html/logo/downloads/HTML5_Logo_512.png)
'''
file_generator.generate_pptx(markdown_ppt, str(pptx_path), prompt='Test PPTX')

# Generate XLSX
xlsx_path = out_dir / f'test_sheet_{int(time.time())}.xlsx'
markdown_sheet = '''
| Header 1 | Header 2 |
| -------- | -------- |
| Value 1  | Value 2  |
'''
file_generator.generate_xlsx(markdown_sheet, str(xlsx_path), prompt='Test XLSX')

print(f'Generated files:')
print(f'  {docx_path}')
print(f'  {pptx_path}')
print(f'  {xlsx_path}')

# Generate Image
import local_sdxl_service
img = local_sdxl_service.sdxl_service.generate(prompt='a red apple on a white table', num_inference_steps=5, width=512, height=512)
img_path = out_dir / f'test_img_{int(time.time())}.jpg'
img.save(img_path)
print(f'  {img_path}')
