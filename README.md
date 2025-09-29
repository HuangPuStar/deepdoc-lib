# Deepdoc

### Installations

- pip
pip install git+https://github.com/HuangPuStar/deepdoc-lib.git

- uv 
Add the following to pyproject.toml

```toml
dependencies = [
    # ... 
    "deepdoc @ git+https://github.com/HuangPuStar/deepdoc-lib.git"
]
```
and run

``` sh
uv sync
```

### Usage

```python
from deepdoc import PdfParser, DocxParser, ExcelParse

# 解析 PDF
pdf_parser = PdfParser()
result = pdf_parser("document.pdf")

# 解析 Word
docx_parser = DocxParser()
result = docx_parser("document.docx")

# 解析 Excel
excel_parser = ExcelParser()
with open("data.xlsx", "rb") as f:
    result = excel_parser(f.read())
```

