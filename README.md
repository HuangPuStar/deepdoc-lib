# Deepdoc

### 编程接口

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
