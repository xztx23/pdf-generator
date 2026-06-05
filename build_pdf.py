from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak
from reportlab.lib import colors

# 读取学号（文件名用）
with open("student_id.txt", "r", encoding="utf-8") as f:
    student_id = f.read().strip()

# 读取报告文本
with open("content.txt", "r", encoding="utf-8") as f:
    content = f.read()

# PDF配置：A4、页边距
pdf_file = f"{student_id}.pdf"
doc = SimpleDocTemplate(pdf_file, pagesize=A4,
                        topMargin=40, bottomMargin=40, leftMargin=45, rightMargin=45)
story = []

# 字体配置（GitHub Ubuntu自带）
font_hei = "WenQuanYiZenHei"

# ------------------- 样式严格按你要求 -------------------
# 主标题：三号黑体、居中
title_style = ParagraphStyle(
    "title", fontName=font_hei, fontSize=16, alignment=1, spaceAfter=24
)
# 一级标题：四号黑体、左对齐
h1_style = ParagraphStyle(
    "h1", fontName=font_hei, fontSize=14, alignment=0, spaceBefore=16, spaceAfter=10
)
# 正文：小四号黑体、左对齐
text_style = ParagraphStyle(
    "text", fontName=font_hei, fontSize=12, alignment=0, spaceAfter=6, leading=16
)

# ------------------- 内容解析 + 分页 -------------------
lines = content.splitlines()
if lines:
    main_title = lines[0].strip()
    story.append(Paragraph(main_title, title_style))
    content_lines = lines[1:]

body_text = "\n".join(content_lines)

# 三大块强制分页
parts = [
    "一、错别字检查结果",
    "二、病句检查结果",
    "三、专业性检查结果"
]

current = body_text
for i, part in enumerate(parts):
    if i > 0:
        story.append(PageBreak())  # 每块另起一页
    if i < len(parts)-1:
        chunk = current.split(parts[i+1])[0]
        current = current.split(parts[i+1])[1]
    else:
        chunk = current

    for line in chunk.splitlines():
        line = line.strip()
        if not line:
            continue
        if line in parts:
            story.append(Paragraph(line, h1_style))
        else:
            story.append(Paragraph(line, text_style))

# 生成PDF
doc.build(story)
print(f"PDF生成成功：{pdf_file}")
