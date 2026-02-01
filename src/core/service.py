import pandas as pd 
import os 
from core.llm_client import Chat 


def read_local_excel_file(
        file_path: str,
        sheet_name: str =None 
    ):
    raw_data = pd.read_excel(file_path,sheet_name=sheet_name)
    print(raw_data)


    return raw_data 


def main(user_query: str, excel_path: str):
    
    if os.path.exists(excel_path):
        excel_data = read_local_excel_file(excel_path)
    elif excel_path.startswith("https://") or excel_path.startswith("www"):
        raise NotImplementedError(f"Pending development on online excel file")
    
    llm_vendor = os.getenv("LLM_VENDOR")
    api_key = os.getenv("API_KEY")
    if not llm_vendor:
        llm_vendor="ZHIPU"
    llm_model = Chat(llm_vendor,api_key)

