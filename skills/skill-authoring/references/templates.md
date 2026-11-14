# skill 模板

本文件给出可复制的 SKILL.md 骨架与 references/scripts 布局。复制后删掉不适用的段落，不保留空占位。

## frontmatter 模板

```markdown
---
name: <目录名>
description: <一段话：适用于什么任务、何时加载；写清不适用于什么>
argument-hint: '[可选上下文]'
---

# <标题>

<第一段：这个 skill 解决什么问题，为什么加载它>

## 适用范围与优先级

<适用顺序；与相邻 skill 的分工边界>

## 流程

<分步决策程序>

## 核心规则

<可判定的默认规则>

## 参考资料

- <模板或维度>：`references/<文件>.md`
```

## description 写法

写触发条件而不是摘要。好坏对比：

- 差：`文档规范 skill，帮助写文档。`（没有触发信息）
- 好：`定义、审查并重构项目的 README、指南与参考页。适用于启动文档集、审查过时与重复，或判断事实归属。`

## 目录布局

```text
<skill-name>/
├── SKILL.md
├── references/
│   ├── dimensions.md   # 按维度展开的规则与边缘情况
│   └── templates.md    # 可复制骨架
└── scripts/            # 可选；运行时脚本，不含测试
```

## 拆分判断

- 正文超过约一屏，把逐条展开移到 `references/dimensions.md`。
- 需要给读者复制粘贴的骨架，放 `references/templates.md`。
- 需要机器执行的校验或生成，放 `scripts/`，正文说明调用方式。

## 引用与链接

- 相对路径以 SKILL.md 所在目录为基准，用 Markdown 相对链接。
- 跨 skill 引用写清“由哪个 skill 裁定”，不复制内容。
- 打包后引用仍可解析；不要用仓库外绝对路径。
