# pdf-to-markdown

把学术论文 PDF 转成 Markdown，并尽可能保留公式为 LaTeX。

## 功能
- `mathpix` 引擎（默认）：通过 Mathpix PDF API，把公式转换为 `$...$` / `$$...$$` LaTeX。
- `local` 引擎：使用 `pymupdf4llm` 本地转换（无需云服务，但公式 LaTeX 质量不如 Mathpix）。
- 提供 Web API（FastAPI），可容器化部署到 ClawCloud Run。

## 安装
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## CLI 使用方法

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

## CLI 参数
```bash
python pdf2md.py <pdf路径> [-o 输出路径] [--engine mathpix|local] [--timeout 秒]
```

## Web API（用于 ClawCloud Run）
本项目新增 `app.py`，可通过 HTTP 上传 PDF 并返回 Markdown。

### 本地启动 API
```bash
uvicorn app:app --host 0.0.0.0 --port 8080
```

### 接口
- `GET /health`：健康检查
- `POST /convert`：转换接口（`multipart/form-data`）
  - `file`: PDF 文件
  - `engine`: `mathpix` 或 `local`（默认 `mathpix`）
  - `timeout`: Mathpix 超时时间秒数（默认 `600`）

示例：
```bash
curl -X POST "http://localhost:8080/convert" \
  -F "file=@paper.pdf" \
  -F "engine=mathpix" \
  -F "timeout=600"
```

## 部署到 ClawCloud Run
可以部署。你只需要：
1. 将仓库推到 GitHub。
2. 在 ClawCloud Run 新建服务，选择该仓库。
3. 使用仓库中的 `Dockerfile` 构建（默认监听 `PORT` 环境变量）。
4. 若使用 `mathpix` 引擎，在 ClawCloud Run 的环境变量里配置：
   - `MATHPIX_APP_ID`
   - `MATHPIX_APP_KEY`

部署后建议先访问 `/health`，再调用 `/convert`。

## 说明
- 如果你最关心“公式变成 LaTeX”，建议优先使用 `mathpix` 引擎。
- `local` 引擎适合离线场景，速度快，但公式识别效果受 PDF 质量影响较大。
