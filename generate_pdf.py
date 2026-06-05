import sys
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

def clean_line(line: str) -> str:
    """清理行：移除不可见字符、首尾空格，合并多余空格"""
    line = re.sub(r'[\u200b\u200c\u200d\u2060\uFEFF]', '', line)
    line = line.strip()
    line = re.sub(r'[ \t]+', ' ', line)
    return line

def is_junk_number_line(line: str) -> bool:
    """判断是否为纯数字序列（如'1. 2. 3. ...'或'1 2 3 4'）"""
    stripped = line.strip()
    # 匹配形如 "1. 2. 3." 或 "1.2.3."
    if re.fullmatch(r'(\d+\.\s*)+', stripped):
        return True
    # 匹配形如 "1 2 3 4 5"
    if re.fullmatch(r'(\d+\s+)+', stripped):
        return True
    # 如果超过20个数字且总长度大于100，视为垃圾
    numbers = re.findall(r'\d+', stripped)
    if len(numbers) > 20 and len(stripped) > 100:
        return True
    return False

def parse_to_elements(text: str):
    """
    解析原始文本，返回元素列表：
    每个元素为 (type, content)
    type: 'title'  (只生成一次，忽略输入中的标题行)
          'h1'     (一级标题)
          'p'      (普通段落)
    """
    lines = text.splitlines()
    elements = []
    seen_h1 = False
    for raw_line in lines:
        line = clean_line(raw_line)
        if not line:
            continue
        # 跳过单独的“论文审查报告”行（避免重复）
        if line == "论文审查报告":
            continue
        # 跳过垃圾数字行
        if is_junk_number_line(line):
            continue

        # 处理一级标题：移除可能的 Markdown 标记（##、#）
        h1_match = re.match(r'^#*\s*([一二三]、.*)$', line)
        if h1_match:
            h1_text = h1_match.group(1)
            # 再次确认不是“论文审查报告”
            if h1_text == "论文审查报告":
                continue
            elements.append(('h1', h1_text))
            seen_h1 = True
        elif line.startswith(('一、', '二、', '三、')):
            elements.append(('h1', line))
            seen_h1 = True
        else:
            # 普通正文（保留原样，包括“·”符号）
            elements.append(('p', line))
    return elements

def build_html(elements):
    """根据元素列表生成完整的 HTML 字符串"""
    html_parts = []
    for idx, (typ, content) in enumerate(elements):
        if typ == 'h1':
            # 第一个一级标题前不加分页，第二个及之后加
            if idx > 0 and any(e[0]=='h1' for e in elements[:idx]):
                html_parts.append(f'<h1 class="break-before">{content}</h1>')
            else:
                html_parts.append(f'<h1>{content}</h1>')
        else:  # p
            # 保留原文中的空格与换行感，使用 white-space: pre-wrap
            html_parts.append(f'<p>{content}</p>')
    content_html = '\n'.join(html_parts)

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
        font-size: 16pt;      /* 三号 */
        font-weight: bold;
        text-align: center;
        margin: 1em 0 1em 0;  /* 段前段后1行 */
        line-height: 1.5;
    }}
    h1 {{
        font-family: "SimHei", "黑体", "Microsoft YaHei", sans-serif;
        font-size: 14pt;      /* 四号 */
        font-weight: bold;
        text-align: left;
        margin: 0.5em 0 0.5em 0;  /* 段前段后0.5行 */
        line-height: 1.5;
        page-break-after: avoid;
    }}
    h1.break-before {{
        page-break-before: always;
    }}
    p {{
        font-family: "Times New Roman", "SimSun", "宋体", serif;
        font-size: 12pt;      /* 小四 */
        line-height: 1.5;
        margin: 0 0 0.5em 0;
        text-align: left;
        white-space: pre-wrap;  /* 保留原文中的空格和缩进 */
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

    # 解析并生成HTML
    elements = parse_to_elements(report_text)
    html = build_html(elements)

    # 调试：保存HTML文件（可选，用于检查）
    # Path("debug.html").write_text(html, encoding='utf-8')

    pdf_bytes = html_to_pdf_bytes(html)
    pdf_dir = Path("PDF")
    pdf_dir.mkdir(exist_ok=True)
    pdf_path = pdf_dir / f"{student_id}.pdf"
    pdf_path.write_bytes(pdf_bytes)
    print(f"PDF saved to {pdf_path}")

if __name__ == '__main__':
    main()
