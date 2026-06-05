import sys
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

def clean_text(text: str) -> str:
    """移除可能导致格式混乱的控制字符和多余空格"""
    # 移除零宽字符等不可见字符
    text = re.sub(r'[\u200b\u200c\u200d\u2060\uFEFF]', '', text)
    # 合并连续空格
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

def is_junk_number_line(line: str) -> bool:
    """判断是否为垃圾数字序列行（如'1. 2. 3. ...'或'1.2.3.'）"""
    stripped = line.strip()
    # 纯数字列表：1. 2. 3. 或 1. 2. 3.
    if re.match(r'^(\d+\.\s*)+$', stripped):
        return True
    # 连续数字加空格：1 2 3 4 ...
    if re.match(r'^(\d+\s+)+$', stripped):
        return True
    # 数字序列超过10个且无意义
    numbers = re.findall(r'\d+', stripped)
    if len(numbers) > 20 and len(stripped) > 100:
        return True
    return False

def generate_pdf_html(report_text: str) -> str:
    lines = report_text.splitlines()
    html_parts = []
    h1_count = 0

    for raw_line in lines:
        line = clean_text(raw_line)
        if not line:
            html_parts.append('<p class="empty-line"> </p>')
            continue

        # 跳过垃圾数字行
        if is_junk_number_line(line):
            continue

        # 跳过单独出现的“论文审查报告”（防止重复）
        if line == "论文审查报告" or line == "论文审查报告":
            continue

        # 处理一级标题：去掉可能的Markdown标记（##、#）和多余空格
        h1_match = re.match(r'^##?\s*([一二三]、.*)$', line)
        if h1_match:
            line = h1_match.group(1)  # 得到“一、错别字检查结果”
        elif line.startswith(('一、', '二、', '三、')):
            pass  # 保持原样
        else:
            # 普通正文行
            html_parts.append(f'<p>{line}</p>')
            continue

        # 至此，是一级标题
        h1_count += 1
        if h1_count == 1:
            html_parts.append(f'<h1>{line}</h1>')
        else:
            html_parts.append(f'<h1 class="break-before">{line}</h1>')

    content = '\n'.join(html_parts)

    return f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>论文审查报告</title>
<style>
    @page {{
        size: A4;
        margin: 2cm;
    }}
    body {{
        font-family: "Times New Roman", "SimSun", "宋体", serif;
        font-size: 12pt;
        line-height: 1.5;
        margin: 0;
        padding: 0;
        background: white;
    }}
    .doc-title {{
        font-family: "SimHei", "黑体", "Microsoft YaHei", sans-serif;
        font-size: 16pt;
        font-weight: bold;
        text-align: center;
        margin: 1em 0 1em 0;
        line-height: 1.5;
    }}
    h1 {{
        font-family: "SimHei", "黑体", "Microsoft YaHei", sans-serif;
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
        font-family: "Times New Roman", "SimSun", "宋体", serif;
        font-size: 12pt;
        line-height: 1.5;
        margin: 0 0 0.5em 0;
        text-align: left;
        white-space: pre-wrap;
    }}
    p.empty-line {{
        margin: 0;
        height: 0.5em;
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

    pdf_dir = Path("PDF")
    pdf_dir.mkdir(exist_ok=True)
    pdf_path = pdf_dir / f"{student_id}.pdf"
    pdf_path.write_bytes(pdf_bytes)
    print(f"PDF saved to {pdf_path}")

if __name__ == '__main__':
    main()
