import numpy as np

class SimilarityCalculator:
    """
    计算图像特征向量之间的相似度
    """
    
    def __init__(self):
        # 初始化参数
        pass
    
    def calculate_similarity(self, features1, features2):
        """
        计算两个特征向量之间的余弦相似度
        参数:
            features1: 第一个图像的特征向量
            features2: 第二个图像的特征向量
        返回:
            相似度分数，范围在0到1之间，值越大表示相似度越高
        """
        # 确保输入是numpy数组
        features1 = np.array(features1)
        features2 = np.array(features2)
        
        # 检查向量维度是否相同
        if features1.shape != features2.shape:
            raise ValueError("特征向量维度不匹配")
        
        # 计算余弦相似度
        # 余弦相似度 = (A·B) / (||A|| * ||B||)
        dot_product = np.dot(features1, features2)
        norm1 = np.linalg.norm(features1)
        norm2 = np.linalg.norm(features2)
        
        # 防止除以零
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        cosine_similarity = dot_product / (norm1 * norm2)
        
        # 余弦相似度范围在-1到1之间，将其映射到0到1之间
        # 使用公式: (similarity + 1) / 2
        normalized_similarity = (cosine_similarity + 1) / 2
        
        # 确保结果在0到1之间
        normalized_similarity = max(0.0, min(1.0, normalized_similarity))
        
        return normalized_similarity
    
    def calculate_batch_similarity(self, base_features, features_list):
        """
        计算一个基准特征向量与多个特征向量之间的相似度
        参数:
            base_features: 基准图像的特征向量
            features_list: 多个图像的特征向量列表
        返回:
            相似度分数列表，每个分数对应features_list中的一个特征向量
        """
        similarities = []
        
        for features in features_list:
            similarity = self.calculate_similarity(base_features, features)
            similarities.append(similarity)
        
        return similarities