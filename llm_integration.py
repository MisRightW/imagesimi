import requests
import json

class LLMIntegration:
    """
    大语言模型集成类，用于生成与图像相似度相关的对话回复
    """
    
    def __init__(self, config=None):
        # 默认配置
        self.config = config or {
            'api_type': 'mock',  # 默认使用模拟响应，可以设置为'openai'等实际API
            # 其他配置可以在这里添加，比如API密钥、模型名称等
        }
    
    def generate_response(self, user_question, original_image_description, 
                         compare_image_description, similarity_score):
        """
        基于用户问题、图像描述和相似度分数生成回复
        参数:
            user_question: 用户的问题
            original_image_description: 原图的描述
            compare_image_description: 对比图的描述
            similarity_score: 两张图片的相似度分数
        返回:
            生成的回复文本
        """
        if self.config['api_type'] == 'mock':
            # 使用模拟响应
            return self._generate_mock_response(
                user_question, original_image_description, 
                compare_image_description, similarity_score
            )
        else:
            # 调用实际的大模型API
            return self._call_external_api(
                user_question, original_image_description, 
                compare_image_description, similarity_score
            )
    
    def _generate_mock_response(self, user_question, original_image_description, 
                               compare_image_description, similarity_score):
        """
        生成模拟的回复（用于演示，无需实际调用API）
        """
        # 根据相似度分数生成不同的描述
        if similarity_score > 0.8:
            similarity_desc = "非常相似"
        elif similarity_score > 0.6:
            similarity_desc = "比较相似"
        elif similarity_score > 0.4:
            similarity_desc = "有一定相似性"
        else:
            similarity_desc = "不太相似"
        
        # 构建回复
        response = f"根据分析，原图和对比图的相似度为{similarity_score:.2f}，{similarity_desc}。\n"
        response += f"原图内容：{original_image_description}\n"
        response += f"对比图内容：{compare_image_description}\n"
        
        # 根据用户问题生成不同的回复
        if "区别" in user_question or "不同" in user_question:
            if similarity_score < 0.6:
                response += "两张图片在内容上有明显差异。"
            else:
                response += "两张图片内容较为相似，但可能在细节上有细微差别。"
        elif "是否相同" in user_question or "是不是同一个" in user_question:
            if similarity_score > 0.9:
                response += "两张图片高度相似，可能是同一张图片或非常相似的内容。"
            else:
                response += "两张图片不是完全相同的内容，但有一定的相似性。"
        else:
            response += "请问您对这两张图片还有什么具体问题吗？"
        
        return response
    
    def _call_external_api(self, user_question, original_image_description, 
                          compare_image_description, similarity_score):
        """
        调用外部大模型API生成回复
        注意：这里需要根据实际使用的API进行配置和实现
        """
        # 这里仅提供一个示例框架，实际使用时需要根据具体API进行修改
        # 例如OpenAI的API调用方式
        
        api_type = self.config['api_type']
        
        if api_type == 'openai':
            # 示例：OpenAI API调用
            # 注意：这需要设置有效的API密钥
            api_key = self.config.get('api_key')
            if not api_key:
                raise ValueError("未设置OpenAI API密钥")
            
            # 构建提示
            prompt = self._build_prompt(
                user_question, original_image_description, 
                compare_image_description, similarity_score
            )
            
            # 这里仅为示例，实际使用时需要按照OpenAI API的最新规范进行调用
            try:
                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-3.5-turbo",
                        "messages": [
                            {"role": "system", "content": "你是一个图像分析助手，可以帮助用户分析图片相似度和内容差异。"},
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": 500
                    }
                )
                
                response.raise_for_status()
                data = response.json()
                
                # 提取生成的文本
                return data['choices'][0]['message']['content']
            except Exception as e:
                # 如果API调用失败，回退到模拟响应
                return f"API调用失败: {str(e)}\n\n" + \
                       self._generate_mock_response(
                           user_question, original_image_description, 
                           compare_image_description, similarity_score
                       )
        else:
            # 不支持的API类型，回退到模拟响应
            return "不支持的API类型，使用模拟响应: " + \
                   self._generate_mock_response(
                       user_question, original_image_description, 
                       compare_image_description, similarity_score
                   )
    
    def _build_prompt(self, user_question, original_image_description, 
                     compare_image_description, similarity_score):
        """
        构建发送给大模型的提示文本
        """
        prompt = f"用户问题: {user_question}\n"
        prompt += f"原图描述: {original_image_description}\n"
        prompt += f"对比图描述: {compare_image_description}\n"
        prompt += f"图像相似度分数: {similarity_score:.2f} (范围0-1，值越大表示越相似)\n"
        prompt += "请基于以上信息，以自然友好的语言回答用户的问题。"
        
        return prompt