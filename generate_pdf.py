import sys
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

def clean_line(line: str) -> str:
    line = re.sub(r'[\u200b\u200c\u200d\u2060\uFEFF]', '', line)
    line = line.strip()
    line = re.sub(r'[ \t]+', ' ', line)
    return line

def is_junk_number_line(line: str) -> bool:
    stripped = line.strip()
    if re.fullmatch(r'(\d+\.\s*)+', stripped):
        return True
    if re.fullmatch(r'(\d+\s+)+', stripped):
        return True
    numbers = re.findall(r'\d+', stripped)
    if len(numbers) > 20 and len(stripped) > 100:
        return True
    return False

def parse_elements(text: str):
    lines = text.splitlines()
    elements = []
    for raw_line in lines:
        line = clean_line(raw_line)
        if not line:
            continue
        # 跳过单独的“论文审查报告”（大小写、全半角变化）
        if re.fullmatch(r'论文审查报告', line):
            continue
        if is_junk_number_line(line):
            continue

        h1_match = re.match(r'^#*\s*([一二三]、.*)$', line)
        if h1_match:
            h1_text = h1_match.group(1)
            if not re.fullmatch(r'论文审查报告', h1_text):
                elements.append(('h1', h1_text))
        elif line.startswith(('一、', '二、', '三、')):
            elements.append(('h1', line))
        else:
            elements.append(('p', line))
    return elements

def build_html(elements):
    html_parts = []
    first_h1 = False
    for typ, content in elements:
        if typ == 'h1':
            if first_h1:
                html_parts.append(f'<h1 class="break-before">{content}</h1>')
            else:
                html_parts.append(f'<h1>{content}</h1>')
                first_h1 = True
        else:
            html_parts.append(f'<p>{content}</p>')
    content_html = '\n'.join(html_parts)

    return f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>论文审查报告</title>
<style>
    @font-face {{
        font-family: 'TimesNewRoman';
        src: local('Times New Roman'), local('TimesNewRoman'), local('Times');
        font-weight: normal;
        font-style: normal;
    }}
    @page {{
        size: A4;
        margin: 2cm;
    }}
    body {{
        font-family: 'TimesNewRoman', 'Liberation Serif', 'Times', 'Noto Serif CJK SC', 'SimSun', '宋体', serif;
        font-size: 12pt;
        line-height: 1.5;
        margin: 0;
        padding: 0;
        background: white;
    }}
    .doc-title {{
        font-family: 'SimHei', 'Noto Sans CJK SC', 'Microsoft YaHei', '黑体', 'TimesNewRoman', sans-serif;
        font-size: 16pt;
        font-weight: bold;
        text-align: center;
        margin: 1em 0 1em 0;
        line-height: 1.5;
    }}
    h1 {{
        font-family: 'SimHei', 'Noto Sans CJK SC', 'Microsoft YaHei', '黑体', 'TimesNewRoman', sans-serif;
        font-size: 14pt;
        font-weight: bold;
        text-align: left;
        margin: 0.5em 0 0.5em 0;
        line-height: 1.5;
        page-break-after: avoid;
    }}
    h1.break-before {{
        page-break-before: always;
    }}
    p {{
        font-family: 'TimesNewRoman', 'Liberation Serif', 'Times', 'Noto Serif CJK SC', 'SimSun', '宋体', serif;
        font-size: 12pt;
        line-height: 1.5;
        margin: 0 0 0.5em 0;
        text-align: left;
        white-space: pre-wrap;
        word-break: break-word;
    }}
</style>
</head>
<body>
<div class="doc-title">论文审查报告</div>
{content_html}
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

    elements = parse_elements(report_text)
    html = build_html(elements)

    pdf_bytes = html_to_pdf_bytes(html)
    pdf_dir = Path("PDF")
    pdf_dir.mkdir(exist_ok=True)
    pdf_path = pdf_dir / f"{student_id}.pdf"
    pdf_path.write_bytes(pdf_bytes)
    print(f"PDF saved to {pdf_path}")

if __name__ == '__main__':
    main()
