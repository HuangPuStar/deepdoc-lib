# Upstream Sync Record

This library is a standalone, pip-installable extraction of the `deepdoc/`
module from [infiniflow/ragflow](https://github.com/infiniflow/ragflow),
restructured around explicit configuration injection
(`PdfModelConfig` / `TokenizerConfig`, `DEEPDOC_*` env vars) and
ModelScope-based model distribution instead of ragflow's global settings and
HuggingFace runtime downloads.

Upstream changes are **ported by behavior, never by wholesale file copy**,
so the library's public API (`from deepdoc import PdfParser, ...`) and
packaging stay stable.

## Sync history

### 2026-07-23 — synced to ragflow `18ea0fb7` (2026-07-22)

Ported fixes (upstream PR references):

| Area | Fix | Upstream |
|---|---|---|
| vision/operators | `StandardizeImag` → `StandardizeImage` rename; the dynamic `getattr(operators, "StandardizeImage")` dispatch silently skipped image standardization before | [#16785](https://github.com/infiniflow/ragflow/pull/16785) |
| mineru/tcadp | zip extraction hardening: reject symlink / encrypted / absolute-path / `..`-traversal / zip-slip entries; streaming download for TCADP results | [#12527](https://github.com/infiniflow/ragflow/pull/12527) |
| html_parser | parse bodyless HTML fragments (`soup.body or soup`) | [#16423](https://github.com/infiniflow/ragflow/pull/16423) |
| html_parser | switch `html5lib` → `html.parser` (aligns with upstream #14486-era behavior the later fixes assume) | [#14486](https://github.com/infiniflow/ragflow/pull/14486) |
| html_parser | h4 heading mapping `#####` → `####` | [#13833](https://github.com/infiniflow/ragflow/pull/13833) |
| html_parser | oversized-block splitting preserves original text (CJK-aware atom splitting) | [#16052](https://github.com/infiniflow/ragflow/pull/16052) |
| excel_parser | keep `0` / `False` cells; skip fully-empty rows | [#16287](https://github.com/infiniflow/ragflow/pull/16287) |
| excel_parser | no spurious header-only chunk when data rows are an exact multiple of `chunk_rows` | [#15490](https://github.com/infiniflow/ragflow/pull/15490) |
| excel_parser | binary-search actual row count for sheets with abnormal `max_row` | [#13018](https://github.com/infiniflow/ragflow/pull/13018) |
| markdown_parser | full sync to upstream state: protected ranges (fenced code / MD tables / HTML tables) never split by delimiters; GFM separators with 1+ dashes; lone-header attachment | #10896 #11018 #11520 #13892 #15630 #15632 #16109 #16319 |
| ppt_parser | cached, None-safe shape sorting (group shapes with `top=None` no longer crash) | [#13054](https://github.com/infiniflow/ragflow/pull/13054) |
| parser/utils | `get_text`: `if binary:` → `if binary is not None:` | [#13196](https://github.com/infiniflow/ragflow/pull/13196) |
| table_structure_recognizer | English caption patterns (`Figure N` / `Table N` / `Fig. N`) | [#15481](https://github.com/infiniflow/ragflow/pull/15481) |
| vision/ocr | env-configurable ONNX thread counts (`OCR_INTRA_OP_NUM_THREADS` / `OCR_INTER_OP_NUM_THREADS`) and opt-in GPU arena shrinkage (`OCR_GPUMEM_ARENA_SHRINKAGE=1`) | [#12777](https://github.com/infiniflow/ragflow/pull/12777) |
| layout_recognizer | figure/equation placeholder boxes get per-type layoutno namespaces (`figure-N` / `equation-N`), preventing unrelated figure and equation crops from merging on scientific PDFs | [#15873](https://github.com/infiniflow/ragflow/pull/15873) |
| layout_recognizer | re-enable CID-pattern garbage filter for text boxes | [#13404](https://github.com/infiniflow/ragflow/pull/13404) |
| pdf_parser | garbled-text detection → OCR fallback (PUA/CID chars, subset-font encoding garbling, OCR-alphabet coverage check) | [#13404](https://github.com/infiniflow/ragflow/pull/13404) |
| pdf_parser | geometry-based word-space recovery, CJK-aware (`_insert_word_spaces`) | [#16958](https://github.com/infiniflow/ragflow/pull/16958) |
| pdf_parser | remove 299-page hardcoded limit (`MAXIMUM_PAGE_NUMBER = 100000`) | [#14382](https://github.com/infiniflow/ragflow/pull/14382) |
| pdf_parser | chunked `parse_into_bboxes` for large PDFs (`PDF_PARSER_PAGE_BATCH_SIZE`, default 50) with window→global box remapping; lazy `img_np` in `__ocr` | [#14385](https://github.com/infiniflow/ragflow/pull/14385) |
| pdf_parser | out-of-range page-index guards in `cropout` / table-figure insertion | [#12938](https://github.com/infiniflow/ragflow/pull/12938) [#12848](https://github.com/infiniflow/ragflow/pull/12848) |
| pdf_parser (VisionParser) | `pdf_page_num = from_page + idx` (page numbering was wrong when `from_page > 0`); fixed broken relative import of `llm_adapter` | [#12938](https://github.com/infiniflow/ragflow/pull/12938) + fork-local fix |
| parser (new) | EPUB parser (spine-order XHTML extraction, delegates to HtmlParser), exported as `deepdoc.EpubParser` | [#13650](https://github.com/infiniflow/ragflow/pull/13650) |

Already present before this sync (no action needed): `ast.literal_eval`
security fix (#12236), XLS/calamine loading (#10660), chartsheet guards
(#10819), KMeans multi-column detection (#11415 + #12534 cleanup),
`is_english` regex fix (#11432), OCR GPU memory limit env (#10407),
`vision_figure_parser_docx_wrapper` guard (#12104).

**Deliberately NOT ported** (decisions):

- **Go + HTTP microservice pipeline** (#16323, `deepdoc/server/`, `DEEPDOC_URL`
  DLA client): conflicts with this library's pure-Python, in-process design.
- **Automatic table orientation detection/rotation** (#12719 feature +
  #12981 / #17016 follow-ups): feature not in our baseline; runs 4× OCR per
  table; adopt separately if ever needed.
- **`rag.utils.lazy_image` memory refactors** (docx/excel lazy image loading,
  #13329 / #13558): optimization only; deferred until vendoring lazy_image is
  justified.
- **3-tuple outlines** (`extract_pdf_outlines` returning
  `(title, depth, page)`, #10456 TOC feature): our `outlines` stays
  `(title, depth)` to avoid breaking downstream consumers.
- **`model_speciess` → `model_species` rename** (#13929): our attribute name
  is part of the public surface; renaming would break existing callers.
- **paddleocr / opendataloader / somark parsers**: cloud-API clients, not
  currently needed; revisit on demand.
- **MinerU feature evolution** (API-only backends, VLM descriptions, etc.):
  only the security fix was taken; feature sync deferred until MinerU usage
  is confirmed.
- **Pure refactors** (moving functions between ragflow modules, lefthook
  reformatting): not applicable to our layout.

Regression tests: `tests/test_upstream_sync_regressions.py`.

## How to run the next sync

```bash
# in a ragflow clone
git log --reverse --format="%h %ad %s" --date=short 18ea0fb7..origin/main -- deepdoc
```

Then for each commit: understand the behavior change, find the corresponding
code in this repo, and re-implement it in this library's style (config
injection, relative imports, vendored `common/` + `depend/`). Update this file.
