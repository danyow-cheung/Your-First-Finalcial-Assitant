from dataclasses import dataclass
import os 
import pandas as pd 

@dataclass 
class ExcelFileType:
    LOCAL: str = "LOCAL"
    GoogleSheet: str = "GoogleSheet"
    TecentDoc: str = "TecentDoc"

    @classmethod
    def which_file(cls, excel_path:str):
        if "google" in excel_path:
            return ExcelFileType.GoogleSheet
        elif "tecent" in excel_path:
            return ExcelFileType.TecentDoc 
        else:
            return ExcelFileType.LOCAL
    
    @classmethod
    def is_file_exists(cls,excel_path: str,excel_type) -> bool:
        if excel_type==ExcelFileType.LOCAL:
            file_exists = os.path.exists(excel_path)
            return file_exists 
        
        elif excel_type == ExcelFileType.GoogleSheet or excel_type==ExcelFileType.TecentDoc:
            raise NotImplementedError(f"Pending ")

    @classmethod 
    def retrive_data(cls,excel_path: str,excel_type, sheet_name: str = None ):
        file_exists = ExcelFileType.is_file_exists(excel_path, excel_type)
        if file_exists:
            file_data  = pd.read_excel(excel_path,sheet_name=sheet_name)
            return file_data 
        


