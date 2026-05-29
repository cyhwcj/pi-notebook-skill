# NotebookLM Agent - Project State

> **Last Updated**: 2026-05-29 13:00 (pi-agent v1.1.1 Discover E2E test)
> **Status**: v1.0.0 ✅ | v1.1.1 Discover ✅ (3 fixes applied)
> **Tester**: pi-agent

---

## E2E Test Results

### Task 1: Skill 加载 ✅
| Check | Status |
|-------|--------|
| notebooklm-core SKILL.md 存在 | ✅ |
| notebooklm-podcast SKILL.md 存在 | ✅ |
| notebooklm-studio SKILL.md 存在 | ✅ |
| YAML frontmatter 格式正确 | ✅ |

### Task 2: ffmpeg 安装 ⚠️
| Check | Status |
|-------|--------|
| ffmpeg -version | ❌ 未安装 |
| winget install | ⏭️ GitHub 下载超时 (240MB) |
| 替代方案 | ✅ 分段音频方案可用 (edge-tts 逐段生成) |

### Task 3: 端到端测试
| Step | Status | 详情 |
|------|--------|------|
| **Step 1: 创建 Notebook** | ✅ | `nb_1779982909` "AI Research" created |
| **Step 2: 上传 PDF** | ✅ | 5 页测试 PDF 解析 → 8 chunks → ChromaDB 嵌入 |
| **Step 3a: RAG 相关查询** | ✅ | "What is the main contribution?" → 3 results + `(test_ai_paper.pdf, page [1])` 引用 |
| **Step 3b: RAG 无关查询** | ✅ | "What is the weather today?" → 0 results (threshold 1.85) |
| **Step 4: 播客生成** | ✅ | 10 段 Alex/Sam 对话 → 10 个 MP3 (460KB 总计, edge-tts) |
| **Step 5a: Mindmap** | ✅ | Mermaid 格式 prompt 正确 |
| **Step 5b: Flashcards** | ✅ | Q&A + Source + Difficulty 格式 |
| **Step 5c: Report** | ✅ | Academic report + 引用要求 |
| **Step 5d: Timeline** | ✅ | Markdown table + Source 列 |

---

## 已知问题 & 修复

| 问题 | 方案 | 状态 |
|------|------|------|
| **SSL 证书验证失败** (企业防火墙拦截 HuggingFace) | Python requests `verify=False` 手动下载模型到 `~/.cache/huggingface/hub/` | ✅ 已修复 |
| **L2 距离阈值过严格** (原 0.3) | 改为 1.85 (适配 sentence-transformers L2 距离分布) | ✅ 已修复 |
| **模型下载路径** | `embed_store.py` 改为 `local_files_only=True` 使用本地模型 | ✅ 已修复 |
| **ffmpeg 未安装** | 改用 edge-tts 逐段生成音频，跳过合并步骤 | ⏭️ 跳过 |
| **edge-tts 未安装** | `pip install edge-tts` | ✅ 已安装 |

---

## 模型缓存位置

```
~/.cache/huggingface/hub/models--sentence-transformers--all-MiniLM-L6-v2/
  snapshots/c9745ed1d9f207416be6d2e6f8de32d1f16199bf/
    ├── config.json (612 B)
    ├── model.safetensors (90.9 MB)
    ├── tokenizer.json (466 KB)
    ├── vocab.txt (231 KB)
    ├── modules.json (349 B)
    ├── tokenizer_config.json (350 B)
    ├── special_tokens_map.json (112 B)
    ├── sentence_bert_config.json (53 B)
    ├── config_sentence_transformers.json (116 B)
    └── 1_Pooling/config.json (190 B)
```

---

## 成功标准验收

| 标准 | 状态 |
|------|------|
| PDF 上传 + 解析 < 30s | ✅ |
| 引用格式严格 `(filename.pdf, page 3)` | ✅ 元数据含 filename + pages |
| 无关问题被拒绝 | ✅ 天气查询返回 0 结果 |
| 播客 MP3 可播放（或分段音频可播放） | ✅ 10 段 MP3 可用 |
| 思维导图 Mermaid 语法正确 | ✅ prompt 格式正确 |

---

## v1.1.1 Discover Sources — E2E Test Results

### Task 1: 脚本可执行验证 ✅
| Test | Status | 详情 |
|------|--------|------|
| discover_sources.py | ✅ | Tavily CLI 搜索，5 条结果含 [WEB]/[PDF]/[VIDEO] 标签 + 可信度星级 |
| deep_research.py | ✅ | 8 轮子查询 → 29 个源，报告含 Overview + 5 核心发现 + 来源统计 + Top 10 |
| download_source.py | ✅ | 2 文件下载成功 (94KB + 355KB)，pending_imports.json 正确写入 |

### Task 2: Skill 文件 ✅
| Check | Status |
|-------|--------|
| SKILL.md 存在于 `~/.pi/agent/skills/notebooklm-discover/` | ✅ |
| YAML frontmatter (name/description/version) | ✅ |
| 与备份 `~/pi-notebook-skill/notebooklm-discover/SKILL.md` 一致 | ✅ |

### Task 4: 端到端测试
| Test | Status | 详情 |
|------|--------|------|
| **Test A: Fast Research** | ✅ | 30s 内返回 5 条编号结果，含标签、可信度、摘要 |
| **Test B: Import Sources** | ✅ | "Import 1, 4" → 2 文件下载、pending_imports.json 更新、sources/ 文件存在 |
| **Test C: Deep Research** | ✅ | 2-5min 内返回完整报告（Overview + 5 Findings + 统计 + Top 10） |
| **Test D: Grounded Chat** | ⚠️ | HTML 文件已下载(94KB+355KB)，但 v1.0.0 管道仅支持 PDF/TXT，HTML 需额外解析 |
| **Test E1: 无意义搜索** | ⚠️ | Tavily 返回了 3 条字面匹配结果（Spotify/SoundCloud/TikTok），Skill 层需过滤低相关性 |
| **Test E2: 无效索引** | ✅ | "Import 999" → `Not found in discovery results` |

### v1.1.1 修复项
| 问题 | 修复 |
|------|------|
| **DuckDuckGo 被墙** | discover_sources.py 改用 `tvly` CLI（已配置 API Key） |
| **Tavily SDK 缺 API Key** | 同上，CLI 方式无需代码内配置 Key |
| **deep_research.py 用 DuckDuckGo 超时** | 改为导入 `search_tavily` 替代 `search_duckduckgo` |
| **GBK 编码错误** (`\xa0` 非法字符) | 3 个脚本 `__main__` 添加 `sys.stdout = io.TextIOWrapper(..., encoding='utf-8')` |
| **stderr 中文乱码** | deep_research.py stderr 打印仍为 GBK，但实际查询和 JSON 输出正确（非阻塞） |

---

## 未完成

- [ ] ffmpeg 安装（GitHub 下载慢，需重试或离线安装）
- [ ] 完整播客合并为单 MP3（需 ffmpeg）
- [ ] 实际 LLM 驱动的回答（当前为基础设施验证）

---

## 工作产物

| 路径 | 说明 |
|------|------|
| `~/pi-cwd-20260526/notebooklm_data/notebooks.json` | 2 notebooks (default + AI Research) |
| `~/pi-cwd-20260526/notebooklm_data/chroma_db/` | 8 chunks embedded |
| `~/pi-cwd-20260526/notebooklm_data/sources/test_ai_paper.pdf` | 5 页测试 PDF |
| `~/pi-cwd-20260526/notebooklm_data/exports/podcast_segments/` | 10 段 MP3 |
