from dataclasses import dataclass, field,fields
from typing import Dict, Any,Type,Optional
from typing import Dict, Type, Any, Optional, Callable

from openai import OpenAI 

@dataclass  
class LLM_VENDOR_CLASS:
    ZHIPU: str = "ZHIPU"
    OPENAI: str = "OPENAI"
    DEEPSEEK: str = "DEEPSEEK"
    
    @classmethod
    def is_valid_vendor(cls, input_str: str) -> bool:
        """
        检查输入字符串是否是有效的厂商
        
        Args:
            input_str: 要检查的字符串
            
        Returns:
            bool: 如果输入存在于 dataclass 字段值中则返回 True
        """
        # 获取所有字段的值
        vendor_values = [getattr(cls, field.name) for field in fields(cls)]
        return input_str in vendor_values

from zai import ZhipuAiClient


# 客户端工厂函数
def create_zhipu_client(api_key: str, **kwargs) -> ZhipuAiClient:
    """智谱AI客户端工厂函数"""
    return ZhipuAiClient(api_key=api_key)

def create_openai_client(api_key: str, **kwargs) -> OpenAI:
    """OpenAI客户端工厂函数"""
    return OpenAI(api_key=api_key, **kwargs)

def create_deepseek_client(api_key: str, **kwargs) -> OpenAI:
    """DeepSeek客户端工厂函数（使用OpenAI兼容接口）"""
    # DeepSeek使用特殊的base_url
    config = kwargs.copy()
    config.setdefault("base_url", "https://api.deepseek.com")
    return OpenAI(api_key=api_key, **config)



@dataclass
class LLMClientRegistry:
    """
    LLM客户端注册表
    职责：管理厂商到客户端工厂函数的映射和配置
    """
    # 存储客户端工厂函数
    _client_factories: Dict[str, Callable] = field(default_factory=dict)
    # API密钥存储
    _api_keys: Dict[str, str] = field(default_factory=dict)
    # 厂商默认配置（不包含api_key）
    _default_configs: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    def __post_init__(self):
        """初始化默认客户端工厂"""
        if not self._client_factories:
            self._init_default_factories()
    
    def _init_default_factories(self):
        """初始化默认客户端工厂函数映射"""
        self._client_factories = {
            LLM_VENDOR_CLASS.ZHIPU: create_zhipu_client,
            LLM_VENDOR_CLASS.OPENAI: create_openai_client,
            LLM_VENDOR_CLASS.DEEPSEEK: create_deepseek_client,
        }
        
        # 设置厂商特定的默认配置
        self._default_configs = {
            LLM_VENDOR_CLASS.DEEPSEEK: {
                "base_url": "https://api.deepseek.com",
                "timeout": 30.0
            },
            LLM_VENDOR_CLASS.OPENAI: {
                "timeout": 60.0,
                "max_retries": 3
            }
        }
    
    def register_factory(self, vendor_name: str, factory_func: Callable, **default_config):
        """注册新的厂商客户端工厂"""
        if not LLM_VENDOR_CLASS.is_valid_vendor(vendor_name):
            raise ValueError(f"无效的厂商名称: {vendor_name}")
        
        self._client_factories[vendor_name] = factory_func
        if default_config:
            self._default_configs[vendor_name] = default_config
    
    def set_api_key(self, vendor_name: str, api_key: str) -> None:
        """设置厂商的API密钥"""
        if not LLM_VENDOR_CLASS.is_valid_vendor(vendor_name):
            raise ValueError(f"无效的厂商: {vendor_name}")
        self._api_keys[vendor_name] = api_key
    
    def get_factory(self, vendor_name: str) -> Optional[Callable]:
        """获取厂商对应的客户端工厂函数"""
        if not LLM_VENDOR_CLASS.is_valid_vendor(vendor_name):
            return None
        return self._client_factories.get(vendor_name)
    
    def create_client(self, vendor_name: str, api_key: str = None, **kwargs) -> Any:
        """
        创建厂商客户端实例
        
        Args:
            vendor_name: 厂商名称
            api_key: API密钥（可选，如果未提供则使用已存储的）
            **kwargs: 客户端配置参数
            
        Returns:
            客户端实例
            
        Raises:
            ValueError: 厂商不存在或未注册客户端工厂
        """
        # 1. 验证厂商
        if not LLM_VENDOR_CLASS.is_valid_vendor(vendor_name):
            raise ValueError(f"不支持的LLM厂商: {vendor_name}")
        
        # 2. 获取客户端工厂函数
        factory = self._client_factories.get(vendor_name)
        if factory is None:
            raise ValueError(f"厂商 {vendor_name} 未注册客户端工厂")
        
        # 3. 确定API密钥
        final_api_key = api_key or self._api_keys.get(vendor_name)
        if final_api_key is None:
            raise ValueError(
                f"创建 {vendor_name} 客户端需要API密钥，但未提供。\n"
                f"请通过以下方式之一提供：\n"
                f"1. 作为参数传入: create_client('{vendor_name}', api_key='your_key')\n"
                f"2. 先调用 set_api_key('{vendor_name}', 'your_key')"
            )
        
        # 4. 构建配置
        config = {}
        
        # 4.1 添加默认配置（如果有）
        if vendor_name in self._default_configs:
            config.update(self._default_configs[vendor_name])
        
        # 4.2 添加用户提供的其他配置
        config.update(kwargs)
        
        # 5. 使用工厂函数创建客户端
        try:
            return factory(api_key=final_api_key, **config)
        except Exception as e:
            # 包装异常，提供更清晰的错误信息
            raise RuntimeError(f"创建 {vendor_name} 客户端失败: {str(e)}") from e
    
    def create_client_with_stored_key(self, vendor_name: str, **kwargs) -> Any:
        """
        使用已存储的API密钥创建客户端实例
        
        Args:
            vendor_name: 厂商名称
            **kwargs: 客户端配置参数
            
        Returns:
            客户端实例
        """
        return self.create_client(vendor_name, api_key=None, **kwargs)
    
    def get_supported_vendors(self) -> list:
        """获取已注册工厂的厂商列表"""
        return list(self._client_factories.keys())
    
    def get_vendor_info(self, vendor_name: str) -> Dict[str, Any]:
        """获取厂商的配置信息"""
        if not LLM_VENDOR_CLASS.is_valid_vendor(vendor_name):
            return {}
        
        info = {
            "has_factory": vendor_name in self._client_factories,
            "has_api_key": vendor_name in self._api_keys,
            "has_default_config": vendor_name in self._default_configs,
        }
        
        if info["has_factory"]:
            info["factory"] = self._client_factories[vendor_name].__name__
        
        if info["has_default_config"]:
            info["default_config"] = self._default_configs[vendor_name]
        
        return info
