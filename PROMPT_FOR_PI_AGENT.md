# PROMPT FOR PI-AGENT: NotebookLM Agent 部署与测试

你是 pi-agent，负责完成 NotebookLM Agent 项目的最后部署和测试。

## 项目背景
- 开发者已完成基础设施：8个Python脚本 + 3个Skill文件 + 依赖安装
- 工作目录：`~/pi-cwd-20260526/notebooklm_data/`
- Skills 目录：`C:\Users\mec\.pi\agent\skills\`

## 你的任务

### 任务 1：验证 Skill 加载（5 min）
1. 打开 pi-web Skills 面板
2. 确认能看到：notebooklm-core、notebooklm-podcast、notebooklm-studio
3. 如果看不到，检查 SKILL.md 的 YAML frontmatter 格式

### 任务 2：安装 ffmpeg（如果 winget 已下完）
```powershell
ffmpeg -version
```

如果失败，尝试：
```powershell
winget install ffmpeg --accept-source-agreements --accept-package-agreements
```

如果还是慢，先跳过，用分段音频方案测试播客。

### 任务 3：端到端测试（30 min）

按这个顺序执行，每步验证：

**Step 1: 创建 Notebook**
用户说："Create a notebook called AI Research"
验证：notebooks.json 中出现新 notebook

**Step 2: 上传 PDF**
拖放一个 PDF 到聊天框，或提供文件路径
验证：返回 "Added {title} ({filename}), X pages, Y chunks"
验证：chroma_db/ 目录有数据生成

**Step 3: RAG 问答**
问："What is the main contribution?"
验证：回答包含 `(filename.pdf, page X)` 格式引用

问："What is the weather today?"
验证：回答 "No relevant sources in current notebook"

**Step 4: 播客生成**
说："Generate a podcast"
验证：返回 MP3 文件路径（或分段音频列表）
验证：文件可播放

**Step 5: Studio 工具**
说："Generate mindmap"
验证：返回 Mermaid 代码，语法正确

说："Generate flashcards"
验证：返回 10 张 Q&A 格式

说："Generate report"
验证：返回 Markdown，带引用

### 任务 4：报告结果

测试完成后，更新 project_state.md：
- 哪些通过了 ✅
- 哪些失败了 ❌（附错误信息）
- 哪些跳过了 ⏭️（附原因）

## 约束

- 只修改 `~/pi-cwd-20260526/notebooklm_data/` 和 `C:\Users\mec\.pi\agent\skills\`
- 不修改 pi-web 核心
- 遇到报错立刻停住，把完整错误贴出来
- 不要顺手重构无关代码

## 成功标准

- [ ] PDF 上传 + 解析 < 30s
- [ ] 引用格式严格：`(filename.pdf, page 3)`
- [ ] 无关问题被拒绝
- [ ] 播客 MP3 可播放（或分段音频可播放）
- [ ] 思维导图 Mermaid 语法正确

## 每5分钟检测 ffmpeg

使用 /loop 技能每5分钟检查一次 ffmpeg 下载进度：
```
/loop 5m 检查 ffmpeg 安装状态
```

开始执行任务 1。