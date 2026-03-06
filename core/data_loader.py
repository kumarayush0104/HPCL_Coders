# core/data_loader.py
import pandas as pd
from core.item_master import classify_item

class DataLoader:
    def __init__(self, path: str):
        self.path = path

    def load(self) -> pd.DataFrame:
        df = pd.read_csv(self.path, parse_dates=["po_date"])

        # ---- ADD ITEM CODE USING ITEM MASTER ----
        if "item_code" not in df.columns:
            item_codes = []
            for desc in df["item_description"]:
                result = classify_item(desc)
                item_codes.append(result["item_code"])

            df["item_code"] = item_codes

        return df
