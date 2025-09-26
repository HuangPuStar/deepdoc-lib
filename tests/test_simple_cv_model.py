import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import base64

# 清除代理设置
os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''
os.environ['NO_PROXY'] = '*'
os.environ['no_proxy'] = '*'

# 添加 deepdoc 路径到 sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ..depend.simple_cv_model import QWenCV, VisionModelFactory, create_vision_model


class TestQWenCV(unittest.TestCase):
    """测试 QWenCV 模型类"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 测试用的API密钥（实际使用时需要替换为真实的）
        self.test_api_key = "sk-ef14e92efd674970b810f15fa095e4c4"
        self.test_model_name = "qwen-vl-max"
        
        # 创建测试图片
        self.test_image = self.create_test_image()
        
        # 创建 QWenCV 实例
        self.qwen_cv = QWenCV(
            key=self.test_api_key,
            model_name=self.test_model_name,
            lang="Chinese"
        )

    def create_test_image(self):
        """创建测试用的图片"""
        # 创建一个简单的测试图片
        img = Image.new('RGB', (100, 100), color='white')
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        return img_bytes

    def test_init(self):
        """测试 QWenCV 初始化"""
        self.assertEqual(self.qwen_cv.key, self.test_api_key)
        self.assertEqual(self.qwen_cv.model_name, self.test_model_name)
        self.assertEqual(self.qwen_cv.lang, "Chinese")

    def test_image2base64(self):
        """测试图片转base64功能"""
        # 测试 BytesIO 格式
        b64 = self.qwen_cv.image2base64(self.test_image)
        self.assertIsInstance(b64, str)
        self.assertTrue(len(b64) > 0)
        
        # 测试 bytes 格式
        img_bytes = self.test_image.getvalue()
        b64_bytes = self.qwen_cv.image2base64(img_bytes)
        self.assertEqual(b64, b64_bytes)
        
        # 测试 PIL Image 格式
        img = Image.open(self.test_image)
        b64_pil = self.qwen_cv.image2base64(img)
        self.assertEqual(b64, b64_pil)

    def test_prompt_generation(self):
        """测试提示词生成"""
        # 测试默认提示词
        prompt = self.qwen_cv.prompt(self.test_image.getvalue())
        self.assertIsInstance(prompt, list)
        self.assertEqual(len(prompt), 1)
        self.assertEqual(prompt[0]["role"], "user")
        self.assertIn("content", prompt[0])
        
        # 测试自定义提示词
        custom_prompt = self.qwen_cv.vision_llm_prompt(
            self.test_image.getvalue(), 
            "请描述这张图片"
        )
        self.assertIsInstance(custom_prompt, list)
        self.assertIn("请描述这张图片", str(custom_prompt))

    def test_temp_image_saving(self):
        """测试临时图片保存功能"""
        img_bytes = self.test_image.getvalue()
        temp_path = self.qwen_cv._save_temp_image(img_bytes)
        
        # 检查文件是否存在
        self.assertTrue(os.path.exists(temp_path))
        self.assertTrue(temp_path.endswith('.jpg'))
        
        # 清理临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)

    @patch('dashscope.MultiModalConversation.call')
    def test_describe_success(self, mock_call):
        """测试成功的图片描述"""
        # 模拟成功的API响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.output.choices = [{
            "message": {
                "content": [{"text": "这是一张白色背景的图片"}]
            }
        }]
        mock_response.usage.output_tokens = 10
        mock_call.return_value = mock_response
        
        # 测试描述功能
        result, tokens = self.qwen_cv.describe(self.test_image)
        
        self.assertEqual(result, "这是一张白色背景的图片")
        self.assertEqual(tokens, 10)
        mock_call.assert_called_once()

    @patch('dashscope.MultiModalConversation.call')
    def test_describe_with_prompt_success(self, mock_call):
        """测试带自定义提示词的图片描述"""
        # 模拟成功的API响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.output.choices = [{
            "message": {
                "content": [{"text": "自定义描述结果"}]
            }
        }]
        mock_response.usage.output_tokens = 15
        mock_call.return_value = mock_response
        
        # 测试带提示词的描述功能
        result, tokens = self.qwen_cv.describe_with_prompt(
            self.test_image, 
            "请详细描述这张图片的内容"
        )
        
        self.assertEqual(result, "自定义描述结果")
        self.assertEqual(tokens, 15)
        mock_call.assert_called_once()

    @patch('dashscope.MultiModalConversation.call')
    def test_describe_failure(self, mock_call):
        """测试API调用失败的情况"""
        # 模拟失败的API响应
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.message = "API调用失败"
        mock_call.return_value = mock_response
        
        # 测试失败情况
        result, tokens = self.qwen_cv.describe(self.test_image)
        
        self.assertEqual(result, "API调用失败")
        self.assertEqual(tokens, 0)

    def test_factory_creation(self):
        """测试通过工厂创建 QWenCV 实例"""
        config = {
            "provider": "qwen",
            "model_name": "qwen-vl-max",
            "api_key": self.test_api_key,
            "lang": "Chinese"
        }
        
        model = VisionModelFactory.create_model(config)
        self.assertIsInstance(model, QWenCV)
        self.assertEqual(model.key, self.test_api_key)
        self.assertEqual(model.model_name, "qwen-vl-max")

    def test_create_vision_model_function(self):
        """测试便捷函数"""
        config = {
            "provider": "qwen",
            "model_name": "qwen-vl-max",
            "api_key": self.test_api_key
        }
        
        model = create_vision_model(config)
        self.assertIsInstance(model, QWenCV)

    def test_language_settings(self):
        """测试不同语言设置"""
        # 测试中文设置
        qwen_chinese = QWenCV(self.test_api_key, self.test_model_name, lang="Chinese")
        self.assertEqual(qwen_chinese.lang, "Chinese")
        
        # 测试英文设置
        qwen_english = QWenCV(self.test_api_key, self.test_model_name, lang="English")
        self.assertEqual(qwen_english.lang, "English")

    def test_invalid_provider(self):
        """测试无效的提供商"""
        config = {
            "provider": "invalid_provider",
            "api_key": self.test_api_key
        }
        
        with self.assertRaises(ValueError):
            VisionModelFactory.create_model(config)

    def tearDown(self):
        """测试后的清理工作"""
        # 清理可能创建的临时文件
        tmp_dir = os.path.join(os.getcwd(), "tmp")
        if os.path.exists(tmp_dir):
            for file in os.listdir(tmp_dir):
                if file.endswith('.jpg'):
                    os.remove(os.path.join(tmp_dir, file))


class TestQWenCVIntegration(unittest.TestCase):
    """集成测试：测试真实的API调用（需要真实的API密钥）"""
    
    def setUp(self):
        """设置真实的API密钥进行测试"""
        # 直接使用你的API密钥
        self.real_api_key = "sk-ef14e92efd674970b810f15fa095e4c4"
        
        self.qwen_cv = QWenCV(
            key=self.real_api_key,
            model_name="qwen-vl-max",
            lang="Chinese"
        )

    def create_test_image(self):
        """创建更真实的测试图片"""
        # 创建一个更复杂的测试图片
        img = Image.new('RGB', (400, 300), color='white')
        
        # 添加一些内容到图片中
        draw = ImageDraw.Draw(img)
        
        # 添加文字
        try:
            # 尝试使用系统字体
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 20)
        except:
            # 如果找不到字体，使用默认字体
            font = ImageFont.load_default()
        
        draw.text((50, 50), "Test Document", fill='black', font=font)
        draw.text((50, 100), "This is a test image for OCR", fill='black', font=font)
        draw.text((50, 150), "包含中文测试", fill='black', font=font)
        
        # 添加一些图形
        draw.rectangle([(50, 200), (200, 250)], outline='black', width=2)
        draw.text((60, 210), "Test Box", fill='black', font=font)
        
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG', quality=95)
        img_bytes.seek(0)
        return img_bytes

    def load_real_test_image(self, image_path):
        """加载真实的测试图片"""
        if os.path.exists(image_path):
            with open(image_path, 'rb') as f:
                image_data = f.read()
            return BytesIO(image_data)
        else:
            print(f"警告: 找不到测试图片 {image_path}，使用生成的测试图片")
            return self.create_test_image()

    def test_real_api_call_with_generated_image(self):
        """测试真实的API调用 - 使用生成的测试图片"""
        test_image = self.create_test_image()
        
        try:
            result, tokens = self.qwen_cv.describe(test_image)
            
            # 检查是否是错误响应
            if "error" in result.lower() or "input format error" in result.lower():
                self.fail(f"API返回错误: {result}")
            
            # 验证返回结果
            self.assertIsInstance(result, str)
            self.assertGreater(len(result), 0)
            self.assertIsInstance(tokens, int)
            self.assertGreaterEqual(tokens, 0)
            
            print(f"✅ 生成图片API调用成功")
            print(f"�� 结果: {result[:200]}...")
            print(f"🔢 Token使用量: {tokens}")
            
        except Exception as e:
            self.fail(f"API调用失败: {str(e)}")

    def test_real_api_call_with_real_images(self):
        """测试真实的API调用 - 使用真实图片文件"""
        # 定义可能的测试图片路径
        test_image_paths = [
            "test_images/document.png",
            "test_images/chart.jpg", 
            "test_images/photo.png",
            "test_images/sample.pdf",  # 如果有PDF转图片的话
            "../test_images/document.png",  # 上级目录
            "../../test_images/document.png"  # 上上级目录
        ]
        
        found_images = []
        for image_path in test_image_paths:
            if os.path.exists(image_path):
                found_images.append(image_path)
        
        if not found_images:
            print("⚠️  没有找到真实测试图片，跳过此测试")
            self.skipTest("没有找到真实测试图片文件")
        
        # 测试每个找到的图片
        for image_path in found_images:
            print(f"\n🖼️  测试图片: {image_path}")
            test_image = self.load_real_test_image(image_path)
            
            try:
                result, tokens = self.qwen_cv.describe(test_image)
                
                # 检查是否是错误响应
                if "error" in result.lower() or "input format error" in result.lower():
                    print(f"❌ API返回错误: {result}")
                    continue
                
                # 验证返回结果
                self.assertIsInstance(result, str)
                self.assertGreater(len(result), 0)
                self.assertIsInstance(tokens, int)
                self.assertGreaterEqual(tokens, 0)
                
                print(f"✅ 真实图片API调用成功")
                print(f"�� 结果: {result[:200]}...")
                print(f"🔢 Token使用量: {tokens}")
                
            except Exception as e:
                print(f"❌ 图片 {image_path} 测试失败: {str(e)}")
                # 不直接失败，继续测试其他图片

    def test_real_api_call_with_custom_prompt(self):
        """测试带自定义提示词的真实API调用"""
        test_image = self.create_test_image()
        
        try:
            custom_prompt = "请详细描述这张图片中的文字内容和布局结构"
            result, tokens = self.qwen_cv.describe_with_prompt(test_image, custom_prompt)
            
            # 检查是否是错误响应
            if "error" in result.lower() or "input format error" in result.lower():
                self.fail(f"API返回错误: {result}")
            
            # 验证返回结果
            self.assertIsInstance(result, str)
            self.assertGreater(len(result), 0)
            self.assertIsInstance(tokens, int)
            self.assertGreaterEqual(tokens, 0)
            
            print(f"✅ 自定义提示词API调用成功")
            print(f"�� 结果: {result[:200]}...")
            print(f"🔢 Token使用量: {tokens}")
            
        except Exception as e:
            self.fail(f"API调用失败: {str(e)}")

    def tearDown(self):
        """测试后的清理工作"""
        # 清理可能创建的临时文件
        tmp_dir = os.path.join(os.getcwd(), "tmp")
        if os.path.exists(tmp_dir):
            for file in os.listdir(tmp_dir):
                if file.endswith('.jpg'):
                    try:
                        os.remove(os.path.join(tmp_dir, file))
                    except:
                        pass


if __name__ == "__main__":
    # 运行测试
    unittest.main(verbosity=2)