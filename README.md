# Literature to Lecture

[中文](README.zh-CN.md)

A Codex skill for turning scientific papers into source-faithful lectures, single-paper handouts, and surveys in Markdown or PDF.

Best suited to science and technical fields such as artificial intelligence, computer science, and physics; not restricted to these fields.

- Retrieve and inspect full texts with traceable sources.
- Explain methods, formulas, figures, and tables with worked examples.
- Check source coverage, reader comprehension, and document layout.

## Install

```bash
git clone https://github.com/Hronrad/literature-to-lecture.git ~/.codex/skills/literature-to-lecture
```

## Use

```text
Use $literature-to-lecture to explain [paper/topic] for [audience] in [language], as [Markdown/PDF].
```

Includes a Python 3 corpus audit script (standard library only; optional `pdfinfo` for PDF page checks). Its checks cover evidence bookkeeping, not scientific correctness or exhaustive coverage.
