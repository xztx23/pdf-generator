from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# 读取参数
with open("student_id.txt", "r", encoding="utf-8") as f:
    student_id = f.read().strip()
with open("content.txt", "r", encoding="utf-8") as f:
    content = f.read()

pdf_filename = f"{student_id}.pdf"
doc = SimpleDocTemplate(pdf_filename, pagesize=A4,
                        topMargin=40, bottomMargin=40, leftMargin=45, rightMargin=45)
story = []

# 关键修复：手动注册文泉驿正黑字体
FONT_NAME = "WenQuanYiZenHei"
try:
    pdfmetrics.registerFont(TTFont(FONT_NAME, "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"))
except:
    # 注册失败 fallback 用默认字体
    FONT_NAME = "Helvetica"

# 样式定义
title_style = ParagraphStyle(
    "title", fontName=FONT_NAME, fontSize=16, alignment=1, spaceAfter=24
)
h1_style = ParagraphStyle(
    "h1", fontName=FONT_NAME, fontSize=14, alignment=0, spaceBefore=16, spaceAfter=10
)
text_style = ParagraphStyle(
    "text", fontName=FONT_NAME, fontSize=12, alignment=0, spaceAfter=6, leading=16
)

# 文档内容拆分
lines = content.splitlines()
if lines:
    story.append(Paragraph(lines[0], title_style))
    body = "\n".join(lines[1:])

parts = [
    "一、错别字检查结果",
    "二、病句检查结果",
    "三、专业性检查结果"
]
current = body

for i, part in enumerate(parts):
    if i > 0:
        story.append(PageBreak())
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

doc.build(story)
print(f"PDF 生成完成：{pdf_filename}")
