from dataclasses import dataclass, field


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
    

