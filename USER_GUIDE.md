# NotebookLM Agent — 用户手册

> **版本**：1.0.0  
> **更新日期**：2026-05-28  
> **适用环境**：pi-web (Windows)

---

## 目录

1. [快速开始（3 分钟上手）](#1-快速开始3-分钟上手)
2. [常用命令清单](#2-常用命令清单)
3. [已知限制 & Workaround](#3-已知限制--workaround)
4. [故障排查](#4-故障排查)

---

## 1. 快速开始（3 分钟上手）

### 1.1 准备工作（一次性）

确保 Python 依赖已安装：

```bash
pip install chromadb sentence-transformers pdfplumber beautifulsoup4 requests edge-tts
```

验证：

```bash
python -c "import chromadb, sentence_transformers, pdfplumber, bs4, edge_tts; print('OK')"
```

> 如果输出 `OK`，说明环境就绪。如果报 `ModuleNotFoundError`，重新运行 `pip install` 命令。

### 1.2 创建你的第一个 Notebook

在 pi-web 聊天框中输入：

```
Create a notebook called "AI Research"
```

系统会创建一个新 Notebook 并自动切换为当前活动 Notebook。

### 1.3 上传一篇 PDF

拖拽 PDF 文件到 pi-web 聊天框，或输入文件路径：

```
Add source: C:\Users\mec\Documents\paper.pdf
```

系统会自动：
1. 提取文本（保留页码）
2. 分块（每块约 450 字，重叠 50 字）
3. 生成嵌入向量并存入 ChromaDB

返回类似：
```
Added "Attention Is All You Need" (paper.pdf), 5 pages, 8 chunks
```

### 1.4 开始提问

```
What is the main contribution of this paper?
```

回答会附带引用，例如：
```
...the Transformer architecture based solely on attention mechanisms...
(paper.pdf, page 1)
```

### 1.5 生成思维导图

```
Generate mindmap
```

返回 Mermaid 格式的思维导图代码。

---

## 2. 常用命令清单

### 2.1 Notebook 管理（notebooklm-core）

| 自然语言命令 | 功能 |
|-------------|------|
| `Create a notebook called "XXX"` | 创建新 Notebook |
| `Switch to notebook "XXX"` | 切换活动 Notebook |
| `List notebooks` | 列出所有 Notebook |
| `Add source: <path>` | 上传文件并解析 |
| `Upload file` + 拖放文件 | 同上 |

### 2.2 RAG 问答（notebooklm-core）

| 命令示例 | 功能 |
|---------|------|
| `What is the main contribution?` | 基于当前 Notebook 检索回答 |
| `Summarize this` | 总结当前源材料 |
| `Explain this section` | 解释某个段落 |
| `according to the paper...` | 明确基于文档的回答 |

> **注意**：所有回答 **必须** 附带 `(文件名.pdf, page X)` 格式的引用。  
> 如果问题与当前 Notebook 无关，系统会回复：  
> `No relevant sources in current notebook`

### 2.3 播客生成（notebooklm-podcast）

| 命令 | 参数 | 默认值 |
|------|------|--------|
| `Generate podcast` | focus, duration, style | medium / casual |
| `Audio overview` | 同上 | 同上 |
| `Make podcast about <topic>` | focus=指定话题 | — |
| `I want to listen to this` | 同上 | 同上 |

**参数说明**：

| 参数 | 可选值 | 说明 |
|------|--------|------|
| duration | `short` / `medium` / `long` | ~800 / 2000 / 4000 词 |
| style | `casual` / `academic` / `storytelling` | 风格 |
| focus | 任意文本 | 聚焦话题（默认全部内容） |

**播客形式**：
- 🎙️ **Alex**（男声，en-US-ChristopherNeural）
- 🎙️ **Sam**（女声，en-US-JennyNeural）
- 双人对话，允许观点分歧
- 自然口语元素（"um", "you know", 笑声）

### 2.4 Studio 工具（notebooklm-studio）

| 命令 | 输出格式 | 说明 |
|------|----------|------|
| `Generate mindmap` | Mermaid 代码 (`.mmd`) | 三层思维导图 |
| `Generate flashcards` | Markdown Q&A (`.md`) | 10 张闪卡，含难度评级 |
| `Generate report` | Markdown 报告 (`.md`) | 1500-2000 词学术报告 |
| `Generate timeline` | Markdown 表格 (`.md`) | 时间线，含来源列 |

---

## 3. 已知限制 & Workaround

### 3.1 ffmpeg 未安装（播客合并）

**限制**：ffmpeg 用于合并多段对话音频为单个 MP3。winget 安装从 GitHub 下载约 240MB，可能因网络问题超时。

**Workaround**：
- 系统会自动退化为 **分段音频** 输出：每条对话生成一个独立 MP3 文件
- 文件位于 `~/pi-cwd-20260526/notebooklm_data/exports/podcast_segments/`
- 按顺序播放即可（文件名 `alex_0000.mp3`, `sam_0001.mp3`, ...）
- 后续可手动安装 ffmpeg 后运行 `python scripts/merge_audio.py exports/podcast_segments/` 合并

**手动安装 ffmpeg**：
```powershell
winget install ffmpeg --accept-source-agreements --accept-package-agreements
```
或从 [ffmpeg.org](https://ffmpeg.org/download.html) 下载 Windows 版本，将 `bin/` 加入 PATH。

### 3.2 SSL 证书 / 企业防火墙

**限制**：企业网络可能拦截 HTTPS 请求（如 HuggingFace），导致 sentence-transformers 模型下载失败。

**Workaround**：
- 模型已预下载到本地缓存：  
  `~/.cache/huggingface/hub/models--sentence-transformers--all-MiniLM-L6-v2/`
- `embed_store.py` 使用 `local_files_only=True` 加载，**不需要联网**
- 如果换机器部署，用 Python 脚本下载模型：
  ```python
  import requests, os
  # ... (参考 project_state.md 中的下载脚本)
  ```
- 如需更新模型，联系管理员获取完整的 cache 目录副本

### 3.3 检索阈值

**限制**：当前使用 L2 距离度量，阈值设为 **1.85**。这可能导致：
- 非常简短的查询偶尔漏掉相关结果
- 非常通用的词语（"is", "the"）可能导致无关结果勉强通过

**Workaround**：
- 提问时尽量使用 **具体术语** 而非泛泛而谈
- 如果收到 `No relevant sources` 但确定文档中有答案，换一种措辞重新提问
- 高级用户可调整 `embed_store.py` 第 21 行的 `threshold` 参数

### 3.4 播客语言

**限制**：skill 默认检测源语言，但 edge-tts 语音包覆盖有限。

**Workaround**：
- 英文内容：使用 `en-US-ChristopherNeural` (Alex) + `en-US-JennyNeural` (Sam)
- 中文内容：使用 `zh-CN-YunjianNeural` (Alex) + `zh-CN-XiaoxiaoNeural` (Sam)
- 其他语言：运行 `edge-tts --list-voices` 查看可用语音，手动指定

### 3.5 大文件处理

**限制**：单个 PDF 超过 100 页时，嵌入和检索可能变慢。

**Workaround**：
- 大文件分拆为多个小 PDF 分别上传
- 使用 `duration: short` 参数生成摘要版播客
- 生成 mindmap 时 LLM 会自动聚焦核心概念

---

## 4. 故障排查

### 4.1 `ModuleNotFoundError: No module named 'chromadb'`

**原因**：Python 依赖未安装。

**解决**：
```bash
pip install chromadb sentence-transformers pdfplumber beautifulsoup4 requests edge-tts
```

### 4.2 上传 PDF 后提示"0 chunks"

**原因**：PDF 可能为扫描件（图片 PDF），文本无法提取。

**解决**：
- 确认 PDF 包含可选择的文字（用 Acrobat 打开检查）
- 扫描件需先用 OCR 工具预处理
- 尝试用 `.txt` 格式上传纯文本

### 4.3 `No relevant sources in current notebook`

**可能原因**：
1. 当前 Notebook 没有添加任何 Source
2. 问题与文档内容确实不相关
3. 检索阈值过滤掉了结果

**排查步骤**：
1. 说 `List notebooks` 确认当前 Notebook
2. 说 `What sources do I have?` 查看已上传文件
3. 换用文档中的原句提问测试
4. 如仍失败，用更具体的术语重新提问

### 4.4 播客生成后无声音

**可能原因**：
1. edge-tts 语音包下载失败（首次使用需联网）
2. ffmpeg 合并失败但未报错

**排查步骤**：
1. 检查 `exports/podcast_segments/` 是否有 `.mp3` 文件
2. 如果文件存在但无法播放，尝试用 VLC 或 Windows Media Player 打开
3. 如果文件不存在，手动测试 edge-tts：
   ```bash
   python -m edge_tts --text "Hello world" --write-media test.mp3
   ```

### 4.5 `[SSL: CERTIFICATE_VERIFY_FAILED]`

**原因**：企业 SSL 证书拦截（仅影响模型首次下载）。

**解决**：
- 模型已预下载到本地缓存，**不影响正常使用**
- 如果是全新部署且没有 cache，参考 [3.2 节](#32-ssl-证书--企业防火墙) 手动下载

### 4.6 思维导图无法渲染

**可能原因**：Mermaid 代码有语法错误（LLM 生成不完美）。

**解决**：
- 要求重新生成：`Regenerate mindmap`
- 手动修正常见错误：
  - 节点名过长（应 2-6 字符）
  - 层级超过 3 层
  - 缩进不一致（必须用 2 空格缩进）
- 将代码粘贴到 [Mermaid Live Editor](https://mermaid.live/) 检查语法

---

## 附录

### 文件结构速查

```
~/pi-cwd-20260526/notebooklm_data/
├── notebooks.json          ← Notebook 元数据
├── sources/                ← 原始上传文件
├── chroma_db/              ← 向量数据库（ChromaDB）
├── exports/                ← 生成产物（播客/报告等）
│   ├── podcast_segments/   ← 分段播客 MP3
│   └── *.mmd, *.md         ← Studio 输出
└── scripts/                ← Python 工具脚本（8个）
```

### Skills 位置

| Skill | 路径 |
|-------|------|
| notebooklm-core | `C:\Users\mec\.pi\agent\skills\notebooklm-core\SKILL.md` |
| notebooklm-podcast | `C:\Users\mec\.pi\agent\skills\notebooklm-podcast\SKILL.md` |
| notebooklm-studio | `C:\Users\mec\.pi\agent\skills\notebooklm-studio\SKILL.md` |

### 参考文档

| 文档 | 路径 |
|------|------|
| 项目进度 | `~/pi-notebook-skill/PROGRESS.md` |
| 项目状态 | `~/pi-notebook-skill/project_state.md` |
| 架构设计 | `~/pi-notebook-skill/arch.md` |
| 产品需求 | `~/pi-notebook-skill/prd.md` |

---

> 💡 **提示**：遇到任何未列出的问题，把完整错误信息贴到 pi-web 聊天框，pi-agent 会协助排查。
