from zai import ZhipuAiClient
import os 
from typing import Tuple 
from src.utils.llm.data_model import LLM_VENDOR_CLASS,LLMClientRegistry


def zhupu_client(user_input: str):
    api_key = os.getenv("API_KEY")
    if not  api_key:
        raise ValueError(f"")
    client = ZhipuAiClient(api_key=api_key)  

    response = client.chat.completions.create(
        model="glm-4.7",
        messages=[
            {"role": "user", "content": user_input}],
        thinking={
            "type": "enabled",    # Enable deep thinking mode
        },
        max_tokens=65536,          # Maximum output tokens
        temperature=1.0           # Control output randomness
    )

    # Get complete response
    print(response.choices[0].message)
    return response.choices[0].message 


class Chat:
    def __init__(self, 
                llm_vendor: str,
                api_key:str) -> None:
        self.history = []
        self.api_key = api_key 
        self.registry = LLMClientRegistry()
        self.pre_ready_llm_client(llm_vendor)


    def pre_ready_llm_client(self,llm_vendor):
        # self.llm_client = llm_client(api_key)
        valid_llm = LLM_VENDOR_CLASS.is_valid_vendor(llm_vendor)
        if valid_llm:
            # 2. 配置API密钥 
            # self.registry.set_api_key(valid_llm, self.api_key)
            # self.client = self.registry.create_client(llm_vendor)
            self.registry.set_api_key(llm_vendor,self.api_key)
            self.client = self.registry.create_client_with_stored_key(llm_vendor)

    
    def accompletions(self, user_query: str):
        this_time_query = [{"role":"user","content":user_query}]

        if self.history:
            for dict_qeury in self.history:
                this_time_query.index(0, dict_qeury)

        response = self.client.chat.completions.create(
        model="glm-4.7",
        messages=this_time_query,
        thinking={
            "type": "enabled",    # Enable deep thinking mode
        },
        max_tokens=65536,          # Maximum output tokens
        temperature=0
    )

        # Get complete response
        # print("[Response from LLM]=",response.choices[0].message)
        return response.choices[0].message




