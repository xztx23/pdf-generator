本工作流用于扣子 (Coze) 工作流通过 HTTP POST 接口向 GitHub Actions 推送学生学号 + 论文审查报告原文，由云端 Python 脚本基于 ReportLab 生成标准 A4 版式 PDF 文档：
排版规范：文档标题【论文审查报告】三号黑体居中；一 / 二 / 三、一级标题四号黑体左对齐；剩余正文小四号黑体左对齐；错别字、病句检查、专业性检查三大部分各自分页另起新页；
文件命名规则：生成 PDF 以传入参数student_id(学号)作为文件名，格式：{学号}.pdf；
流转链路：扣子入参→GitHub repository_dispatch 触发 CI 任务→预装中文字体与 Python 运行环境→落地存储入参文本与学号→自动排版导出 PDF→制品打包为 Artifact，后续可通过 Github API 拉取二进制 PDF 文件回传给扣子工作流供预览、下载。
