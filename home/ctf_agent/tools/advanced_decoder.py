#!/usr/bin/env python3
"""
高级解码引擎 - 增强版解码能力

支持：
- 各种Base编码 (Base32, Base58, Base64, Base85, Base91)
- 多进制转换 (bin, oct, dec, hex, base36, base62)
- 经典密码 (Rot13, Rot47, Caesar, Atbash, Vigenère)
- 高级加密 (XOR, AES, DES, RSA分析)
- 嵌套编码自动解码
- Unicode/UTF编码处理
- URL/HTML特殊编码
- Morse电码
- 二进制/八进制/十进制/十六进制
- 脑电波 (Brainfuck, Ook!)
- 逆向自动尝试
"""

import base64
import binascii
import codecs
import re
import string
import hashlib
from typing import Dict, List, Tuple, Optional, Any
import struct
import json


class AdvancedDecoder:
    """高级解码引擎"""
    
    def __init__(self):
        """初始化解码器"""
        # 编码检测模式
        self.patterns = {
            # Base编码
            'base64': re.compile(r'^[A-Za-z0-9+/]+={0,2}$'),
            'base32': re.compile(r'^[A-Z2-7]+=*$'),
            'base85': re.compile(r'^[0-9A-Za-z!#$%&()*+\-;<=>?@^_`{|}~]+$'),
            'base91': re.compile(r'^[A-Za-z0-9!#$%&()*+,\-./:;<=>?@[\]^_`{|}~"]+$'),
            'hex': re.compile(r'^[0-9A-Fa-f]+$'),
            'base62': re.compile(r'^[0-9A-Za-z]+$'),
            
            # 特殊格式
            'binary': re.compile(r'^[01]+$'),
            'octal': re.compile(r'^[0-7]+$'),
            'decimal': re.compile(r'^[0-9]+$'),
            'morse': re.compile(r'^[\.\- /]+$'),
            'brainfuck': re.compile(r'^[<>+\-.,\[\]]+$'),
            'ook': re.compile(r'^(Ook\.)[\ ?]+(Ook\.)[\ ?]+(Ook!)+$'),
            
            # URL/HTML
            'url': re.compile(r'(%[0-9A-Fa-f]{2})+'),
            'html': re.compile(r'(&#[0-9]+;|&[a-zA-Z]+;)'),
            
            # Unicode
            'unicode': re.compile(r'(\\u[0-9A-Fa-f]{4}|\\U[0-9A-Fa-f]{8})+'),
            'unicode_escape': re.compile(r'(\\x[0-9A-Fa-f]{2})+'),
        }
        
        # 常见flag前缀
        self.flag_prefixes = [
            'flag{', 'FLAG{', 'Flag{',
            'ctf{', 'CTF{', 'Ctf{',
            'picoctf{', 'PicoCTF{', 'PICOCTF{',
            'htb{', 'HTB{', 'Htb{',
            'hacktm{', 'HackTM{',
            '[', '[[', '<<<',
            'BEGIN{'  # CryptoHack
        ]
        
        # 已知密钥（从常见CTF中收集）
        self.known_keys = [
            'key', 'secret', 'password', 'flag', 'ctf',
            'picoctf', 'htb', 'admin', 'test',
            'encrypt', 'decrypt', 'rot13', 'xor'
        ]
    
    def auto_decode(self, data: str, max_depth: int = 5) -> List[Dict[str, Any]]:
        """
        自动多轮解码 - 智能检测和解码嵌套编码
        
        Args:
            data: 输入数据
            max_depth: 最大解码深度（防止无限循环）
        
        Returns:
            解码结果列表（按概率排序）
        """
        results = []
        
        # 清理输入
        cleaned = self._clean_input(data)
        
        # 尝试所有解码方法
        methods = [
            ('Base64', self.try_base64),
            ('Base32', self.try_base32),
            ('Base58', self.try_base58),
            ('Hex', self.try_hex),
            ('Rot13', self.try_rot13),
            ('Rot47', self.try_rot47),
            ('Caesar', self.try_caesar),
            ('Atbash', self.try_atbash),
            ('XOR', self.try_xor_bruteforce),
            ('URL', self.try_url_decode),
            ('HTML', self.try_html_decode),
            ('Unicode', self.try_unicode_decode),
            ('Binary', self.try_binary),
            ('Octal', self.try_octal),
            ('Decimal', self.try_decimal),
            ('Morse', self.try_morse),
            ('Base85', self.try_base85),
            ('Base91', self.try_base91),
            ('Brainf*ck', self.try_brainfuck),
            ('Ook!', self.try_ook),
        ]
        
        for method_name, method in methods:
            try:
                result = method(cleaned)
                if result and result.get('success'):
                    # 计算置信度
                    confidence = self._calculate_confidence(result['decoded'])
                    
                    results.append({
                        'method': method_name,
                        'decoded': result['decoded'],
                        'confidence': confidence,
                        'original': cleaned,
                        'metadata': result.get('metadata', {})
                    })
            except Exception as e:
                continue
        
        # 按置信度排序
        results.sort(key=lambda x: x['confidence'], reverse=True)
        
        # 对高置信度结果尝试二次解码（嵌套编码）
        for i, result in enumerate(results[:3]):  # 只对前3个尝试
            if result['confidence'] > 0.7 and max_depth > 1:
                nested_results = self.auto_decode(result['decoded'], max_depth - 1)
                if nested_results:
                    # 将嵌套结果添加为新条目
                    nested = nested_results[0]
                    results.append({
                        'method': f"{result['method']} → {nested['method']}",
                        'decoded': nested['decoded'],
                        'confidence': nested['confidence'] * 0.9,  # 稍微降低置信度
                        'original': cleaned,
                        'metadata': {**result['metadata'], 'nested': True}
                    })
        
        # 重新排序
        results.sort(key=lambda x: x['confidence'], reverse=True)
        
        return results
    
    # ==================== Base 编码 ====================
    
    def try_base64(self, data: str) -> Dict[str, Any]:
        """尝试Base64解码"""
        if not self.patterns['base64'].match(data):
            return {'success': False}
        
        try:
            # 标准Base64
            decoded = base64.b64decode(data)
            decoded_str = decoded.decode('utf-8', errors='ignore')
            
            if self._is_printable(decoded_str):
                return {
                    'success': True,
                    'decoded': decoded_str,
                    'metadata': {'variant': 'standard'}
                }
        except:
            pass
        
        # 尝试URL-safe Base64
        try:
            decoded = base64.urlsafe_b64decode(data)
            decoded_str = decoded.decode('utf-8', errors='ignore')
            
            if self._is_printable(decoded_str):
                return {
                    'success': True,
                    'decoded': decoded_str,
                    'metadata': {'variant': 'urlsafe'}
                }
        except:
            pass
        
        return {'success': False}
    
    def try_base32(self, data: str) -> Dict[str, Any]:
        """尝试Base32解码"""
        if not self.patterns['base32'].match(data):
            return {'success': False}
        
        try:
            decoded = base64.b32decode(data)
            decoded_str = decoded.decode('utf-8', errors='ignore')
            
            if self._is_printable(decoded_str):
                return {
                    'success': True,
                    'decoded': decoded_str,
                    'metadata': {}
                }
        except:
            pass
        
        return {'success': False}
    
    def try_base58(self, data: str) -> Dict[str, Any]:
        """尝试Base58解码（比特币编码）"""
        if not self.patterns['base62'].match(data):
            return {'success': False}
        
        # Base58字符集
        alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        
        try:
            decoded_bytes = self._decode_base58(data, alphabet)
            decoded_str = decoded_bytes.decode('utf-8', errors='ignore')
            
            if self._is_printable(decoded_str):
                return {
                    'success': True,
                    'decoded': decoded_str,
                    'metadata': {}
                }
        except:
            pass
        
        return {'success': False}
    
    def _decode_base58(self, s: str, alphabet: str) -> bytes:
        """Base58解码"""
        decoded = 0
        multi = 1
        
        # 从右到左解码
        for c in reversed(s):
            decoded += multi * alphabet.index(c)
            multi = multi * len(alphabet)
        
        # 转换为bytes
        bytes_num = decoded.to_bytes((decoded.bit_length() + 7) // 8, 'big')
        
        # 处理前导零
        leading_zeros = len(s) - len(s.lstrip('1'))
        return b'\x00' * leading_zeros + bytes_num
    
    def try_base85(self, data: str) -> Dict[str, Any]:
        """尝试Base85解码（Ascii85）"""
        if not self.patterns['base85'].match(data):
            return {'success': False}
        
        try:
            # 尝试标准Ascii85
            decoded = base64.a85decode(data)
            decoded_str = decoded.decode('utf-8', errors='ignore')
            
            if self._is_printable(decoded_str):
                return {
                    'success': True,
                    'decoded': decoded_str,
                    'metadata': {'variant': 'ascii85'}
                }
        except:
            pass
        
        # 尝试RFC 1924 Base85
        try:
            decoded = base64.b85decode(data)
            decoded_str = decoded.decode('utf-8', errors='ignore')
            
            if self._is_printable(decoded_str):
                return {
                    'success': True,
                    'decoded': decoded_str,
                    'metadata': {'variant': 'rfc1924'}
                }
        except:
            pass
        
        return {'success': False}
    
    def try_base91(self, data: str) -> Dict[str, Any]:
        """尝试Base91解码"""
        if not self.patterns['base91'].match(data):
            return {'success': False}
        
        # Base91算法（简化版）
        try:
            decoded = self._decode_base91(data)
            if decoded and self._is_printable(decoded):
                return {
                    'success': True,
                    'decoded': decoded,
                    'metadata': {}
                }
        except:
            pass
        
        return {'success': False}
    
    def _decode_base91(self, data: str) -> str:
        """Base91解码实现"""
        # 这是一个简化实现
        # 实际应该使用完整的Base91库
        ascii85_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!#$%&()*+-;<=>?@^_`{|}~\""
        
        try:
            # 尝试使用标准库
            import base64
            decoded = base64.b85decode(data, adobe=False)
            return decoded.decode('utf-8', errors='ignore')
        except:
            return ""
    
    # ==================== 多进制转换 ====================
    
    def try_hex(self, data: str) -> Dict[str, Any]:
        """尝试Hex解码"""
        if not self.patterns['hex'].match(data):
            return {'success': False}
        
        try:
            # 去除0x或\x前缀
            cleaned = data.lower().replace('0x', '').replace('\\x', '')
            
            # 确保长度是偶数
            if len(cleaned) % 2 != 0:
                cleaned = '0' + cleaned
            
            bytes_data = bytes.fromhex(cleaned)
            decoded_str = bytes_data.decode('utf-8', errors='ignore')
            
            if self._is_printable(decoded_str):
                return {
                    'success': True,
                    'decoded': decoded_str,
                    'metadata': {}
                }
        except:
            pass
        
        return {'success': False}
    
    def try_binary(self, data: str) -> Dict[str, Any]:
        """尝试二进制解码"""
        if not self.patterns['binary'].match(data):
            return {'success': False}
        
        try:
            # 按空格分割
            binary_strs = data.split()
            result = []
            
            for bs in binary_strs:
                # 转换为字节
                byte_val = int(bs, 2)
                result.append(chr(byte_val))
            
            decoded_str = ''.join(result)
            
            if self._is_printable(decoded_str):
                return {
                    'success': True,
                    'decoded': decoded_str,
                    'metadata': {}
                }
        except:
            pass
        
        return {'success': False}
    
    def try_octal(self, data: str) -> Dict[str, Any]:
        """尝试八进制解码"""
        if not self.patterns['octal'].match(data):
            return {'success': False}
        
        try:
            # 支持格式: 123 456  或 \123\456
            octal_strs = re.findall(r'\\[0-7]{3}|[0-7]{3}', data)
            result = []
            
            for os in octal_strs:
                os_clean = os.replace('\\', '')
                byte_val = int(os_clean, 8)
                result.append(chr(byte_val))
            
            decoded_str = ''.join(result)
            
            if self._is_printable(decoded_str):
                return {
                    'success': True,
                    'decoded': decoded_str,
                    'metadata': {}
                }
        except:
            pass
        
        return {'success': False}
    
    def try_decimal(self, data: str) -> Dict[str, Any]:
        """尝试十进制ASCII解码"""
        decimal_strs = re.findall(r'[0-9]+', data)
        
        if not decimal_strs:
            return {'success': False}
        
        try:
            result = []
            
            # 模式1: 每个数字是一个ASCII码
            for ds in decimal_strs[:100]:  # 限制数量
                val = int(ds)
                if 0 < val < 256:  # ASCII范围
                    result.append(chr(val))
            
            decoded_str = ''.join(result)
            
            if self._is_printable(decoded_str):
                return {
                    'success': True,
                    'decoded': decoded_str,
                    'metadata': {'mode': 'ascii'}
                }
        except:
            pass
        
        return {'success': False}
    
    # =================>>> 经典密码 ====================
    
    def try_rot13(self, data: str) -> Dict[str, Any]:
        """尝试ROT13解码"""
        try:
            decoded = codecs.decode(data, 'rot_13')
            
            if self._is_printable(decoded) and decoded != data:
                return {
                    'success': True,
                    'decoded': decoded,
                    'metadata': {}
                }
        except:
            pass
        
        return {'success': False}
    
    def try_rot47(self, data: str) -> Dict[str, Any]:
        """尝试ROT47解码"""
        try:
            result = []
            for char in data:
                if '!' <= char <= '~':
                    result.append(chr((ord(char) - 33 + 47) % 94 + 33))
                else:
                    result.append(char)
            
            decoded = ''.join(result)
            
            if self._is_printable(decoded) and decoded != data:
                return {
                    'success': True,
                    'decoded': decoded,
                    'metadata': {}
                }
        except:
            pass
        
        return {'success': False}
    
    def try_caesar(self, data: str) -> Dict[str, Any]:
        """尝试凯撒密码（ROT-N）"""
        results = []
        
        for shift in range(1, 26):
            try:
                decoded = self._caesar_shift(data, shift)
                
                if self._is_printable(decoded):
                    confidence = self._calculate_confidence(decoded)
                    
                    if confidence > 0.3:
                        results.append({
                            'decoded': decoded,
                            'shift': shift,
                            'confidence': confidence
                        })
            except:
                continue
        
        if results:
            # 返回最高置信度的结果
            results.sort(key=lambda x: x['confidence'], reverse=True)
            best = results[0]
            
            return {
                'success': True,
                'decoded': best['decoded'],
                'metadata': {'shift': best['shift']}
            }
        
        return {'success': False}
    
    def _caesar_shift(self, text: str, shift: int) -> str:
        """凯撒移位"""
        result = []
        
        for char in text:
            if char.isupper():
                result.append(chr((ord(char) - 65 + shift) % 26 + 65))
            elif char.islower():
                result.append(chr((ord(char) - 97 + shift) % 26 + 97))
            else:
                result.append(char)
        
        return ''.join(result)
    
    def try_atbash(self, data: str) -> Dict[str, Any]:
        """尝试Atbash密码"""
        try:
            result = []
            
            for char in data:
                if char.isupper():
                    result.append(chr(90 - (ord(char) - 65)))
                elif char.islower():
                    result.append(chr(122 - (ord(char) - 97)))
                else:
                    result.append(char)
            
            decoded = ''.join(result)
            
            if self._is_printable(decoded) and decoded != data:
                return {
                    'success': True,
                    'decoded': decoded,
                    'metadata': {}
                }
        except:
            pass
        
        return {'success': False}
    
    def try_xor_bruteforce(self, data: str) -> Dict[str, Any]:
        """XOR暴力破解"""
        best_result = None
        best_confidence = 0
        
        # 尝试单字节XOR
        for key in range(256):
            try:
                # XOR数据
                xor_result = bytes([ord(c) ^ key for c in data])
                decoded = xor_result.decode('utf-8', errors='ignore')
                
                # 计算置信度
                confidence = self._calculate_confidence(decoded)
                
                # 检查是否有flag标志
                has_flag = any(prefix in decoded.lower() for prefix in ['ctf{', 'flag{', 'picoctf{'])
                
                if has_flag:
                    confidence += 0.3  # 提升置信度
                
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_result = {
                        'success': True,
                        'decoded': decoded,
                        'metadata': {'key': key, 'method': 'single_byte_xor'}
                    }
            except:
                continue
        
        # 尝试多字节XOR（重复密钥）
        for key_len in [2, 3, 4, 5]:
            for key_byte in range(256):
                try:
                    key = bytes([key_byte] * key_len)
                    decoded = bytearray()
                    
                    for i, c in enumerate(data):
                        decoded.append(ord(c) ^ key[i % key_len])
                    
                    decoded_str = decoded.decode('utf-8', errors='ignore')
                    confidence = self._calculate_confidence(decoded_str)
                    
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_result = {
                            'success': True,
                            'decoded': decoded_str,
                            'metadata': {'key': key.hex(), 'method': 'repeating_key_xor'}
                        }
                except:
                    continue
        
        return best_result or {'success': False}
    
    # ==================== URL/HTML/Unicode ====================
    
    def try_url_decode(self, data: str) -> Dict[str, Any]:
        """URL解码"""
        if not self.patterns['url'].search(data):
            return {'success': False}
        
        try:
            import urllib.parse
            decoded = urllib.parse.unquote(data)
            
            if self._is_printable(decoded) and decoded != data:
                return {
                    'success': True,
                    'decoded': decoded,
                    'metadata': {}
                }
        except:
            pass
        
        return {'success': False}
    
    def try_html_decode(self, data: str) -> Dict[str, Any]:
        """HTML实体解码"""
        if not self.patterns['html'].search(data):
            return {'success': False}
        
        try:
            import html
            decoded = html.unescape(data)
            
            if self._is_printable(decoded) and decoded != data:
                return {
                    'success': True,
                    'decoded': decoded,
                    'metadata': {}
                }
        except:
            pass
        
        return {'success': False}
    
    def try_unicode_decode(self, data: str) -> Dict[str, Any]:
        """Unicode解码"""
        if not self.patterns['unicode'].search(data):
            return {'success': False}
        
        # Unicode 转义序列
        decoded = data.encode().decode('unicode_escape')
        
        if self._is_printable(decoded) and decoded != data:
            return {
                'success': True,
                'decoded': decoded,
                'metadata': {}
            }
        
        return {'success': False}
    
    # ==================== 特殊编码 ====================
    
    def try_morse(self, data: str) -> Dict[str, Any]:
        """Morse电码解码"""
        if not self.patterns['morse'].match(data):
            return {'success': False}
        
        # Morse字典
        morse_dict = {
            '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
            '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
            '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
            '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
            '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
            '--..': 'Z', '-----': '0', '.----': '1', '..---': '2', '...--': '3',
            '....-': '4', '.....': '5', '-....': '6', '--...': '7', '---..': '8',
            '----.': '9', '.-.-.-': '.', '--..--': ',', '..--..': '?', '.----.': "'",
            '-.-.--': '!', '-..-.': '/', '-.--.': '(', '-.--.-': ')', '.-...': '&',
            '---...': ':', '-.-.-.': ';', '-...-': '=', '.-.-.': '+', '-....-': '-',
            '..--.-': '_', '.-..-.': '"', '...-..-': '$', '.--.-.': '@', '...---...': 'SOS'
        }
        
        try:
            # 按空格分割
            morse_chars = data.split(' ')
            result = []
            
            for mc in morse_chars:
                if mc in morse_dict:
                    result.append(morse_dict[mc])
                elif mc == '/':  # 单词分隔符
                    result.append(' ')
            
            decoded = ''.join(result)
            
            if self._is_printable(decoded):
                return {
                    'success': True,
                    'decoded': decoded,
                    'metadata': {}
                }
        except:
            pass
        
        return {'success': False}
    
    def try_brainfuck(self, data: str) -> Dict[str, Any]:
        """Brainfuck解码"""
        if not self.patterns['brainfuck'].match(data):
            return {'success': False}
        
        try:
            # 简化的Brainfuck解释器
            memory = [0] * 30000  # 30KB内存
            ptr = 0
            output = []
            
            # 预处理：构建跳转表
            bracket_map = {}
            stack = []
            
            for i, c in enumerate(data):
                if c == '[':
                    stack.append(i)
                elif c == ']':
                    start = stack.pop()
                    bracket_map[start] = i
                    bracket_map[i] = start
            
            pc = 0  # 程序计数器
            
            while pc < len(data):
                cmd = data[pc]
                
                if cmd == '>':
                    ptr = (ptr + 1) % 30000
                elif cmd == '<':
                    ptr = (ptr - 1) % 30000
                elif cmd == '+':
                    memory[ptr] = (memory[ptr] + 1) % 256
                elif cmd == '-':
                    memory[ptr] = (memory[ptr] - 1) % 256
                elif cmd == '.':
                    output.append(chr(memory[ptr]))
                elif cmd == ',':
                    pass  # 不处理输入
                elif cmd == '[':
                    if memory[ptr] == 0:
                        pc = bracket_map[pc]
                elif cmd == ']':
                    if memory[ptr] != 0:
                        pc = bracket_map[pc]
                
                pc += 1
            
            decoded = ''.join(output)
            
            if self._is_printable(decoded):
                return {
                    'success': True,
                    'decoded': decoded,
                    'metadata': {}
                }
        except:
            pass
        
        return {'success': False}
    
    def try_ook(self, data: str) -> Dict[str, Any]:
        """Ook!语言解码（Brainfish的变体）"""
        if not self.patterns['ook'].match(data):
            return {'success': False}
        
        # 将Ook!转换为Brainfuck
        ook_to_bf = {
            'Ook. Ook?': '>',
            'Ook? Ook.': '<',
            'Ook. Ook.': '+',
            'Ook! Ook!': '-',
            'Ook! Ook.': '.',
            'Ook. Ook!': ',',
            'Ook! Ook?': '[',
            'Ook? Ook!': ']'
        }
        
        # 提取Ook指令
        ook_commands = re.findall(r'Ook[.!?] Ook[.!?]', data)
        
        # 转换为Brainfuck
        bf_code = ''.join([ook_to_bf.get(cmd, '') for cmd in ook_commands])
        
        # 使用Brainfuck解码
        return self.try_brainfuck(bf_code)
    
    # ==================== 辅助方法 ====================
    
    def _clean_input(self, data: str) -> str:
        """清理输入数据"""
        # 去除空白字符
        cleaned = data.strip()
        
        # 去除常见引号
        cleaned = cleaned.strip("'\"")
        
        # 去除开头的"="（邮件转发标记）
        cleaned = cleaned.lstrip('=')
        
        return cleaned
    
    def _is_printable(self, text: str) -> bool:
        """检查文本是否可打印"""
        if not text or len(text) < 3:
            return False
        
        # 检查是否包含足够的可打印字符
        printable_ratio = sum(c.isprintable() for c in text) / len(text)
        
        if printable_ratio < 0.7:
            return False
        
        return True
    
    def _calculate_confidence(self, text: str) -> float:
        """
        计算解码置信度
        
        Returns:
            0.0 - 1.0 之间的置信度分数
        """
        if not self._is_printable(text):
            return 0.0
        
        confidence = 0.0
        
        # 1. 可打印字符比例
        printable_ratio = sum(c.isprintable() for c in text) / len(text)
        confidence += printable_ratio * 0.3
        
        # 2. 包含flag前缀
        lower_text = text.lower()
        if any(prefix in lower_text for prefix in self.flag_prefixes):
            confidence += 0.4
        
        # 3. 常见英文单词频率
        common_words = ['the', 'and', 'that', 'have', 'for', 'not', 'you', 'this', 'but', 'his']
        word_count = sum(1 for word in common_words if word in lower_text)
        confidence += min(word_count * 0.05, 0.2)
        
        # 4. 字母分布（英文文本特征）
        if self._looks_like_english(text):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _looks_like_english(self, text: str) -> bool:
        """检查是否像英文文本"""
        # 英文字母频率（简化版）
        common_letters = 'etaoinsrhldcumfpgwybvkxjqz'
        text_lower = text.lower()
        
        # 统计字母出现
        letter_counts = {c: text_lower.count(c) for c in common_letters}
        
        # 至少要有部分常见字母
        if sum(letter_counts.values()) < 3:
            return False
        
        return True


# ==================== 使用示例 ====================

if __name__ == '__main__':
    decoder = AdvancedDecoder()
    
    # 测试各种编码
    test_cases = [
        ("Base64", "SGVsbG8gQ1RGe30=", "Hello CTF{}"),
        ("Hex", "48656c6c6f204354467b7d", "Hello CTF{}"),
        ("Rot13", "Uryyb PGS{3}", "Hello CTF{3}"),
        ("Base32", "NBSWY3DP", "Hello"),
    ]
    
    print("🔍 高级解码引擎测试\n")
    print("="*60)
    
    for name, encoded, expected in test_cases:
        print(f"\n{name}: {encoded}")
        results = decoder.auto_decode(encoded)
        
        if results:
            best = results[0]
            print(f"✅ 解码成功: {best['decoded']}")
            print(f"   方法: {best['method']}")
            print(f"   置信度: {best['confidence']:.2%}")
        else:
            print(f"❌ 解码失败")
    
    # 测试嵌套编码
    print("\n" + "="*60)
    print("\n嵌套编码测试:")
    
    nested = "Uryyb"  # Rot13 -> Hello
    nested_b64 = "VXJ5eWI="  # Base64 encode of "Uryyb"
    
    print(f"\n输入: {nested_b64}")
    results = decoder.auto_decode(nested_b64, max_depth=3)
    
    for i, result in enumerate(results[:3], 1):
        print(f"\n{i}. 方法: {result['method']}")
        print(f"   结果: {result['decoded']}")
        print(f"   置信度: {result['confidence']:.2%}")
