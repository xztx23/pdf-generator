import sys
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

def generate_pdf_html(report_text: str) -> str:
    """将报告文本包装为符合格式要求的 HTML"""
    lines = report_text.strip().splitlines()
    html_lines = []
    h1_flag = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(('一、', '二、', '三、')):
            if h1_flag:
                html_lines.append(f'<h1 class="break-before">{stripped}</h1>')
            else:
                html_lines.append(f'<h1>{stripped}</h1>')
                h1_flag = True
        else:
            html_lines.append(f'<p>{stripped}</p>')
    content = '\n'.join(html_lines)
    return f'''<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>论文审查报告</title>
<style>
@page {{ size: A4; margin: 2.5cm 2.2cm; }}
body {{
    font-family: "WenQuanYi Micro Hei", "Noto Sans CJK SC", "SimHei", "Microsoft YaHei", "PingFang SC", "Apple LiGothic", "Droid Sans Fallback", sans-serif;
    margin:0;
    line-height:1.5;
}}
.doc-title {{
    font-size: 16pt;
    font-weight: bold;
    text-align: center;
    margin: 1cm 0 2cm 0;
}}
h1 {{
    font-size: 14pt;
    font-weight: bold;
    text-align: left;
    margin: 1.2em 0 0.8em 0;
}}
h1.break-before {{
    page-break-before: always;
}}
p, li {{
    font-size: 12pt;
    line-height: 1.5;
    margin: 0.5em 0;
}}
.content {{
    white-space: pre-wrap;
}}
</style>
</head>
<body>
<div class="doc-title">论文审查报告</div>
<div class="content">{content}</div>
</body>
</html>'''

def html_to_pdf_bytes(html: str) -> bytes:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html)
        pdf_bytes = page.pdf(format="A4")
        browser.close()
        return pdf_bytes

def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_pdf.py <student_id> <report_text>")
        sys.exit(1)
    student_id = sys.argv[1]
    report_text = sys.argv[2]
    html = generate_pdf_html(report_text)
    pdf_bytes = html_to_pdf_bytes(html)
    # 创建 PDF 目录
    pdf_dir = Path("PDF")
    pdf_dir.mkdir(exist_ok=True)
    pdf_path = pdf_dir / f"{student_id}.pdf"
    pdf_path.write_bytes(pdf_bytes)
    print(f"PDF saved to {pdf_path}")

if __name__ == '__main__':
    main()
