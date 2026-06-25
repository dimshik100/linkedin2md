from __future__ import annotations
"""Optional PDF generation from generated profile markdown.

SOLID principles compliance:
- Single Responsibility: Handles Markdown to PDF conversion using
  an optional Weasyprint backend.
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def convert_md_to_pdf(markdown_content: str, pdf_path: Path) -> bool:
    """Convert generated profile markdown into an elegant, styled A4 print-ready PDF.

    This feature is optional and requires 'markdown' package.
    If 'weasyprint' is missing, it falls back to Google Chrome headless printing.
    """
    try:
        import markdown  # type: ignore
    except ImportError:
        logger.error("PDF generation requires the 'markdown' package.")
        return False

    try:
        # Convert Markdown to HTML
        html_body = markdown.markdown(
            markdown_content, extensions=["tables", "fenced_code"]
        )

        # Styled executive A4 print CSS
        styled_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>LinkedIn Export Resume</title>
    <style>
        @page {{
            size: A4;
            margin: 15mm;
            @bottom-right {{
                content: "Page " counter(page) " of " counter(pages);
                font-size: 8pt;
                font-family: Arial, sans-serif;
                color: #777;
            }}
        }}
        body {{
            font-family: Arial, sans-serif;
            font-size: 9.5pt;
            line-height: 1.45;
            color: #333;
            margin: 0;
            padding: 0;
        }}
        h1 {{
            font-size: 20pt;
            font-weight: bold;
            color: #111;
            margin: 0 0 4px 0;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        p {{
            margin: 0 0 10px 0;
        }}
        strong {{
            color: #111;
        }}
        h1 + p {{
            font-size: 11pt;
            color: #0056b3;
            font-weight: bold;
            margin-bottom: 8px;
        }}
        /* Contact block */
        h1 + p + p {{
            font-size: 9pt;
            color: #555;
            margin-bottom: 15px;
            border-bottom: 2px solid #333;
            padding-bottom: 10px;
        }}
        h2 {{
            font-size: 12pt;
            color: #111;
            border-bottom: 1px solid #aaa;
            padding-bottom: 3px;
            margin: 18px 0 10px 0;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        h3 {{
            font-size: 10.5pt;
            color: #111;
            margin: 12px 0 4px 0;
        }}
        h3 strong {{
            font-weight: bold;
        }}
        h3 + p {{
            font-style: italic;
            color: #555;
            margin-bottom: 6px;
            font-size: 9pt;
        }}
        ul {{
            margin: 0 0 10px 0;
            padding-left: 20px;
        }}
        li {{
            margin-bottom: 4px;
            text-align: justify;
        }}
        hr {{
            display: none; /* Hide horizontal rules since we use borders on headers */
        }}
        a {{
            color: #0056b3;
            text-decoration: none;
        }}
    </style>
</head>
<body>
{html_body}
</body>
</html>
"""
        # Try using WeasyPrint first
        try:
            from weasyprint import HTML  # type: ignore
            HTML(string=styled_html).write_pdf(str(pdf_path))
            return True
        except Exception as wp_error:
            logger.info("WeasyPrint not available or failed: %s. Trying Google Chrome fallback...", wp_error)

        # Fallback to Google Chrome headless printing
        import subprocess
        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        if Path(chrome_path).exists():
            temp_html_path = pdf_path.with_suffix(".html")
            temp_html_path.write_text(styled_html, encoding="utf-8")
            try:
                subprocess.run([
                    chrome_path,
                    "--headless",
                    "--disable-gpu",
                    f"--print-to-pdf={pdf_path}",
                    str(temp_html_path)
                ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if temp_html_path.exists():
                    temp_html_path.unlink()
                return True
            except Exception as chrome_error:
                logger.error("Chrome PDF generation failed: %s", chrome_error)
                if temp_html_path.exists():
                    temp_html_path.unlink()
        else:
            logger.error("Google Chrome not found at %s", chrome_path)

        return False
    except Exception as e:
        logger.error("Failed to generate PDF: %s", e)
        return False
