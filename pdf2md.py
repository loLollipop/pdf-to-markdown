#!/usr/bin/env python3
"""Convert academic PDF files to Markdown, with optional LaTeX formula support via Mathpix."""

from __future__ import annotations

import argparse
import os
import time
from pathlib import Path

import requests


def convert_with_mathpix(pdf_path: Path, output_path: Path, app_id: str, app_key: str, timeout: int = 600) -> Path:
    """Use Mathpix PDF API to convert PDF into Markdown with LaTeX formulas."""
    with pdf_path.open("rb") as f:
        files = {"file": (pdf_path.name, f, "application/pdf")}
        data = {
            "options_json": '{"math_inline_delimiters":["$","$"],"math_display_delimiters":["$$","$$"],"enable_tables_fallback":true}',
        }
        headers = {"app_id": app_id, "app_key": app_key}
        r = requests.post("https://api.mathpix.com/v3/pdf", headers=headers, files=files, data=data, timeout=60)

    r.raise_for_status()
    pdf_id = r.json()["pdf_id"]

    deadline = time.time() + timeout
    status_url = f"https://api.mathpix.com/v3/pdf/{pdf_id}"
    headers = {"app_id": app_id, "app_key": app_key}

    while time.time() < deadline:
        status_resp = requests.get(status_url, headers=headers, timeout=30)
        status_resp.raise_for_status()
        status_data = status_resp.json()
        status = status_data.get("status", "")

        if status == "completed":
            md_resp = requests.get(f"{status_url}.md", headers=headers, timeout=60)
            md_resp.raise_for_status()
            output_path.write_text(md_resp.text, encoding="utf-8")
            return output_path

        if status == "error":
            error = status_data.get("error", "Unknown Mathpix error")
            raise RuntimeError(f"Mathpix conversion failed: {error}")

        time.sleep(3)

    raise TimeoutError(f"Mathpix conversion timed out after {timeout}s")


def convert_with_local_backend(pdf_path: Path, output_path: Path) -> Path:
    """Fallback local conversion using pymupdf4llm (best-effort for formulas)."""
    try:
        import pymupdf4llm
    except ImportError as exc:
        raise RuntimeError(
            "Local backend requires pymupdf4llm. Install dependencies or use --engine mathpix."
        ) from exc

    markdown = pymupdf4llm.to_markdown(str(pdf_path))
    output_path.write_text(markdown, encoding="utf-8")
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert academic PDF to Markdown, optionally preserving formulas as LaTeX via Mathpix."
    )
    parser.add_argument("pdf", type=Path, help="Path to source PDF")
    parser.add_argument("-o", "--output", type=Path, help="Output markdown path (default: same name .md)")
    parser.add_argument(
        "--engine",
        choices=["mathpix", "local"],
        default="mathpix",
        help="Conversion engine: mathpix (best for LaTeX formulas) or local",
    )
    parser.add_argument("--timeout", type=int, default=600, help="Timeout seconds for mathpix job")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    pdf_path: Path = args.pdf

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    output_path = args.output or pdf_path.with_suffix(".md")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if args.engine == "mathpix":
        app_id = os.getenv("MATHPIX_APP_ID", "")
        app_key = os.getenv("MATHPIX_APP_KEY", "")
        if not app_id or not app_key:
            raise RuntimeError(
                "Mathpix credentials missing. Set MATHPIX_APP_ID and MATHPIX_APP_KEY, "
                "or run with --engine local."
            )
        result = convert_with_mathpix(pdf_path, output_path, app_id, app_key, timeout=args.timeout)
    else:
        result = convert_with_local_backend(pdf_path, output_path)

    print(f"✅ Markdown generated: {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
