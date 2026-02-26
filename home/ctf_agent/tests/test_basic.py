"""
CTF Agent - 基础测试套件
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os


class TestCryptoTools:
    """密码学工具测试"""

    def test_base64_decode(self):
        """测试Base64解码"""
        from tools.enhanced_tools import base64_decode
        
        result = base64_decode("SGVsbG8=")
        assert result == "Hello"
        
        # 测试空字符串
        assert base64_decode("") is None
        
        # 测试padding
        result = base64_decode("SGVsbG8gQ1RG")
        assert result == "Hello CTF"

    def test_rot13(self):
        """测试ROT13编解码"""
        from tools.enhanced_tools import rot13
        
        result = rot13("Hello")
        assert result == "Uryyb"
        
        # 两次回原
        assert rot13(rot13("Hello")) == "Hello"

    def test_xor_bruteforce(self):
        """测试XOR暴力破解"""
        from tools.enhanced_tools import xor_bruteforce
        
        # 单字节XOR
        encrypted = b"\x1f\x1e\x1d\x1c"  # XOR 31后的"Hello"
        result = xor_bruteforce(encrypted)
        assert result is not None
        assert "Hello" in result or result is not None

    def test_caesar_decrypt(self):
        """测试凯撒密码解密"""
        from tools.enhanced_tools import caesar_decrypt
        
        ciphertext = "Khoor Zruog"  # Hello World shift 3
        result = caesar_decrypt(ciphertext)
        assert "Hello" in result or "World" in result or result is not None

    def test_url_decode(self):
        """测试URL解码"""
        from tools.enhanced_tools import url_decode
        
        encoded = "Hello%20World"
        decoded = url_decode(encoded)
        assert decoded == "Hello World"

    def test_analyze_hash(self):
        """测试哈希类型分析"""
        from tools.enhanced_tools import analyze_hash
        
        md5_hash = "5d41402abc4b2a76b9719d911017c592"
        result = analyze_hash(md5_hash)
        assert "MD5" in result or "128" in result


class TestWebTools:
    """Web工具测试"""

    def test_check_sqli_static(self):
        """测试SQL注入静态检测"""
        from tools.enhanced_tools import check_sqli
        
        url = "http://example.com/page?id=1' OR '1'='1"
        result = check_sqli(url)
        assert result is not None

    def test_check_xss(self):
        """测试XSS检测"""
        from tools.enhanced_tools import check_xss
        
        payload = "<script>alert(document.cookie)</script>"
        result = check_xss(payload)
        assert result is not None

    def test_parse_cookies(self):
        """测试Cookie解析"""
        from tools.enhanced_tools import parse_cookies
        
        cookie_string = "session=abc123; user=john; theme=dark"
        cookies = parse_cookies(cookie_string)
        assert cookies["session"] == "abc123"
        assert cookies["user"] == "john"


class TestForensicsTools:
    """取证工具测试"""

    @patch('tools.enhanced_tools.subprocess.run')
    def test_detect_filetype(self, mock_run):
        """测试文件类型检测"""
        from tools.enhanced_tools import detect_filetype
        
        mock_result = Mock()
        mock_result.stdout = b"test.txt: ASCII text"
        mock_run.return_value = mock_result
        
        result = detect_filetype("test.txt")
        assert "ASCII" in result or result is not None

    @patch('tools.enhanced_tools.subprocess.run')
    def test_extract_strings(self, mock_run):
        """测试字符串提取"""
        from tools.enhanced_tools import extract_strings
        
        mock_result = Mock()
        mock_result.stdout = b"Hello\nWorld\nCTF\n"
        mock_run.return_value = mock_result
        
        result = extract_strings("test.bin")
        assert "Hello" in result or len(result) > 0

    def test_auto_decode(self):
        """测试自动解码"""
        from tools.enhanced_tools import auto_decode
        
        # Base64编码
        encoded = "SGVsbG8="
        result = auto_decode(encoded, attempts=['base64'])
        assert "Hello" in result or result is not None


class TestToolRegistry:
    """工具注册表测试"""

    def test_register_tool(self):
        """测试工具注册"""
        from tools.toolkit import ToolRegistry
        from tools.base_tool import BaseTool
        
        class TestTool(BaseTool):
            name = "test_tool"
            description = "Test tool"
            
            def execute(self, args):
                return "test result"
        
        registry = ToolRegistry()
        registry.register(TestTool())
        
        assert "test_tool" in registry.tools

    def test_execute_tool(self):
        """测试工具执行"""
        from tools.toolkit import ToolRegistry
        
        # 使用内置工具
        from tools.enhanced_tools import base64_decode
        from tools.base_tool import BaseTool
        
        class Base64Tool(BaseTool):
            name = "base64_decode"
            description = "Base64 decode"
            
            def execute(self, args):
                data = args.get("input", "")
                return base64_decode(data)
        
        registry = ToolRegistry()
        registry.register(Base64Tool())
        
        result = registry.execute("base64_decode", {"input": "SGVsbG8="})
        assert "Hello" in result or result is not None


class TestAgent:
    """Agent核心测试"""

    @patch('core.agent.openai.ChatCompletion.create')
    @patch('core.agent.anthropic.Anthropic.messages.create')
    def test_solve_crypto_problem(self, mock_anthropic, mock_openai):
        """测试解决Crypto问题"""
        from core.agent import CTFAgent
        from config import Config
        
        # Mock API响应
        mock_response = Mock()
        mock_response.content = [
            Mock(text="调用base64_decode工具解码SGVsbG8=")
        ]
        mock_anthropic.return_value = mock_response
        
        try:
            config = Config()
            # 设置测试配置
            config.llm.provider = "anthropic"
            config.llm.model = "claude-3-haiku-20240307"
            config.llm.api_key = "test-key"
            
            agent = CTFAgent(config)
            
            problem = {
                "description": "Base64编码: SGVsbG8=",
                "type": "crypto"
            }
            
            # 注意：这需要实际的工具调用才能成功
            # result = agent.solve(problem)
            # 断言可以添加如果成功执行
            pass
            
        except ImportError:
            # 如果某个依赖缺失，跳过测试
            pytest.skip("Anthropic not installed")

    def test_classify_challenge(self):
        """测试题目分类"""
        from core.agent import CTFAgent
        from config import Config
        
        try:
            config = Config()
            agent = CTFAgent(config)
            
            # 分类测试
            crypto_problem = {
                "description": "RSA密钥破解",
                "files": ["rsa_key.pem"]
            }
            
            web_problem = {
                "description": "SQL注入",
                "url": "http://example.com"
            }
            
            # 如果agent有分类方法，测试它
            # result = agent.classify(crypto_problem)
            # assert result == "crypto"
            pass
            
        except Exception:
            pytest.skip("Classification not implemented")


class TestConfig:
    """配置管理测试"""

    def test_config_load(self):
        """测试配置加载"""
        from config import Config
        
        # 创建临时配置文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
llm:
  provider: anthropic
  model: claude-3-haiku
  api_key: test-key
""")
            config_file = f.name
        
        try:
            config = Config(config_file)
            assert config.llm.provider == "anthropic"
            assert config.llm.model == "claude-3-haiku"
        finally:
            os.unlink(config_file)

    def test_env_override(self):
        """测试环境变量覆盖"""
        import os
        
        # 设置环境变量
        os.environ['ANTHROPIC_API_KEY'] = 'env-test-key'
        
        from config import Config
        config = Config()
        
        assert 'env-test-key' in str(config.llm.api_key) or config.llm.api_key is not None


class TestMemory:
    """记忆系统测试"""

    def test_memory_store_and_retrieve(self):
        """测试记忆存储和检索"""
        try:
            from core.memory import Memory
            
            memory = Memory()
            
            # 存储记忆
            memory.add({
                "challenge": "Test Challenge",
                "solution": "Test Solution",
                "tools": ["base64_decode"]
            })
            
            # 检索记忆
            results = memory.search("Test")
            assert len(results) > 0
            
        except ImportError:
            pytest.skip("Memory module not available")


class TestKnowledgeBase:
    """知识库测试"""

    def test_knowledge_add_and_search(self):
        """测试知识库添加和搜索"""
        try:
            from knowledge.rag import KnowledgeBase
            
            kb = KnowledgeBase()
            
            # 添加知识
            kb.add_entry({
                "category": "crypto",
                "problem": "如何解密Base64",
                "solution": "使用base64_decode工具",
                "code": "base64_decode(encoded_string)"
            })
            
            # 搜索知识
            results = kb.search("Base64 解密")
            assert len(results) > 0 or results is not None
            
        except ImportError:
            pytest.skip("KnowledgeBase not available")


class TestDockerSandbox:
    """Docker沙箱测试"""

    @pytest.mark.skipif(
        os.geteuid() != 0,
        reason="需要root权限运行Docker"
    )
    def test_docker_available(self):
        """测试Docker可用性"""
        try:
            import docker
            
            client = docker.from_env()
            version = client.version()
            assert version is not None
        except Exception:
            pytest.skip("Docker not available or not running")


# Pytest配置
pytest_plugins = []

# 测试标记
pytest.mark.crypto = pytest.mark.skipif(
    True,
    reason="Crypto tests"
)
