# v1.2.0 快速开始指南

> 5 分钟跑通 Discover → KB 联动 → RAG 问答全流程

---

## 前置条件

```bash
# 确认依赖
pip install chromadb sentence-transformers pdfplumber beautifulsoup4 requests edge-tts

# 确认 tvly CLI
tvly --version  # 如未安装: curl -fsSL https://cli.tavily.com/install.sh | bash && tvly login
```

---

## Step 1：搜索 & 导入（1 分钟）

在 pi-web 聊天框输入：

```
I want to learn about machine learning
```

返回 5 条结果后，导入前两条：

```
Import 1, 2
```

---

## Step 2：验证双目录同步（30 秒）

```bash
# Notebook 工作目录
ls ~/pi-cwd-20260526/notebooklm_data/sources/default/
# 应有 2 个 HTML 文件

# KB inbox（自动同步）
ls "C:/Users/mec/Desktop/claode code test/karpathy-kb/0-raw/inbox/"
# 应有 2 个 HTML + 2 个 .meta.json
```

> **新增**：pipeline 自动把导入源复制到 KB inbox 并生成 `.meta.json` 元数据。

---

## Step 3：Wiki 回写 Notebook（30 秒）

```bash
python "C:/Users/mec/Desktop/claode code test/karpathy-kb/scripts/sync_wiki_to_notebook.py" default
```

输出：
```
Synced: index.md -> kb_index.txt
Synced: concepts/arch-check.md -> kb_concepts_arch-check.txt
...
Synced 10 wiki files to notebook
```

```bash
ls ~/pi-cwd-20260526/notebooklm_data/sources/default/kb_*.txt | wc -l
# 应输出: 10
```

> **新增**：Wiki 内容一键同步为 Notebook 可检索的 txt 源。

---

## Step 4：RAG 问答（1 分钟）

上传 kb_*.txt 到 Notebook 后，在 pi-web 提问：

```
什么是架构检查？
```

预期回答引用格式：
```
架构检查（ARCH-CHECK）是 /ht-pm plan 时自动触发的评估机制...
(kb_concepts_arch-check.txt, chunk X)
```

---

## 数据流总览

```
Discover → Import 1,2
              ├── sources/default/*.html    (Notebook)
              └── inbox/*.html + .meta.json (KB)

Sync wiki → Notebook
              └── sources/default/kb_*.txt  (10 files)

kb_*.txt → embed → ChromaDB → RAG 问答
```

---

## 常见问题

**Q: KB 路径不对？**
确认 `C:/Users/mec/Desktop/claode code test/karpathy-kb/` 存在。如需修改，编辑 `download_source.py` 第 14 行 `KB_DIR`。

**Q: sync_wiki_to_notebook 报 "Wiki index not found"？**
先运行 `build_rag_index.py` 生成索引：
```bash
python "C:/Users/mec/Desktop/claode code test/karpathy-kb/scripts/build_rag_index.py"
```

**Q: RAG 回答精度不够？**
调整 `embed_store.py` 的 `threshold` 参数（默认 1.85）。
