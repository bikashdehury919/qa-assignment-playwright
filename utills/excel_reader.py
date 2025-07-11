# utills/excel_reader.py to fetch data from excel

import pandas as pd
import os


class ExcelReader:
    def __init__(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Excel file not found: {file_path}")
        self.file_path = file_path
        self.sheets = pd.read_excel(file_path, sheet_name=None, engine='openpyxl')

    def get_order_test_cases(self):
        df = self.sheets.get("Order_Details")
        if df is None:
            raise ValueError("Missing 'Order_Details' sheet in Excel.")
        return df.dropna(how="all").to_dict(orient="records")

    def get_customer(self):
        df = self.sheets.get("Customer_Details")
        if df is None:
            raise ValueError("Missing 'Customer_Details' sheet.")
        return df.dropna(how="all").iloc[0].to_dict()
