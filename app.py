from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import base64
import io
import time
from PIL import Image
from image_processor import ImageProcessor
from similarity_calculator import SimilarityCalculator
from llm_integration import LLMIntegration
import os

# 配置Flask应用，指定静态文件目录
app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)  # 启用跨域支持

# 初始化各个模块
image_processor = ImageProcessor()
similarity_calculator = SimilarityCalculator()
llm_integration = LLMIntegration()

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'ok',
        'timestamp': time.time()
    })

@app.route('/api/image/similarity/single', methods=['POST'])
def single_image_similarity():
    """单张对比图相似度计算接口"""
    try:
        data = request.json
        
        # 获取原图
        original_image_data = get_image_from_request(data, 'original_image')
        if not original_image_data:
            return jsonify({'error': '原图数据不存在或格式错误'}), 400
        
        # 获取对比图
        compare_image_data = get_image_from_request(data, 'compare_image')
        if not compare_image_data:
            return jsonify({'error': '对比图数据不存在或格式错误'}), 400
        
        # 提取特征
        original_features = image_processor.extract_features(original_image_data)
        compare_features = image_processor.extract_features(compare_image_data)
        
        # 计算相似度
        similarity_score = similarity_calculator.calculate_similarity(original_features, compare_features)
        
        return jsonify({
            'similarity': float(similarity_score),
            'timestamp': time.time()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/image/similarity/multiple', methods=['POST'])
def multiple_image_similarity():
    """多张对比图相似度计算接口"""
    try:
        data = request.json
        
        # 获取原图
        original_image_data = get_image_from_request(data, 'original_image')
        if not original_image_data:
            return jsonify({'error': '原图数据不存在或格式错误'}), 400
        
        # 获取对比图列表
        compare_images = data.get('compare_images', [])
        if not compare_images or not isinstance(compare_images, list):
            return jsonify({'error': '对比图列表不存在或格式错误'}), 400
        
        # 提取原图特征
        original_features = image_processor.extract_features(original_image_data)
        
        # 计算每张对比图的相似度
        results = []
        for i, compare_image_data in enumerate(compare_images):
            try:
                # 处理每张对比图
                image_data = get_image_from_request(compare_image_data, 'image')
                if image_data:
                    compare_features = image_processor.extract_features(image_data)
                    similarity_score = similarity_calculator.calculate_similarity(original_features, compare_features)
                    results.append({
                        'index': i,
                        'similarity': float(similarity_score)
                    })
                else:
                    results.append({
                        'index': i,
                        'error': '图像数据不存在或格式错误'
                    })
            except Exception as e:
                results.append({
                    'index': i,
                    'error': str(e)
                })
        
        return jsonify({
            'results': results,
            'timestamp': time.time()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/image/similarity/llm', methods=['POST'])
def similarity_with_llm():
    """结合大模型对话的图像相似度计算接口"""
    try:
        data = request.json
        
        # 获取原图
        original_image_data = get_image_from_request(data, 'original_image')
        if not original_image_data:
            return jsonify({'error': '原图数据不存在或格式错误'}), 400
        
        # 获取对比图
        compare_image_data = get_image_from_request(data, 'compare_image')
        if not compare_image_data:
            return jsonify({'error': '对比图数据不存在或格式错误'}), 400
        
        # 获取用户问题
        user_question = data.get('question', '')
        if not user_question:
            return jsonify({'error': '用户问题不存在'}), 400
        
        # 提取特征
        original_features = image_processor.extract_features(original_image_data)
        compare_features = image_processor.extract_features(compare_image_data)
        
        # 计算相似度
        similarity_score = similarity_calculator.calculate_similarity(original_features, compare_features)
        
        # 获取图像描述
        original_description = image_processor.describe_image(original_image_data)
        compare_description = image_processor.describe_image(compare_image_data)
        
        # 调用大模型生成回答
        llm_response = llm_integration.generate_response(
            user_question=user_question,
            original_image_description=original_description,
            compare_image_description=compare_description,
            similarity_score=float(similarity_score)
        )
        
        return jsonify({
            'similarity': float(similarity_score),
            'original_image_description': original_description,
            'compare_image_description': compare_description,
            'llm_response': llm_response,
            'timestamp': time.time()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_image_from_request(data, field_name):
    """从请求数据中获取图像"""
    image_field = data.get(field_name, {})
    
    # 检查是否为URL
    if isinstance(image_field, str) and (image_field.startswith('http://') or image_field.startswith('https://')):
        return {'type': 'url', 'data': image_field}
    
    # 检查是否为base64编码
    if isinstance(image_field, dict) and 'base64' in image_field:
        try:
            # 尝试解码base64
            img_data = base64.b64decode(image_field['base64'])
            img = Image.open(io.BytesIO(img_data))
            return {'type': 'image', 'data': img}
        except Exception:
            pass
    
    # 检查是否为文件路径（仅用于本地测试）
    if isinstance(image_field, dict) and 'path' in image_field:
        return {'type': 'path', 'data': image_field['path']}
    
    return None

@app.route('/')
def index():
    """默认路由，返回前端页面"""
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)