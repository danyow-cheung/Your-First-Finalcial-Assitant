import pandas as pd 
import os 
from core.llm_client import Chat 
from dotenv import load_dotenv
import json 
load_dotenv()


def read_local_excel_file(
        file_path: str,
        sheet_name: str =None 
    ):
    raw_data = pd.read_excel(file_path,sheet_name=sheet_name)
    print(raw_data)


    return raw_data 


def main(user_query: str, excel_path: str):
    excel_data = None 

    if os.path.exists(excel_path):
        excel_data = read_local_excel_file(excel_path)
    elif excel_path.startswith("https://") or excel_path.startswith("www"):
        raise NotImplementedError(f"Pending development on online excel file")
    
    llm_vendor = os.getenv("LLM_VENDOR")
    api_key = os.getenv("API_KEY")
    if not llm_vendor and not api_key:
        raise ValueError(f"Please update .env file,receive llm_vendor={llm_vendor},api_key={api_key}")
    print(f"Receive llm_vendor={llm_vendor},api_key={api_key}")
    if not llm_vendor:
        llm_vendor="ZHIPU"
    llm_model = Chat(llm_vendor,api_key)
   
    if excel_data and isinstance(excel_data,dict):
        try:
            formatted_json = json.dumps(excel_data, ensure_ascii=False, indent=2)
            user_query += formatted_json 
        except Exception as e:
            print("Fail to parse json format,default use string ")
            user_query += str(excel_data)

    response = llm_model.accompletions(user_query)


