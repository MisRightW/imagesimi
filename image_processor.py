import torch
import requests
from PIL import Image
from io import BytesIO
from transformers import CLIPProcessor, CLIPModel

class ImageProcessor:
    def __init__(self):
        # 加载CLIP模型和处理器
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        
        # 检查是否有GPU可用
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        
        # 模型设置为评估模式
        self.model.eval()
    
    def load_image(self, image_data):
        """
        根据不同类型的数据加载图像
        image_data格式: {'type': 'url'/'path'/'image', 'data': 具体数据}
        """
        if image_data['type'] == 'url':
            # 从URL加载图像
            response = requests.get(image_data['data'])
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))
        elif image_data['type'] == 'path':
            # 从本地路径加载图像
            img = Image.open(image_data['data'])
        elif image_data['type'] == 'image':
            # 已经是PIL Image对象
            img = image_data['data']
        else:
            raise ValueError(f"不支持的图像类型: {image_data['type']}")
        
        # 转换为RGB格式
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        return img
    
    def extract_features(self, image_data):
        """
        提取图像特征
        返回: numpy数组形式的特征向量
        """
        # 加载图像
        img = self.load_image(image_data)
        
        # 准备输入
        inputs = self.processor(images=img, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # 提取特征
        with torch.no_grad():
            features = self.model.get_image_features(**inputs)
            # 归一化特征向量
            features = torch.nn.functional.normalize(features, dim=1)
        
        # 转换为numpy数组并返回
        return features.cpu().numpy().flatten()
    
    def describe_image(self, image_data):
        """
        使用CLIP模型生成图像的文字描述
        注意：CLIP本身不能直接生成描述，但我们可以使用一些预设的标签来描述图像
        这里简单实现，实际应用中可能需要接入其他模型
        """
        # 加载图像
        img = self.load_image(image_data)
        
        # 一些常见的图像描述标签
        common_labels = [
            "a photo of a cat", "a photo of a dog", "a photo of a person",
            "a photo of a car", "a photo of a building", "a photo of food",
            "a photo of nature", "a photo of a landscape", "a photo of a city",
            "a photo of a beach", "a photo of mountains", "a photo of a river",
            "a photo of an animal", "a photo of a plant", "a photo of technology"
        ]
        
        # 准备输入
        image_inputs = self.processor(images=img, return_tensors="pt")
        image_inputs = {k: v.to(self.device) for k, v in image_inputs.items()}
        
        text_inputs = self.processor(text=common_labels, return_tensors="pt", padding=True)
        text_inputs = {k: v.to(self.device) for k, v in text_inputs.items()}
        
        # 计算图像和文本的相似度
        with torch.no_grad():
            image_features = self.model.get_image_features(**image_inputs)
            text_features = self.model.get_text_features(**text_inputs)
            
            # 归一化特征向量
            image_features = torch.nn.functional.normalize(image_features, dim=1)
            text_features = torch.nn.functional.normalize(text_features, dim=1)
            
            # 计算余弦相似度
            similarity = torch.matmul(image_features, text_features.T)
            
            # 获取最匹配的前3个标签
            values, indices = torch.topk(similarity, 3)
        
        # 构建描述
        descriptions = [common_labels[i] for i in indices[0]]
        confidence_scores = [float(v) for v in values[0]]
        
        # 构建简单描述
        if max(confidence_scores) > 0.25:  # 设置阈值
            main_description = descriptions[0]
            return f"图像可能是: {main_description}"
        else:
            return "无法准确描述图像内容"