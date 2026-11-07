# Literature to Lecture：从文献到讲义

[English](README.md)

一个 Codex 技能，将科学文献整理为忠于原文的教学讲义、单篇论文导读或综述，支持 Markdown 和 PDF。

更适合人工智能、计算机科学、物理等理科与技术领域，但不限定于这些领域。

- 获取并核查全文，保留可追溯来源。
- 通过具体算例讲清方法、公式、图表。
- 检查原文覆盖、读者理解和文档排版。

## 安装

```bash
git clone https://github.com/Hronrad/literature-to-lecture.git ~/.codex/skills/literature-to-lecture
```

## 使用

```text
使用 $literature-to-lecture，面向[读者]，将[论文/主题]讲解为[语言]的[Markdown/PDF]讲义。
```

附带 Python 3 文献记录核查脚本，仅依赖标准库；可选用 `pdfinfo` 核查 PDF 页数。脚本检查证据记录，不证明科学结论正确或文献覆盖穷尽。
