import sys
import json
import base64
import requests
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
body {{ font-family: "SimHei", "Microsoft YaHei", "黑体", sans-serif; margin:0; line-height:1.5; }}
.doc-title {{ font-size: 16pt; font-weight: bold; text-align: center; margin: 1cm 0 2cm 0; }}
h1 {{ font-size: 14pt; font-weight: bold; text-align: left; margin: 1.2em 0 0.8em 0; }}
h1.break-before {{ page-break-before: always; }}
p, li {{ font-size: 12pt; line-height: 1.5; margin: 0.5em 0; }}
.content {{ white-space: pre-wrap; }}
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

def upload_to_tmpfiles(pdf_bytes: bytes) -> str:
    """上传到 tmpfiles.org 并返回下载链接"""
    files = {'file': ('report.pdf', pdf_bytes, 'application/pdf')}
    r = requests.post('https://tmpfiles.org/api/v1/upload', files=files)
    if r.status_code == 200:
        data = r.json()
        # 返回的 data['data']['url'] 是页面链接，实际文件链接需加 /dl/
        return data['data']['url'].replace('/v1/', '/dl/')
    else:
        raise Exception("Upload failed")

def main():
    student_id = sys.argv[1]
    report_text = sys.argv[2]
    html = generate_pdf_html(report_text)
    pdf_bytes = html_to_pdf_bytes(html)
    url = upload_to_tmpfiles(pdf_bytes)
    with open('pdf_url.txt', 'w') as f:
        f.write(url)
    print(f"PDF uploaded: {url}")

if __name__ == '__main__':
    main()
