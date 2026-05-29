# NotebookLM Agent

> 运行在 **pi-agent** 中的本地 NotebookLM 风格研究助手 —— 上传 PDF，提问带引用，一键生成播客、思维导图、闪卡和报告。

[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-brightgreen)]()
[![Version](https://img.shields.io/badge/version-v1.2.0-blue)]()
[![pi-agent](https://img.shields.io/badge/runs%20on-pi--agent-purple)]()

---

## ✨ 功能

| 模块 | 能力 | 版本 |
|------|------|------|
| 🔍 **Discover** | Fast / Deep Research + **KB 双向联动**：导入源自动同步到知识库 inbox，wiki 一键回写 Notebook | 🆕 v1.2.0 |
| 📚 **Core** | 上传 PDF → 自动分块嵌入 → RAG 问答，所有回答附带 `(文件名.pdf, page X)` 引用 | v1.0.0 |
| 🎙️ **Podcast** | Alex & Sam 双人对话播客，edge-tts 生成音频，支持 short/medium/long 三档时长 | v1.0.0 |
| 🧠 **Studio** | 一键生成：思维导图 (Mermaid)、闪卡 (Q&A)、学术报告、时间线 | v1.0.0 |

---

## 🚀 3 分钟上手

```bash
# 1. 安装依赖
pip install chromadb sentence-transformers pdfplumber beautifulsoup4 requests edge-tts

# 2. 在 pi-web 聊天框中：
Create a notebook called "AI Research"
Add source: /path/to/paper.pdf

# 3. 开始提问
What is the main contribution?

# 4. 生成内容
Generate mindmap
Generate podcast
Generate flashcards
```

---

## 🏗️ 架构

```
pi-notebook-skill/
├── notebooklm-core/SKILL.md       ← 源管理 + RAG 问答
├── notebooklm-discover/SKILL.md   ← 🆕 Fast/Deep Research 搜索
├── notebooklm-podcast/SKILL.md    ← Alex/Sam 双人播客
├── notebooklm-studio/SKILL.md     ← 思维导图/闪卡/报告/时间线
├── scripts/                       ← 11 个 Python 工具脚本
│   ├── discover_sources.py        # 🆕 Fast Research (Tavily CLI)
│   ├── deep_research.py           # 🆕 Deep Research 多轮搜索+报告
│   ├── download_source.py         # 🆕 下载源 → pending_imports.json
│   ├── parse_pdf.py               # PDF 文本提取（保留页码）
│   ├── chunk_text.py              # 450字/块 + 50字重叠
│   ├── embed_store.py             # ChromaDB 向量存储 & 检索
│   ├── notebook_manager.py        # Notebook CRUD
│   ├── generate_podcast_script.py # 播客 LLM prompt 生成
│   ├── parse_dialogue.py          # Alex/Sam 对话解析
│   ├── merge_audio.py             # ffmpeg 音频合并
│   └── studio_generator.py        # 思维导图/闪卡/报告 prompt
└── docs/
    ├── prd.md                     # 产品需求
    ├── arch.md                    # 架构设计
    ├── USER_GUIDE.md              # 用户手册（中文）
    └── project_state.md           # E2E 测试结果
```

### 数据流

```
🔍 Discover → tvly CLI → Fast Research / Deep Research
              ↓ 用户确认
  download_source → sources/ + pending_imports.json
              ↓                       ↓
    NotebookLM sources/      KB inbox/ + .meta.json 🆕
              ↓                       ↓
           embed_store          karpathy-kb wiki
              ↓                       ↓
         RAG 问答 ←──────── sync_wiki_to_notebook 🆕
              ↓
源材料 → studio_generator → LLM → 思维导图/闪卡/报告
       → generate_podcast_script → parse_dialogue → edge-tts → MP3
```

---

## 🛠️ 技术栈

| 组件 | 用途 |
|------|------|
| **ChromaDB** | 向量数据库，存储文本嵌入 |
| **sentence-transformers** | `all-MiniLM-L6-v2` 模型，384 维嵌入 |
| **pdfplumber** | PDF 文本提取（支持页码保留） |
| **edge-tts** | 微软 Edge TTS，生成自然语音 |
| **Tavily CLI** | 🆕 Web 搜索（Fast + Deep Research），替代码内 API Key |
| **karpathy-kb** | 🆕 v1.2.0 知识库联动：inbox 同步 + wiki 回写 |
| **BeautifulSoup4** | HTML → TXT 文本提取（Discover 导入 workaround） |
| **ffmpeg** | 合并多段播客音频（可选） |

---

## 📋 常见命令

```
# Discover 🆕
I want to learn about <topic>
Deep research <topic>
Import 1, 3, 5
Sync wiki to notebook       # 🆕 v1.2.0
Ingest inbox                # 🆕 v1.2.0

# Notebook
Create a notebook called "XXX"
Switch to notebook "XXX"

# 问答
What is the main contribution?
Summarize this
based on my sources...

# 播客
Generate podcast
Make podcast about <topic>

# Studio
Generate mindmap
Generate flashcards
Generate report
Generate timeline
```

---

## ⚠️ 已知限制

| 问题 | Workaround | v1.2.0 计划 |
|------|------------|------------|
| ffmpeg 未安装 | 分段 MP3 逐个播放，或手动 `winget install ffmpeg` | 内置分段播放器 |
| 企业 SSL 拦截 HuggingFace | 模型已预下载到本地 cache，无需联网 | — |
| 大量页 PDF 较慢 | 拆分为小文件上传 | 流式分块 |
| HTML 源需手动转换 🆕 | BS4 提取文本 → 存 `.txt` → 导入 | 原生 HTML parsing 到 Core 管道 |
| 单词语境过滤弱 🆕 | 多词查询效果良好；全滤掉时 fallback 保底 | 语义相关性评分 |
| KB 路径硬编码 🆕 | 当前 KB 路径为固定 Windows 绝对路径 | 可配置 KB_DIR 环境变量 |

详见 [USER_GUIDE.md](USER_GUIDE.md)

---

## 📄 License

MIT
