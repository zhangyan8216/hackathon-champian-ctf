#!/usr/bin/env python3
"""
向量化知识检索系统 - 增强知识库管理

功能：
- 文本向量化（使用多种Embedding模型）
- 语义相似度搜索
- 混合检索（关键词+语义）
- 知识聚类和去重
- 自动知识更新
- 离线索引构建
- 增量索引更新
- 相关性评分
"""

import json
import hashlib
import pickle
import time
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from collections import defaultdict
import re


class TextVectorizer:
    """文本向量化器"""
    
    def __init__(self, method: str = 'tfidf'):
        """
        初始化向量化器
        
        Args:
            method: 向量化方法 ('tfidf', 'hash', 'co-occurrence', 'keyword')
        """
        self.method = method
        self.vocabulary = {}
        self.idf = {}
        self.document_count = 0
    
    def train(self, documents: List[str]):
        """
        训练向量化器
        
        Args:
            documents: 文档列表
        """
        self.document_count = len(documents)
        
        # 构建词表
        word_doc_count = defaultdict(int)
        
        for doc in documents:
            words = self._tokenize(doc)
            unique_words = set(words)
            
            for word in unique_words:
                self.vocabulary[word] = self.vocabulary.get(word, 0) + word_doc_count[word] + 1
                word_doc_count[word] += 1
        
        # 计算IDF
        for word, doc_count in word_doc_count.items():
            self.idf[word] = self._calculate_idf(doc_count, self.document_count)
    
    def vectorize(self, text: str) -> Dict[str, float]:
        """
        将文本转换为向量
        
        Args:
            text: 输入文本
        
        Returns:
            向量字典 {word: weight}
        """
        if self.method == 'tfidf':
            return self._tfidf_vectorize(text)
        elif self.method == 'hash':
            return self._hash_vectorize(text)
        elif self.method == 'co-occurrence':
            return self._cooccurrence_vectorize(text)
        else:  # keyword
            return self._keyword_vectorize(text)
    
    def _tokenize(self, text: str) -> List[str]:
        """分词"""
        # 小写化
        text = text.lower()
        
        # 提取单词
        words = re.findall(r'\b\w+\b', text)
        
        # 过滤停用词
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
            'can', 'could', 'may', 'might', 'must', 'shall', 'this', 'that', 'these',
            'those', 'a', 'an', 'it', 'its', 'they', 'them', 'their', 'you', 'your'
        }
        
        words = [w for w in words if w not in stop_words and len(w) > 2]
        
        # 词干提取（简化版）
        words = [self._stem(w) for w in words]
        
        return words
    
    def _stem(self, word: str) -> str:
        """简化词干提取"""
        # 简单规则：去除常见后缀
        suffixes = ['ing', 'ly', 'ed', 'ies', 'es', 's']
        
        for suffix in suffixes:
            if word.endswith(suffix) and len(word) > len(suffix) + 2:
                return word[:-len(suffix)]
        
        return word
    
    def _calculate_tf(self, word: str, document: str) -> float:
        """计算词频（TF）"""
        words = self._tokenize(document)
        word_count = words.count(word)
        return word_count / len(words)
    
    def _calculate_idf(self, doc_count: int, total_docs: int) -> float:
        """计算逆文档频率（IDF）"""
        import math
        return math.log(total_docs / (doc_count + 1)) + 1
    
    def _tfidf_vectorize(self, text: str) -> Dict[str, float]:
        """TF-IDF向量化"""
        words = self._tokenize(text)
        vector = {}
        
        # 计算每个词的TF-IDF
        unique_words = set(words)
        
        for word in unique_words:
            tf = self._calculate_tf(word, text)
            idf = self.idf.get(word, 1.0)
            tfidf = tf * idf
            
            vector[word] = tfidf
        
        return vector
    
    def _hash_vectorize(self, text: str, n_buckets: int = 1024) -> Dict[str, float]:
        """Hash向量化（简化版SimHash）"""
        words = self._tokenize(text)
        vector = {}
        
        for word in words:
            # 计算word的hash
            hash_value = int(hashlib.md5(word.encode()).hexdigest(), 16)
            
            # 映射到bucket
            bucket = hash_value % n_buckets
            vector[f'bucket_{bucket}'] = vector.get(f'bucket_{bucket}', 0) + 1
        
        # 归一化
        total = sum(vector.values())
        if total > 0:
            vector = {k: v / total for k, v in vector.items()}
        
        return vector
    
    def _cooccurrence_vectorize(self, text: str, window: int = 2) -> Dict[str, float]:
        """共现向量化"""
        words = self._tokenize(text)
        vector = {}
        
        # 统计共现词对
        for i in range(len(words)):
            for j in range(i + 1, min(i + window + 1, len(words))):
                word1 = words[i]
                word2 = words[j]
                
                pair = f'{word1}_{word2}'
                vector[pair] = vector.get(pair, 0) + 1
        
        # 归一化
        total = sum(vector.values())
        if total > 0:
            vector = {k: v / total for k, v in vector.items()}
        
        return vector
    
    def _keyword_vectorize(self, text: str) -> Dict[str, float]:
        """关键词向量化（TF简化版）"""
        words = self._tokenize(text)
        vector = {}
        
        # 词频
        word_counts = defaultdict(int)
        for word in words:
            word_counts[word] += 1
        
        # 按词频排序，取前20个
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:20]
        
        # 归一化权重
        total = sum(count for _, count in sorted_words)
        for word, count in sorted_words:
            vector[word] = count / total
        
        return vector


class SimilarityCalculator:
    """相似度计算器"""
    
    @staticmethod
    def cosine_similarity(vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """
        计算余弦相似度
        
        Args:
            vec1: 向量1
            vec2: 向量2
        
        Returns:
            相似度分数 (0-1)
        """
        # 获取共同的keys
        common_keys = set(vec1.keys()) & set(vec2.keys())
        
        if not common_keys:
            return 0.0
        
        # 计算点积
        dot_product = sum(vec1[k] * vec2[k] for k in common_keys)
        
        # 计算向量长度
        norm1 = (sum(v ** 2 for v in vec1.values())) ** 0.5
        norm2 = (sum(v ** 2 for v in vec2.values())) ** 0.5
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        return max(0.0, min(1.0, similarity))
    
    @staticmethod
    def jaccard_similarity(vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """
        计算Jaccard相似度
        
        Args:
            vec1: 向量1
            vec2: 向量2
        
        Returns:
            相似度分数 (0-1)
        """
        keys1 = set(vec1.keys())
        keys2 = set(vec2.keys())
        
        intersection = keys1 & keys2
        union = keys1 | keys2
        
        if not union:
            return 0.0
        
        return len(intersection) / len(union)
    
    @staticmethod
    def euclidean_distance(vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """
        计算欧几里得距离
        
        Args:
            vec1: 向量1
            vec2: 向量2
        
        Returns:
            距离（越小越相似）
        """
        all_keys = set(vec1.keys()) | set(vec2.keys())
        
        distance = 0.0
        for key in all_keys:
            v1 = vec1.get(key, 0)
            v2 = vec2.get(key, 0)
            distance += (v2 - v1) ** 2
        
        return distance ** 0.5


class VectorKnowledgeBase:
    """向量化知识库"""
    
    def __init__(self, storage_path: str = None, vectorizer_method: str = 'tfidf'):
        """
        初始化知识库
        
        Args:
            storage_path: 存储路径
            vectorizer_method: 向量化方法
        """
        self.storage_path = storage_path or 'memory/vector_kb'
        self.vectorizer = TextVectorizer(method=vectorizer_method)
        self.similarity_calc = SimilarityCalculator()
        
        # 知识库
        self.documents = {}  # {doc_id: document}
        self.vectors = {}    # {doc_id: vector}
        self.metadata = {}   # {doc_id: metadata}
        
        # 索引
        self.inverse_index = defaultdict(list)  # {word: [doc_ids]}
        
        # 统计
        self.stats = {
            'total_docs': 0,
            'avg_vector_size': 0,
            'last_updated': time.time()
        }
        
        # 加载已有知识
        self._load()
    
    def _load(self):
        """加载知识库"""
        try:
            base_path = Path(self.storage_path)
            
            # 加载文档
            docs_path = base_path / 'documents.pkl'
            if docs_path.exists():
                with open(docs_path, 'rb') as f:
                    self.documents = pickle.load(f)
            
            # 加载向量
            vectors_path = base_path / 'vectors.pkl'
            if vectors_path.exists():
                with open(vectors_path, 'rb') as f:
                    self.vectors = pickle.load(f)
            
            # 加载元数据
            metadata_path = base_path / 'metadata.pkl'
            if metadata_path.exists():
                with open(metadata_path, 'rb') as f:
                    self.metadata = pickle.load(f)
            
            # 更新统计
            self.stats['total_docs'] = len(self.documents)
            self.stats['last_updated'] = base_path.stat().st_mtime if base_path.exists() else time.time()
            
            print(f"  加载了 {len(self.documents)} 篇文档")
            
        except Exception as e:
            print(f"  加载知识库失败: {e}")
    
    def _save(self):
        """保存知识库"""
        try:
            base_path = Path(self.storage_path)
            base_path.mkdir(parents=True, exist_ok=True)
            
            # 保存文档
            with open(base_path / 'documents.pkl', 'wb') as f:
                pickle.dump(self.documents, f)
            
            # 保存向量
            with open(base_path / 'vectors.pkl', 'wb') as f:
                pickle.dump(self.vectors, f)
            
            # 保存元数据
            with open(base_path / 'metadata.pkl', 'wb') as f:
                pickle.dump(self.metadata, f)
            
            self.stats['last_updated'] = time.time()
            
        except Exception as e:
            print(f"  保存知识库失败: {e}")
    
    def add_document(self, doc_id: str, text: str, metadata: Dict = None):
        """
        添加文档到知识库
        
        Args:
            doc_id: 文档ID
            text: 文档文本
            metadata: 元数据
        """
        # 清理文本
        cleaned_text = self._clean_text(text)
        
        # 向量化
        vector = self.vectorizer.vectorize(cleaned_text)
        
        # 存储
        self.documents[doc_id] = cleaned_text
        self.vectors[doc_id] = vector
        self.metadata[doc_id] = metadata or {}
        
        # 更新倒排索引
        words = self.vectorizer._tokenize(cleaned_text)
        for word in words:
            if doc_id not in self.inverse_index[word]:
                self.inverse_index[word].append(doc_id)
        
        # 更新统计
        self.stats['total_docs'] += 1
        
        # 增量更新IDF（简化版：重新训练）
        self._retrain_vectorizer()
    
    def _retrain_vectorizer(self):
        """重新训练向量化器"""
        all_texts = list(self.documents.values())
        self.vectorizer.train(all_texts)
        
        # 重新向量化所有文档
        for doc_id, text in self.documents.items():
            self.vectors[doc_id] = self.vectorizer.vectorize(text)
    
    def _clean_text(self, text: str) -> str:
        """清理文本"""
        # 去除HTML标签
        text = re.sub(r'<[^>]+>', ' ', text)
        
        # 去除多余空白
        text = re.sub(r'\s+', ' ', text)
        
        # 去除特殊字符（保留基本标点）
        text = re.sub(r'[^a-zA-Z0-9\s\.\,\!\?\-\_]', ' ', text)
        
        return text.strip()
    
    def search(self, query: str, top_k: int = 10, 
              similarity_threshold: float = 0.1) -> List[Dict[str, Any]]:
        """
        语义搜索
        
        Args:
            query: 查询文本
            top_k: 返回前k个结果
            similarity_threshold: 相似度阈值
        
        Returns:
            搜索结果列表
        """
        # 向量化查询
        query_vec = self.vectorizer.vectorize(query)
        
        # 计算相似度
        results = []
        
        for doc_id, doc_vec in self.vectors.items():
            # 计算余弦相似度
            similarity = self.similarity_calc.cosine_similarity(query_vec, doc_vec)
            
            if similarity >= similarity_threshold:
                results.append({
                    'doc_id': doc_id,
                    'similarity': similarity,
                    'text': self.documents[doc_id],
                    'metadata': self.metadata[doc_id]
                })
        
        # 按相似度排序
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        return results[:top_k]
    
    def hybrid_search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        混合搜索（关键词+语义）
        
        Args:
            query: 查询文本
            top_k: 返回前k个结果
        
        Returns:
            搜索结果列表
        """
        # 关键词搜索
        keywords = self.vectorizer._tokenize(query)
        keyword_scores = defaultdict(float)
        
        for keyword in keywords:
            for doc_id in self.inverse_index.get(keyword, []):
                keyword_scores[doc_id] += 1
        
        # 语义搜索
        semantic_results = self.search(query, top_k=top_k * 2)
        
        # 合并分数
        combined_results = []
        
        for result in semantic_results:
            doc_id = result['doc_id']
            semantic_score = result['similarity']
            keyword_score = keyword_scores.get(doc_id, 0)
            
            # 加权组合（70%语义 + 30%关键词）
            combined_score = semantic_score * 0.7 + min(keyword_score / 10, 0.3)
            
            combined_results.append({
                **result,
                'combined_score': combined_score,
                'keyword_score': keyword_score
            })
        
        # 按组合分数排序
        combined_results.sort(key=lambda x: x['combined_score'], reverse=True)
        
        return combined_results[:top_k]
    
    def find_similar(self, doc_id: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        找到相似的文档
        
        Args:
            doc_id: 参考文档ID
            top_k: 返回前k个结果
        
        Returns:
            相似文档列表
        """
        if doc_id not in self.vectors:
            return []
        
        query_vec = self.vectors[doc_id]
        
        results = []
        
        for other_id, other_vec in self.vectors.items():
            if other_id == doc_id:
                continue
            
            similarity = self.similarity_calc.cosine_similarity(query_vec, other_vec)
            
            results.append({
                'doc_id': other_id,
                'similarity': similarity,
                'text': self.documents[other_id],
                'metadata': self.metadata[other_id]
            })
        
        # 按相似度排序
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        return results[:top_k]
    
    def cluster_documents(self, n_clusters: int = 5) -> Dict[str, List[str]]:
        """
        文档聚类（简化版K-Means）
        
        Args:
            n_clusters: 聚类数量
        
        Returns:
            聚类结果 {cluster_id: [doc_ids]}
        """
        import random
        
        doc_ids = list(self.vectors.keys())
        if len(doc_ids) < n_clusters:
            return {f'cluster_{i}': [] for i in range(n_clusters)}
        
        # 随机初始化聚类中心
        centers = []
        for _ in range(n_clusters):
            center_id = random.choice(doc_ids)
            centers.append(self.vectors[center_id])
        
        # 简化的K-Means（只进行10次迭代）
        clusters = defaultdict(list)
        
        for iteration in range(10):
            clusters.clear()
            
            # 分配文档到最近的聚类
            for doc_id in doc_ids:
                doc_vec = self.vectors[doc_id]
                
                similarities = [
                    self.similarity_calc.cosine_similarity(doc_vec, center)
                    for center in centers
                ]
                
                best_cluster = similarities.index(max(similarities))
                clusters[f'cluster_{best_cluster}'].append(doc_id)
            
            # 更新聚类中心
            new_centers = []
            for cluster_id, cluster_docs in clusters.items():
                if not cluster_docs:
                    continue
                
                # 计算平均向量
                avg_vector = defaultdict(float)
                for doc_id in cluster_docs:
                    doc_vec = self.vectors[doc_id]
                    for word, weight in doc_vec.items():
                        avg_vector[word] += weight
                
                # 归一化
                total = sum(avg_vector.values())
                avg_vector = {k: v / total for k, v in avg_vector.items()}
                new_centers.append(avg_vector)
            
            centers = new_centers
        
        return dict(clusters)
    
    def deduplicate(self, similarity_threshold: float = 0.95) -> List[str]:
        """
        去重非常相似的文档
        
        Args:
            similarity_threshold: 相似度阈值
        
        Returns:
            重复的文档ID列表
        """
        duplicates = []
        checked = set()
        
        for doc_id1, vec1 in self.vectors.items():
            if doc_id1 in checked:
                continue
            
            for doc_id2, vec2 in self.vectors.items():
                if doc_id1 == doc_id2 or doc_id2 in checked:
                    continue
                
                similarity = self.similarity_calc.cosine_similarity(vec1, vec2)
                
                if similarity >= similarity_threshold:
                    duplicates.append(doc_id2)
                    checked.add(doc_id2)
            
            checked.add(doc_id1)
        
        return duplicates
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        avg_vec_size = sum(len(v) for v in self.vectors.values()) / len(self.vectors) if self.vectors else 0
        
        return {
            'total_documents': len(self.documents),
            'total_vectors': len(self.vectors),
            'average_vector_size': avg_vec_size,
            'vocabulary_size': len(self.vectorizer.vocabulary),
            'last_updated': self.stats['last_updated']
        }
    
    def export(self, filepath: str):
        """导出知识库为JSON"""
        export_data = {
            'documents': self.documents,
            'metadata': self.metadata,
            'stats': self.get_stats(),
            'export_time': time.time()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
    
    def import_from_json(self, filepath: str):
        """从JSON导入知识库"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for doc_id, text in data['documents'].items():
            self.add_document(doc_id, text, data['metadata'].get(doc_id))


# 使用示例
if __name__ == '__main__':
    print("📊 向量化知识检索系统\n")
    print("="*60)
    
    # 创建知识库
    kb = VectorKnowledgeBase(storage_path='memory/test_kb', vectorizer_method='tfidf')
    
    # 添加文档
    documents = [
        ("doc1", "Base64编码是一种常见的编码方式，用于将二进制数据转换为ASCII字符。", {"category": "crypto"}),
        ("doc2", "SQL注入是通过插入恶意SQL语句来攻击数据库的漏洞。", {"category": "web"}),
        ("doc3", "XSS跨站脚本攻击是通过注入恶意脚本来攻击用户的漏洞。", {"category": "web"}),
        ("doc4", "Hex十六进制是一种常用的数字表示方法，用于表示二进制数据。", {"category": "crypto"}),
        ("doc5", "RSA是一种非对称加密算法，使用公钥和私钥进行加密解密。", {"category": "crypto"}),
        ("doc6", "SSRF服务器端请求伪造，攻击者可以让服务器发起恶意请求。", {"category": "web"}),
    ]
    
    print("\n📝 添加文档...")
    for doc_id, text, metadata in documents:
        kb.add_document(doc_id, text, metadata)
        print(f"  ✓ {doc_id}: {text[:30]}...")
    
    # 语义搜索
    print("\n🔍 语义搜索: '十六进制'")
    results = kb.search('十六进制', top_k=3)
    for i, result in enumerate(results, 1):
        print(f"  {i}. [{result['doc_id']}] 相似度: {result['similarity']:.3f}")
        print(f"     文本: {result['text']}")
    
    # 混合搜索
    print("\n🔍 混合搜索: '编码方式'")
    results = kb.hybrid_search('编码方式', top_k=3)
    for i, result in enumerate(results, 1):
        print(f"  {i}. [{result['doc_id']}] 组合分数: {result['combined_score']:.3f}")
        print(f"     语义相似度: {result['similarity']:.3f}")
        print(f"     关键词分数: {result['keyword_score']:.3f}")
    
    # 聚类
    print("\n📊 文档聚类 (3类)")
    clusters = kb.cluster_documents(n_clusters=3)
    for cluster_id, doc_ids in clusters.items():
        print(f"  {cluster_id}: {doc_ids}")
    
    # 统计
    print(f"\n📈 知识库统计")
    stats = kb.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # 保存
    kb._save()
    print("\n✅ 知识库已保存")
