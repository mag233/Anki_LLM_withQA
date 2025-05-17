# 📘 Anki 卡片模板说明文档（Maggie 专用）

---

## 🧩 模板 1：问答卡（适合定义、概念、计算题）

### 🧾 用途  
- 学术名词解释（中英文）
- 数学公式推导步骤
- Python 函数用途解释
- 公共卫生知识点对照

---

### ✅ 字段命名建议：
- `Question` → 问题描述
- `Answer` → 答案内容（可含 Latex 公式或解释）
- `Tag`（可选）→ 例如：`math-linear-concept`

---

### ✅ 卡片模板设置

#### 样式（CSS）：
```css
.card {
  font-family: "Segoe UI", "Helvetica Neue", sans-serif;
  font-size: 20px;
  background-color: #fefefe;
  color: #333;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
  line-height: 1.7;
  max-width: 700px;
  margin: auto;
}

h2 {
  margin-top: 0;
  margin-bottom: 12px;
  font-size: 22px;
  font-weight: bold;
  color: #1a1a1a;
}

hr {
  border: none;
  border-top: 1px solid #ccc;
  margin: 16px 0;
}
```

#### 正面模板（Front）：
```html
<h2>Question</h2>
<div>{{Question}}</div>
```

#### 背面模板（Back）：
```html
<h2>Question</h2>
<div>{{Question}}</div>
<hr>
<h2>Answer</h2>
<div>{{Answer}}</div>
```

---

## 🧩 模板 2：Cloze 填空卡（适合公式、术语、语言记忆）

### 🧾 用途  
- 公式记忆（如 $\sec^2 x = 1 + 	an^2 x$）
- 重要术语（如 "Knowledge Translation"）
- 专业长句中关键词隐藏训练

---

### ✅ 字段命名建议：
- `文字` → Cloze 填空正文
- `背面额外`（可选）→ 解释、提示等补充信息

---

### ✅ 卡片模板设置

#### 样式（CSS）：
```css
.card {
  font-family: "Segoe UI", "Helvetica Neue", sans-serif;
  font-size: 20px;
  text-align: left;
  color: #2e2e2e;
  background-color: #fefefe;
  padding: 24px;
  border-radius: 14px;
  box-shadow: 0 0 12px rgba(0, 0, 0, 0.05);
  line-height: 1.75;
  max-width: 700px;
  margin: auto;
}

.cloze {
  font-weight: bold;
  color: #007acc;
  background-color: #e6f2fb;
  padding: 2px 4px;
  border-radius: 4px;
}

.nightMode .cloze {
  color: #4da8ff;
  background-color: #223344;
}

h2 {
  font-size: 22px;
  margin-top: 0;
  margin-bottom: 12px;
  color: #222;
}

hr {
  margin: 24px 0;
  border: none;
  border-top: 1px solid #ddd;
}

.note {
  font-size: 16px;
  color: #999;
  margin-top: 12px;
}
```

#### 正面模板（Front）：
```html
<h2>Fill in the blank:</h2>
<div>{{cloze:文字}}</div>
```

#### 背面模板（Back）：
```html
<h2>Fill in the blank:</h2>
<div>{{cloze:文字}}</div>

{{#背面额外}}
  <hr>
  <h2>Explanation</h2>
  <div>{{背面额外}}</div>
{{/背面额外}}
```

---

## 💡 制作技巧

| 用法 | 示例 |
|------|------|
| Cloze 填空语法 | `{{c1::supervised learning}}` |
| LaTeX 数学公式 | `\[ a^2 + b^2 = c^2 \]` |
| 添加注释 | `<span class="note">中文提示</span>` |
| 多个空格 | `{{c1::Supervised}}, {{c2::Unsupervised}}` |
| 音频插入 | `[sound:xxx.mp3]`（用于语言学习） |

---

## 📦 文件保存建议
- 将本说明文档保存为 `.md` 或 `.docx` 文件放入学习资料目录
- 将模板样式备份为 `.apkg` 文件（可让我帮你打包）
