# pdf-to-markdown

把学术论文 PDF 转成 Markdown，并尽可能保留公式为 LaTeX。

## 功能
- `mathpix` 引擎（默认）：通过 Mathpix PDF API，把公式转换为 `$...$` / `$$...$$` LaTeX。
- `local` 引擎：使用 `pymupdf4llm` 本地转换（无需云服务，但公式 LaTeX 质量不如 Mathpix）。

## 安装
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 使用方法

### 1) 推荐：Mathpix（公式效果更好）
先设置环境变量：
```bash
export MATHPIX_APP_ID="your_app_id"
export MATHPIX_APP_KEY="your_app_key"
```

执行：
```bash
python pdf2md.py paper.pdf -o paper.md --engine mathpix
```

### 2) 纯本地转换
```bash
python pdf2md.py paper.pdf -o paper.md --engine local
```

## 参数
```bash
python pdf2md.py <pdf路径> [-o 输出路径] [--engine mathpix|local] [--timeout 秒]
```

## 说明
- 如果你最关心“公式变成 LaTeX”，建议优先使用 `mathpix` 引擎。
- `local` 引擎适合离线场景，速度快，但公式识别效果受 PDF 质量影响较大。
