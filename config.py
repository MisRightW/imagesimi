# 应用配置文件

# Flask应用配置
class Config:
    """基本配置类"""
    # 应用密钥
    SECRET_KEY = 'dev_key_change_in_production'  # 生产环境中应更改为随机密钥
    
    # 图像处理配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 最大上传文件大小，16MB
    
    # LLM配置
    LLM_CONFIG = {
        'api_type': 'openai',  # 可选值: 'mock', 'openai'
        'api_key': 'sk-xxxx',  # 如果使用实际API，填写对应的API密钥
        'model': 'qwen3-max'  # 使用的模型名称
    }

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    
class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    # 生产环境中应更改SECRET_KEY
    SECRET_KEY = 'production_secret_key_change_this'

# 根据环境选择配置
config_by_name = {
    'dev': DevelopmentConfig,
    'prod': ProductionConfig,
    'default': DevelopmentConfig
}