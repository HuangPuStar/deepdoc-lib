import os
import sys
import time
import json
import traceback
from pathlib import Path
from datetime import datetime

# 清除代理设置
os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''
os.environ['NO_PROXY'] = '*'
os.environ['no_proxy'] = '*'

# 添加 deepdoc 路径到 sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# 导入所有解析器
from parser import (
    TxtParser, MarkdownParser, JsonParser, HtmlParser, 
    ExcelParser, PptParser, DocxParser, PdfParser
)
from parser.figure_parser import VisionFigureParser

# 导入视觉模型
from ..depend.simple_cv_model import create_vision_model


class RealFileParserTest:
    """真实文件解析测试类"""
    
    def __init__(self):
        """初始化测试环境"""
        # 创建测试数据目录
        self.test_data_dir = Path(__file__).parent / "test_data"
        
        # 创建测试结果目录
        self.test_results_dir = Path(__file__).parent / "test_results"
        self.test_results_dir.mkdir(exist_ok=True)
        
        # 创建视觉模型实例
        try:
            self.vision_model = create_vision_model("qwen")
            print("✅ 视觉模型创建成功")
        except Exception as e:
            print(f"⚠️ 视觉模型创建失败: {e}")
            self.vision_model = None
        
        # 初始化解析器
        self.parsers = {
            "txt": TxtParser(),
            "md": MarkdownParser(),
            "json": JsonParser(),
            "html": HtmlParser(),
            "excel": ExcelParser(),
            "pdf": PdfParser(),
            "docx": DocxParser(),
            "ppt": PptParser(),
        }
        
        # 测试文件映射
        self.test_files = {
            "pdf": "test.pdf",
            "docx": "test.docx", 
            "ppt": "test.ppt",
            "xlsx": "test.xlsx",
            "jpg": "test.jpg",
        }
        
        # 测试结果存储
        self.results = {}
        
    def log(self, message):
        """日志输出"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def save_result(self, file_type, result, parse_time):
        """保存解析结果"""
        result_file = self.test_results_dir / f"{file_type}_result.txt"
        
        with open(result_file, 'w', encoding='utf-8') as f:
            f.write(f"文件类型: {file_type}\n")
            f.write(f"解析时间: {parse_time:.2f}秒\n")
            f.write(f"结果类型: {type(result)}\n")
            f.write(f"结果长度: {len(str(result))}字符\n")
            f.write("-" * 50 + "\n")
            f.write(str(result))
        
        # 保存到结果字典
        self.results[file_type] = {
            "success": True,
            "parse_time": parse_time,
            "result_length": len(str(result)),
            "result_type": str(type(result)),
            "result_file": str(result_file)
        }
    
    def save_error(self, file_type, error, parse_time):
        """保存错误信息"""
        error_file = self.test_results_dir / f"{file_type}_error.txt"
        
        with open(error_file, 'w', encoding='utf-8') as f:
            f.write(f"文件类型: {file_type}\n")
            f.write(f"解析时间: {parse_time:.2f}秒\n")
            f.write(f"错误类型: {type(error).__name__}\n")
            f.write(f"错误信息: {str(error)}\n")
            f.write("-" * 50 + "\n")
            f.write(traceback.format_exc())
        
        # 保存到结果字典
        self.results[file_type] = {
            "success": False,
            "parse_time": parse_time,
            "error": str(error),
            "error_file": str(error_file)
        }
    
    def test_pdf_parser(self):
        """测试PDF解析器"""
        self.log("开始测试PDF解析器...")
        
        file_path = self.test_data_dir / self.test_files["pdf"]
        if not file_path.exists():
            self.log(f"❌ PDF文件不存在: {file_path}")
            return
        
        start_time = time.time()
        try:
            parser = self.parsers["pdf"]
            # 传递字符串路径而不是 Path 对象
            result = parser(str(file_path))
            
            parse_time = time.time() - start_time
            self.log(f"✅ PDF解析成功，耗时: {parse_time:.2f}秒")
            
            # 显示结果预览
            if isinstance(result, list):
                self.log(f"   解析出 {len(result)} 个chunk")
                for i, chunk in enumerate(result[:3]):
                    preview = str(chunk)[:100] + "..." if len(str(chunk)) > 100 else str(chunk)
                    self.log(f"   Chunk {i}: {preview}")
            else:
                preview = str(result)[:200] + "..." if len(str(result)) > 200 else str(result)
                self.log(f"   结果预览: {preview}")
            
            self.save_result("pdf", result, parse_time)
            
        except Exception as e:
            parse_time = time.time() - start_time
            self.log(f"❌ PDF解析失败: {e}")
            self.save_error("pdf", e, parse_time)

    def test_docx_parser(self):
        """测试Word解析器"""
        self.log("开始测试Word解析器...")
        
        file_path = self.test_data_dir / self.test_files["docx"]
        if not file_path.exists():
            self.log(f"❌ Word文件不存在: {file_path}")
            return
        
        start_time = time.time()
        try:
            parser = self.parsers["docx"]
            # 传递字符串路径而不是 Path 对象
            result = parser(str(file_path))
            
            parse_time = time.time() - start_time
            self.log(f"✅ Word解析成功，耗时: {parse_time:.2f}秒")
            
            # 显示结果预览
            if isinstance(result, list):
                self.log(f"   解析出 {len(result)} 个chunk")
                for i, chunk in enumerate(result[:3]):
                    preview = str(chunk)[:100] + "..." if len(str(chunk)) > 100 else str(chunk)
                    self.log(f"   Chunk {i}: {preview}")
            else:
                preview = str(result)[:200] + "..." if len(str(result)) > 200 else str(result)
                self.log(f"   结果预览: {preview}")
            
            self.save_result("docx", result, parse_time)
            
        except Exception as e:
            parse_time = time.time() - start_time
            self.log(f"❌ Word解析失败: {e}")
            self.save_error("docx", e, parse_time)

    def test_ppt_parser(self):
        """测试PPT解析器"""
        self.log("开始测试PPT解析器...")
        
        file_path = self.test_data_dir / self.test_files["ppt"]
        if not file_path.exists():
            self.log(f"❌ PPT文件不存在: {file_path}")
            return
        
        start_time = time.time()
        try:
            parser = self.parsers["ppt"]
            # 添加必需的参数
            result = parser(str(file_path), from_page=0, to_page=100000)
            
            parse_time = time.time() - start_time
            self.log(f"✅ PPT解析成功，耗时: {parse_time:.2f}秒")
            
            # 显示结果预览
            if isinstance(result, list):
                self.log(f"   解析出 {len(result)} 个chunk")
                for i, chunk in enumerate(result[:3]):
                    preview = str(chunk)[:100] + "..." if len(str(chunk)) > 100 else str(chunk)
                    self.log(f"   Chunk {i}: {preview}")
            else:
                preview = str(result)[:200] + "..." if len(str(result)) > 200 else str(result)
                self.log(f"   结果预览: {preview}")
            
            self.save_result("ppt", result, parse_time)
            
        except Exception as e:
            parse_time = time.time() - start_time
            self.log(f"❌ PPT解析失败: {e}")
            self.save_error("ppt", e, parse_time)
    
    def test_image_parser(self):
        """测试图片解析器"""
        self.log("开始测试图片解析器...")
        
        if not self.vision_model:
            self.log("❌ 视觉模型不可用，跳过图片解析测试")
            return
        
        file_path = self.test_data_dir / self.test_files["jpg"]
        if not file_path.exists():
            self.log(f"❌ 图片文件不存在: {file_path}")
            return
        
        start_time = time.time()
        try:
            # 读取图片文件
            with open(file_path, 'rb') as f:
                image_data = f.read()
            
            # 使用视觉模型解析
            result = self.vision_model.describe_with_prompt(image_data)
            
            parse_time = time.time() - start_time
            self.log(f"✅ 图片解析成功，耗时: {parse_time:.2f}秒")
            
            # 显示结果预览
            preview = str(result)[:200] + "..." if len(str(result)) > 200 else str(result)
            self.log(f"   结果预览: {preview}")
            
            self.save_result("image", result, parse_time)
            
        except Exception as e:
            parse_time = time.time() - start_time
            self.log(f"❌ 图片解析失败: {e}")
            self.save_error("image", e, parse_time)
    
    def test_excel_parser_real(self):
        """测试Excel解析器（真实文件）"""
        self.log("开始测试Excel解析器（真实文件）...")
        
        file_path = self.test_data_dir / self.test_files["xlsx"]
        if not file_path.exists():
            self.log(f"❌ Excel文件不存在: {file_path}")
            return
        
        start_time = time.time()
        try:
            parser = self.parsers["excel"]
            
            # 读取文件为二进制
            with open(file_path, 'rb') as f:
                binary_content = f.read()
            
            result = parser(binary_content)
            
            parse_time = time.time() - start_time
            self.log(f"✅ Excel解析成功，耗时: {parse_time:.2f}秒")
            
            # 显示结果预览
            if isinstance(result, list):
                self.log(f"   解析出 {len(result)} 行数据")
                for i, row in enumerate(result[:3]):
                    preview = str(row)[:100] + "..." if len(str(row)) > 100 else str(row)
                    self.log(f"   行 {i}: {preview}")
            else:
                preview = str(result)[:200] + "..." if len(str(result)) > 200 else str(result)
                self.log(f"   结果预览: {preview}")
            
            self.save_result("excel", result, parse_time)
            
        except Exception as e:
            parse_time = time.time() - start_time
            self.log(f"❌ Excel解析失败: {e}")
            self.save_error("excel", e, parse_time)
    
    def generate_summary_report(self):
        """生成测试总结报告"""
        self.log("生成测试总结报告...")
        
        summary_file = self.test_results_dir / "summary.txt"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("DeepDoc 真实文件解析测试报告\n")
            f.write("=" * 50 + "\n")
            f.write(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"测试文件数量: {len(self.test_files)}\n\n")
            
            success_count = sum(1 for r in self.results.values() if r.get("success", False))
            f.write(f"成功解析: {success_count}/{len(self.results)}\n\n")
            
            f.write("详细结果:\n")
            f.write("-" * 30 + "\n")
            
            for file_type, result in self.results.items():
                f.write(f"\n{file_type.upper()}:\n")
                if result.get("success", False):
                    f.write(f"  状态: ✅ 成功\n")
                    f.write(f"  解析时间: {result.get('parse_time', 0):.2f}秒\n")
                    f.write(f"  结果长度: {result.get('result_length', 0)}字符\n")
                    f.write(f"  结果类型: {result.get('result_type', 'Unknown')}\n")
                    f.write(f"  结果文件: {result.get('result_file', 'N/A')}\n")
                else:
                    f.write(f"  状态: ❌ 失败\n")
                    f.write(f"  解析时间: {result.get('parse_time', 0):.2f}秒\n")
                    f.write(f"  错误信息: {result.get('error', 'Unknown')}\n")
                    f.write(f"  错误文件: {result.get('error_file', 'N/A')}\n")
        
        # 同时保存JSON格式的详细结果
        json_file = self.test_results_dir / "results.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        self.log(f"✅ 测试报告已保存到: {summary_file}")
        self.log(f"✅ 详细结果已保存到: {json_file}")
    
    def run_all_tests(self):
        """运行所有测试"""
        self.log("开始DeepDoc真实文件解析测试")
        self.log("=" * 50)
        
        # 运行各个解析器测试
        self.test_pdf_parser()
        self.test_docx_parser()
        self.test_ppt_parser()
        self.test_image_parser()
        self.test_excel_parser_real()
        
        # 生成总结报告
        self.generate_summary_report()
        
        self.log("=" * 50)
        self.log("测试完成！")


if __name__ == '__main__':
    # 运行测试
    tester = RealFileParserTest()
    tester.run_all_tests()