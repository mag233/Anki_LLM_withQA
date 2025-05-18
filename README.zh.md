<!-- Logo -->
<p align="center">
  <img src="assets/logo.png" alt="ScholarPilot: AI Literature Review & Knowledge Pipeline Logo" width="220"/>
</p>

# 个人知识库与学习助手

[English version available in README.md](README.md)

---

## 关于本项目

你好！这是我的第一个编程项目。虽然我不是计算机专业出身，但我非常喜欢学习新技术，希望通过这个项目挑战自己，做出一些实用又有趣的东西。还在不断学习中，欢迎大家提出建议和意见！
<p align="center">
  <img src="assets/intro.png" alt="Project Introduction" width="400" height="400"/>
</p>
---

## 技术栈与学习收获

本项目是我动手实践以下技术的过程：

- **Python**：主要编程语言，负责后端逻辑和数据处理。
- **Streamlit**：快速搭建数据科学和机器学习交互式Web应用。
- **OpenAI API**：调用大语言模型进行文本生成、摘要和问答。
- **ChromaDB**：向量数据库，实现语义检索和RAG（检索增强生成）。
- **LangChain**：LLM链式调用与文档加载框架。
- **PyMuPDF, Unstructured 等**：文档解析与分块。
- **Anki 导出**：自动生成记忆卡片，辅助间隔复习。
- **Docker & Git**：基础的容器化和版本管理实践。

我在API集成、prompt工程、Python库组合等方面收获很大，代码风格和最佳实践还在持续改进中。

---

## 功能亮点

- **文档导入**：支持上传和处理PDF、Word、Excel、Markdown、HTML等文件。
- **灵活分块**：按句子、段落、页面或固定长度分块，适配不同下游任务。
- **语义检索（RAG）**：基于向量相似度检索相关文档片段。
- **文献综述与问答**：输入研究问题，获得带引用的总结性答案。
- **Anki卡片生成**：自动从知识库生成Q&A和完形填空卡片。
- **交互式仪表盘**：可视化项目状态、分块/向量数量和处理进度。
- **自定义模板**：可编辑摘要和卡片生成的prompt模板。
- **多语言界面**：支持中英文切换。

---

## 项目进度

| 里程碑                     | 状态           | 备注                              |
| -------------------------- | -------------- | --------------------------------- |
| 项目初始化                 | ✅ 已完成      | Streamlit骨架搭建                 |
| PDF导入与分块              | ✅ 已完成      | 支持多种分块方式                  |
| 向量数据库集成             | ✅ 已完成      | 集成Chroma DB                     |
| 检索问答模块               | 🔄 进行中      | 优化流式问答体验                  |
| Anki卡片导出               | 🔄 进行中      | 支持Q&A和完形填空格式             |
| 仪表盘与统计               | 🔲 待开发      | 设计可视化组件                    |
| 心愿单功能                 | 🔲 待开发      | 增加心愿单管理界面                |

---

## 后续计划

- [ ] 优化UI/UX，丰富仪表盘可视化。
- [ ] 支持更多文档类型和多语言。
- [ ] 增强引用和参考文献导出功能。
- [ ] 移动端适配或开发配套App。
- [ ] 云同步与多设备支持。
- [ ] 更丰富的学习进度分析。
- [ ] 重构代码，提升模块化和可维护性。

---

## 项目结构

```
anki_llm_withqa/
├── app.py               # Streamlit应用入口
├── anki/                # 卡片生成逻辑
├── embed/               # 向量与数据库相关
├── preprocess/          # 文档加载与分块
├── retrieve/            # 语义检索与RAG
├── dashboard/           # UI组件与统计
├── data/                # 原始与处理后文件
├── requirements.txt     # 依赖包
├── README.md            # 英文说明
├── README.zh.md         # 中文说明（本文件）
└── LICENSE
```

---

## 如何运行

1. **克隆仓库：**
   ```bash
   git clone https://github.com/mag233/rag-anki-kit.git
   cd rag-anki-kit
   ```

2. **安装依赖：**
   ```bash
   pip install -r requirements.txt
   ```

3. **设置OpenAI API密钥：**
   ```bash
   export OPENAI_API_KEY="你的API密钥"
   ```

4. **启动应用：**
   ```bash
   streamlit run app.py
   ```

---

## 使用方法

- 在 **RAG** 标签页上传并处理文档。
- 在 **文献综述** 标签页输入问题，获取总结与答案。
- 在 **Anki卡片** 标签页生成并导出记忆卡片。

---

## 参与贡献

我还在学习阶段，非常欢迎各种建议和帮助！如果你有想法或愿意参与：

1. Fork 本仓库。
2. 新建分支（`git checkout -b feature/你的功能`）。
3. 提交你的更改。
4. 发起 Pull Request。

---

## 许可证

本项目采用 [MIT License](LICENSE)。

---

感谢你的关注！如有建议或想交流，欢迎通过GitHub联系我。
