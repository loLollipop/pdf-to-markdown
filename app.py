#!/usr/bin/env python3
"""HTTP service wrapper for PDF-to-Markdown conversion."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from pdf2md import convert_with_local_backend, convert_with_mathpix

app = FastAPI(title="pdf-to-markdown", version="1.0.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/convert")
def convert(
    file: UploadFile = File(...),
    engine: str = Form("mathpix"),
    timeout: int = Form(600),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only .pdf files are supported")

    if engine not in {"mathpix", "local"}:
        raise HTTPException(status_code=400, detail="engine must be one of: mathpix, local")

    with tempfile.TemporaryDirectory() as tmp:
        pdf_path = Path(tmp) / file.filename
        out_path = pdf_path.with_suffix(".md")

        with pdf_path.open("wb") as f:
            f.write(file.file.read())

        try:
            if engine == "mathpix":
                app_id = os.getenv("MATHPIX_APP_ID", "")
                app_key = os.getenv("MATHPIX_APP_KEY", "")
                if not app_id or not app_key:
                    raise HTTPException(
                        status_code=400,
                        detail="MATHPIX_APP_ID / MATHPIX_APP_KEY are required for mathpix engine",
                    )
                convert_with_mathpix(pdf_path, out_path, app_id, app_key, timeout=timeout)
            else:
                convert_with_local_backend(pdf_path, out_path)
        except HTTPException:
            raise
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        markdown = out_path.read_text(encoding="utf-8")

    return JSONResponse({"markdown": markdown, "engine": engine})
