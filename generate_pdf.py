import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

def generate_pdf_html(report_text: str) -> str:
    """将报告文本包装为符合格式要求的 HTML"""
    lines = report_text.strip().splitlines()
    html_lines = []
    h1_flag = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            html_lines.append('<p class="empty-line"> </p>')
            continue
        # 判断是否为一级标题（以“一、”“二、”“三、”开头）
        if stripped.startswith(('一、', '二、', '三、')):
            if h1_flag:
                html_lines.append(f'<h1 class="break-before">{stripped}</h1>')
            else:
                html_lines.append(f'<h1>{stripped}</h1>')
                h1_flag = True
        else:
            # 普通正文段落，保留原文中的特殊符号和空格
            html_lines.append(f'<p>{stripped}</p>')
    content = '\n'.join(html_lines)
    
    return f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>论文审查报告</title>
<style>
    /* 页面全局设置：A4，页边距2cm，1.5倍行距 */
    @page {{
        size: A4;
        margin: 2cm;
    }}
    body {{
        font-family: "Times New Roman", "SimSun", "宋体", serif;
        font-size: 12pt;      /* 正文默认小四 ≈12pt */
        line-height: 1.5;
        margin: 0;
        padding: 0;
        background: white;
    }}
    /* 总标题：论文审查报告 */
    .doc-title {{
        font-family: "SimHei", "黑体", "Microsoft YaHei", sans-serif;
        font-size: 16pt;      /* 三号 */
        font-weight: bold;
        text-align: center;
        margin: 1em 0 1em 0;  /* 段前段后1行 */
        line-height: 1.5;
    }}
    /* 一级标题：一、二、三、 */
    h1 {{
        font-family: "SimHei", "黑体", "Microsoft YaHei", sans-serif;
        font-size: 14pt;      /* 四号 */
        font-weight: bold;
        text-align: left;
        margin: 0.5em 0 0.5em 0;  /* 段前段后0.5行 */
        line-height: 1.5;
        page-break-after: avoid;
    }}
    /* 需要分页的一级标题 */
    h1.break-before {{
        page-break-before: always;
    }}
    /* 普通正文段落 */
    p {{
        font-family: "Times New Roman", "SimSun", "宋体", serif;
        font-size: 12pt;
        line-height: 1.5;
        margin: 0 0 0.5em 0;
        text-align: left;
    }}
    /* 处理空行占位 */
    p.empty-line {{
        margin: 0;
        height: 0.5em;
    }}
    /* 保留原文本中的空白格式 */
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
    
    pdf_dir = Path("PDF")
    pdf_dir.mkdir(exist_ok=True)
    pdf_path = pdf_dir / f"{student_id}.pdf"
    pdf_path.write_bytes(pdf_bytes)
    print(f"PDF saved to {pdf_path}")

if __name__ == '__main__':
    main()
