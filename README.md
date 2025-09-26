# DeepDoc - 智能文档解析工具

DeepDoc 是一个从 RagFlow 中剥离出来的独立文档解析工具，支持多种文档格式的智能解析，包括 OCR、布局识别、表格结构识别等功能。

## 🚀 功能特性

- **多格式支持**: PDF、Word、PPT、Excel、图片、文本、Markdown、JSON、HTML
- **OCR 识别**: 基于 ONNX 的高精度文字识别
- **布局识别**: 智能识别文档布局结构
- **表格识别**: 自动识别和解析表格结构
- **视觉理解**: 支持图片内容描述
- **独立运行**: 完全剥离，不依赖 RagFlow 其他组件

## 📦 安装

### 1. 克隆项目
```bash
git clone <your-repo-url>
cd deepdoc
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 下载模型文件
模型文件会自动下载到 `dict/` 目录中。

## 🛠️ 使用方法

### 命令行工具

```bash
# 基本用法
python deepdoc_cli.py <文件路径>

# 解析 PDF 文件
python deepdoc_cli.py document.pdf

# 解析 Word 文件并保存结果
python deepdoc_cli.py document.docx -o result.txt

# 解析图片文件
python deepdoc_cli.py image.jpg --vision-provider openai

# 解析 Excel 文件
python deepdoc_cli.py data.xlsx -o excel_result.txt
```

### 支持的参数

- `file`: 要解析的文件路径
- `-o, --output`: 输出文件路径（可选）
- `--vision-provider`: 视觉模型提供商（用于图片解析）
  - 选项: openai, qwen, zhipu, ollama, gemini, anthropic
  - 默认: qwen

### 编程接口

```python
from parser import PdfParser, DocxParser, ExcelParser
from depend.simple_cv_model import create_vision_model

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

# 图片解析
vision_model = create_vision_model("qwen")
with open("image.jpg", "rb") as f:
    result = vision_model.describe_with_prompt(f.read())
```

## 📁 项目结构

```
deepdoc/
├── deepdoc_cli.py          # 命令行工具
├── requirements.txt        # 依赖文件
├── deepdoc_config.yaml    # 配置文件
├── README.md              # 说明文档
├── parser/                # 解析器模块
│   ├── __init__.py
│   ├── pdf_parser.py
│   ├── docx_parser.py
│   ├── ppt_parser.py
│   ├── excel_parser.py
│   └── ...
├── vision/                # 视觉处理模块
│   ├── __init__.py
│   ├── ocr.py
│   ├── layout_recognizer.py
│   └── ...
├── depend/                # 依赖模块
│   ├── __init__.py
│   ├── simple_cv_model.py
│   ├── rag_tokenizer.py
│   └── ...
├── dict/                  # 模型文件目录
│   ├── ocr/              # OCR 模型
│   ├── huqie.txt         # 中文分词词典
│   └── ...
├── prompts/               # 提示词模板
└── test/                  # 测试文件
```

## ⚙️ 配置

### 环境变量

```bash
# 视觉模型配置
export DEEPDOC_VISION_PROVIDER="qwen"
export DEEPDOC_VISION_API_KEY="your-api-key"
export DEEPDOC_VISION_MODEL="qwen-vl-max"

# 其他配置
export DEEPDOC_LIGHTEN=0  # 是否使用轻量模式
```

### 配置文件

创建 `deepdoc_config.yaml`:

```yaml
vision_model:
  provider: "qwen"
  model_name: "qwen-vl-max"
  api_key: "your-api-key"
  lang: "Chinese"
```

## 🔧 开发

### 运行测试

```bash
cd test
python test_real_files.py
```

### 添加新的解析器

1. 在 `parser/` 目录下创建新的解析器类
2. 继承基础解析器类或实现 `__call__` 方法
3. 在 `parser/__init__.py` 中导入新解析器
4. 在 `deepdoc_cli.py` 中添加文件扩展名映射

## 📊 性能

- **PDF 解析**: ~1.5秒/页
- **Word 解析**: ~1.6秒/文档
- **Excel 解析**: ~0.01秒/文件
- **图片解析**: ~0.2秒/图片

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

本项目基于 MIT 许可证开源。

## 🙏 致谢

本项目基于 [RagFlow](https://github.com/infiniflow/ragflow) 的 DeepDoc 模块开发，感谢原项目的贡献者。