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

按以下层级判断效力，高层覆盖低层，低层只在高层未规定时补充：

1. 强制的平台、法律、宿主与全局用户约束。
2. 本 skill 的规则。
3. 既有项目约定与事实；项目约定只在本 skill 未规定时补充，作为输入按本 skill 的规则处理，不能覆盖本 skill。
4. 个人偏好，永远不能覆盖上述三层。

<与相邻 skill 的分工边界>

## 流程

<分步决策程序>

## 核心规则

<可判定的默认规则>

## 维度索引

每个维度的详细规则、示例与边界情况见 `references/dimensions.md`；维度列中的编号就是该文件中的节号。

| 维度 | 首条规则 | 详情 |
|---|---|---|
| 1. 维度 | 规则。 | `references/dimensions.md` 第 1 节 |

## 参考资料

- <模板或维度>：`references/<文件>.md`
```

含 `references/dimensions*.md` 的 skill 必须保留「维度索引」一节；不含维度文件的 skill 删掉该节。

## description 写法

写成“适用于…，不适用于…”，让代理据任务判断是否加载。三种失败写法：

- 太宽泛：`适用于一切编程任务。` → 无关任务也触发，浪费加载上下文。
- 太窄：`只用于修复 Python 3.11 的 asyncio 超时。` → 该触发的相邻任务从不加载。
- 复述名字：`文档规范 skill，帮助写文档。` → 没有触发信息，代理无从判断。

合格写法同时给适用范围与排除项：

`定义、审查并重构项目的 README、指南与参考页。适用于启动文档集、审查过时与重复，或判断事实归属；不适用于代码注释与 API 文档。`

## 目录布局

```text
<skill-name>/
├── SKILL.md
├── references/
│   ├── dimensions.md   # 按维度展开的规则；或按主题拆成 dimensions-<主题>.md
│   └── templates.md    # 可复制骨架；或按主题拆成 templates-<主题>.md
└── scripts/            # 可选；运行时脚本，不含测试
```

## 拆分判断

- 正文超过 250 行（不含 frontmatter），把逐条展开移到 `references/` 下的维度文件。
- 单个维度文件超过 300 行或 20 节时按主题拆成 `dimensions-<主题>.md`；其余 references 文件按内容命名，不受此
  拆分规则约束。正文索引说明句指向 `references/` 中对应文件，详情列写 `references/<文件>.md` 第 N 节，节号沿用
  原编号。
- 需要给读者复制粘贴的骨架，放 `references/` 下的模板文件。
- 需要机器执行的校验或生成，放 `scripts/`，正文说明调用方式。

## 可判定改写

把形容词换成可观察条件、阈值与正反例：

- 不可判定：`正文要合理拆分。`
- 可判定：`正文超过 250 行（不含 frontmatter），就把逐条展开、示例与边缘情况移到 references/，正文只留规则与默认值。`

## 引用与链接

- 相对路径以 SKILL.md 所在目录为基准，用 Markdown 相对链接。
- 跨 skill 引用写清“由哪个 skill 裁定”，不复制内容。
- 打包后引用仍可解析；不要用仓库外绝对路径。

## references 命名与去重

- 文件按内容维度命名，kebab-case。下列是示例而非闭集：`dimensions.md`、`dimensions-<主题>.md`、`templates.md`、
  `languages.md`、`playbooks.md`、`gates.md`、`evaluation.md`、`checklist.md`、`checklists.md`；清单只有一份时用
  `checklist.md`，多份时用 `checklists.md`。
- 文件名与正文链接一致，改文件名时同步改链接；不用无意义名（`ref1.md`、`extra.md`）。
- 一条事实只在一处：正文、各 references 之间不互相复制，其余用链接引用。
