"""Regression tests for fixes ported from upstream ragflow (2026-07 sync).

Each test pins one ported fix. They avoid model downloads: only pure-Python
code paths are exercised.
"""

import io
import logging
import os
import zipfile

import pytest


# ---------------------------------------------------------------------------
# vision/operators.py — ragflow #16785
# ---------------------------------------------------------------------------
def test_standardize_image_resolves_by_canonical_name():
    from deepdoc.vision import operators

    assert hasattr(operators, "StandardizeImage")
    assert not hasattr(operators, "StandardizeImag")

    import numpy as np

    op = getattr(operators, "StandardizeImage")(
        mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225], is_scale=True
    )
    out, _ = op(np.ones((4, 4, 3), dtype="float32"), {})
    assert out.shape == (4, 4, 3)


# ---------------------------------------------------------------------------
# parser/markdown_parser.py — ragflow #15630/#15632/#16109/#16319 et al.
# ---------------------------------------------------------------------------
def test_markdown_tables_and_code_blocks_survive_delimiter_split():
    from deepdoc.parser.markdown_parser import MarkdownElementExtractor

    text = (
        "# Title\n"
        "Intro; with delimiter.\n\n"
        "| a | b |\n"
        "|-|:-|\n"
        "| 1; x | 2 |\n\n"
        "```python\ncode; still code\n```\n"
        "Tail; end."
    )
    ex = MarkdownElementExtractor(text)
    assert ex._is_table_separator_row("|-|:-|"), "GFM one-dash separator must be accepted"
    sections = ex.extract_elements(delimiter=";")
    joined = "\n".join(sections)
    assert "| 1; x | 2 |" in joined, "table row must not be split at the delimiter"
    assert "code; still code" in joined, "fenced code must not be split at the delimiter"


# ---------------------------------------------------------------------------
# parser/excel_parser.py — ragflow #16287 / #15490 / #13018
# ---------------------------------------------------------------------------
def _xlsx_bytes(rows):
    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    for r in rows:
        ws.append(r)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def test_excel_keeps_zero_and_false_cells():
    from deepdoc.parser.excel_parser import RAGFlowExcelParser

    data = _xlsx_bytes([["h1", "h2"], [0, False], ["", None]])
    res = RAGFlowExcelParser()(data)
    joined = " || ".join(res)
    assert "0" in joined
    assert "False" in joined
    assert len(res) == 1, "all-empty row must not emit a line"


def test_excel_html_no_header_only_chunk_at_exact_multiple():
    from deepdoc.parser.excel_parser import RAGFlowExcelParser

    data = _xlsx_bytes([["h"], [1], [2]])
    chunks = RAGFlowExcelParser().html(data, chunk_rows=2)
    assert len(chunks) == 1


# ---------------------------------------------------------------------------
# parser/html_parser.py — ragflow #16423 / #13833 / #16052
# ---------------------------------------------------------------------------
def test_html_title_tags_h4_mapping():
    from deepdoc.parser import html_parser

    assert html_parser.TITLE_TAGS["h4"] == "####"


def test_html_parses_bodyless_fragment():
    from deepdoc.parser.html_parser import RAGFlowHtmlParser

    parser = RAGFlowHtmlParser()
    sections = parser.parser_txt("<div><p>hello fragment</p></div>", chunk_token_num=512)
    assert any("hello fragment" in s for s in sections)


def test_html_oversized_block_split_preserves_text():
    from deepdoc.parser.html_parser import RAGFlowHtmlParser

    parser = RAGFlowHtmlParser()
    block = "word " * 1200
    pieces = parser._split_oversized_block(block.strip(), 512)
    assert "".join(pieces).replace(" ", "") == block.strip().replace(" ", "")


# ---------------------------------------------------------------------------
# zip extraction hardening — ragflow #12527
# ---------------------------------------------------------------------------
def _zip_with(arcname, payload=b"evil"):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(arcname, payload)
    return buf.getvalue()


@pytest.mark.parametrize(
    "arcname", ["../escape.txt", "/abs.txt", "C:/win.txt", "a/../../up.txt"]
)
def test_mineru_zip_rejects_unsafe_entries(tmp_path, arcname):
    from deepdoc.parser.mineru_parser import MinerUParser

    zpath = tmp_path / "evil.zip"
    zpath.write_bytes(_zip_with(arcname))

    class Dummy:
        logger = logging.getLogger("test")
        _is_zipinfo_symlink = staticmethod(MinerUParser._is_zipinfo_symlink)

    with pytest.raises(RuntimeError):
        MinerUParser._extract_zip_no_root(Dummy(), str(zpath), str(tmp_path / "out"), None)


def test_mineru_zip_extracts_benign_entries(tmp_path):
    from deepdoc.parser.mineru_parser import MinerUParser

    zpath = tmp_path / "ok.zip"
    zpath.write_bytes(_zip_with("ok/file.txt", b"fine"))

    class Dummy:
        logger = logging.getLogger("test")
        _is_zipinfo_symlink = staticmethod(MinerUParser._is_zipinfo_symlink)

    outdir = tmp_path / "out"
    MinerUParser._extract_zip_no_root(Dummy(), str(zpath), str(outdir), None)
    assert (outdir / "ok" / "file.txt").read_bytes() == b"fine"


def test_tcadp_zip_rejects_traversal_entries(tmp_path):
    from deepdoc.parser.tcadp_parser import TCADPParser

    zpath = tmp_path / "evil.zip"
    zpath.write_bytes(_zip_with("../escape.json", b"{}"))

    class Dummy:
        logger = logging.getLogger("test")
        _is_zipinfo_symlink = staticmethod(TCADPParser._is_zipinfo_symlink)

    assert TCADPParser._extract_content_from_zip(Dummy(), str(zpath)) == []


# ---------------------------------------------------------------------------
# parser/pdf_parser.py — ragflow #13404 / #16958 / #14382 / #14385
# ---------------------------------------------------------------------------
def test_pdf_garbled_detection_statics():
    from deepdoc.parser.pdf_parser import RAGFlowPdfParser as K

    assert K._is_garbled_char("")
    assert not K._is_garbled_char("永")
    assert K._is_garbled_text("(cid:123) hello")
    assert not K._is_garbled_text("normal text 中文")
    assert K._has_subset_font_prefix("DY1+ZLQDm1-1")
    assert not K._has_subset_font_prefix("Arial")


def test_pdf_insert_word_spaces_latin_not_cjk():
    from deepdoc.parser.pdf_parser import RAGFlowPdfParser as K

    latin = [
        {"text": "hello", "x0": 0, "x1": 10, "width": 10},
        {"text": "world", "x0": 14, "x1": 24, "width": 10},
    ]
    K._insert_word_spaces(latin)
    assert latin[0]["text"] == "hello "

    cjk = [
        {"text": "中", "x0": 0, "x1": 10, "width": 10},
        {"text": "文", "x0": 14, "x1": 24, "width": 10},
    ]
    K._insert_word_spaces(cjk)
    assert cjk[0]["text"] == "中"


def test_pdf_page_limit_and_offset_tag():
    from deepdoc.parser import pdf_parser

    assert pdf_parser.MAXIMUM_PAGE_NUMBER == 100000
    out = pdf_parser.RAGFlowPdfParser._offset_position_tag("@@1-2\t0.0\t1.0\t2.0\t3.0##", 50)
    assert out.startswith("@@51-52\t")


# ---------------------------------------------------------------------------
# parser/epub_parser.py — ragflow #13650
# ---------------------------------------------------------------------------
def test_epub_parses_spine_order():
    from deepdoc.parser.epub_parser import RAGFlowEpubParser

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(
            "META-INF/container.xml",
            '<?xml version="1.0"?>'
            '<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
            '<rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles>'
            "</container>",
        )
        z.writestr(
            "OEBPS/content.opf",
            '<?xml version="1.0"?>'
            '<package xmlns="http://www.idpf.org/2007/opf">'
            "<manifest>"
            '<item id="c1" href="c1.xhtml" media-type="application/xhtml+xml"/>'
            "</manifest>"
            '<spine><itemref idref="c1"/></spine>'
            "</package>",
        )
        z.writestr("OEBPS/c1.xhtml", "<html><body><p>epub says hi</p></body></html>")

    parser = RAGFlowEpubParser()
    sections = parser("test.epub", binary=buf.getvalue())
    assert any("epub says hi" in s for s in sections)


# ---------------------------------------------------------------------------
# vision/table_structure_recognizer.py — ragflow #15481
# ---------------------------------------------------------------------------
def test_tsr_caption_matches_english_patterns():
    from deepdoc.vision.table_structure_recognizer import TableStructureRecognizer

    for text in ["Figure 3: results", "Table 12. stats", "Fig. 4 overview"]:
        assert TableStructureRecognizer.is_caption({"text": text, "layout_type": ""}), text
