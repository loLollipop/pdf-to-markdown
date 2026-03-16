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

## 部署到 ClawCloud Run（GitHub 直连，不用手动推镜像）
可以部署，而且不需要你先自己构建并推送镜像。你只需要：
1. 将仓库推到 GitHub。
2. 在 ClawCloud Run 新建服务，代码来源选 GitHub 仓库。
3. 构建方式选择 Dockerfile（平台会自动从仓库构建镜像）。
4. 若使用 `mathpix` 引擎，在 ClawCloud Run 的环境变量里配置：
   - `MATHPIX_APP_ID`
   - `MATHPIX_APP_KEY`

部署后建议先访问 `/health`，再调用 `/convert`。

## Vercel 能不能部署？
可以做，但不推荐作为这个项目的主部署方案：
- Vercel 更偏前端/Serverless 场景。
- 本项目是 PDF 上传 + 解析任务，通常执行时间和资源占用都更大。
- 在 Serverless 平台上容易碰到请求体大小、执行超时、冷启动等限制。

如果你想要「从 GitHub 仓库直接拉代码并自动部署」，更建议优先使用：
- ClawCloud Run（当前已适配 Dockerfile）
- 或 Railway / Render 这类同样支持 GitHub 持续部署的平台

## 说明
- 如果你最关心“公式变成 LaTeX”，建议优先使用 `mathpix` 引擎。
- `local` 引擎适合离线场景，速度快，但公式识别效果受 PDF 质量影响较大。

## GitHub 自动构建镜像并推送（推荐你当前场景）
如果 ClawCloud Run 当前入口只支持填写镜像名，可以用下面方式：

1. 把本仓库推到 GitHub（默认分支建议 `main`）。
2. 本项目已提供 GitHub Actions 工作流：`.github/workflows/docker-ghcr.yml`。
3. 每次 push 到 `main`，GitHub 会自动：
   - 用仓库里的 `Dockerfile` 构建镜像
   - 推送到 `ghcr.io/<你的GitHub用户名或组织>/<仓库名>`
4. 然后去 ClawCloud Run 的 Image 部署页，填：
   - `Image Name`: `ghcr.io/<owner>/<repo>:latest`
   - 如果是私有镜像，选择 `Private` 并配置拉取凭据

### 首次使用 GHCR 的检查项
- 仓库 `Settings -> Actions -> General -> Workflow permissions` 设为 **Read and write permissions**（允许 push 到 packages）。
- 若组织仓库有额外策略，请确认允许 Actions 发布 GHCR 包。

### 工作流触发规则
- push 到 `main`：自动构建并推送
- push `v*` 标签：自动构建并推送版本标签
- 支持手动触发（`workflow_dispatch`）
