# core/vendor_comparison.py
import pandas as pd

class VendorComparison:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def compare(self, item_code: str, year):
        if self.df.empty:
            return pd.DataFrame()

        # ---- FILTER BY ITEM CODE ----
        df = self.df[self.df["item_code"] == item_code]

        # ---- FILTER BY YEAR ----
        if year != "All":
            df = df[df["po_date"].dt.year == int(year)]

        if df.empty:
            return pd.DataFrame()

        # ---- DETECT VENDOR COLUMN ----
        possible_vendor_cols = ["vendor"]
        vendor_col = None
        for col in possible_vendor_cols:
            if col in df.columns:
                vendor_col = col
                break

        if vendor_col is None:
            raise ValueError(
                f"No vendor column found. Available columns: {df.columns.tolist()}"
            )

        # ---- CLEAN DATA ----
        df = df.dropna(subset=[vendor_col, "unit_price"])

        # ---- HANDLE SINGLE VENDOR CASE ----
        if df[vendor_col].nunique() < 2:
            return pd.DataFrame({
                "Message": ["Only one vendor available for this item & year"]
            })

        # ---- AGGREGATE ----
        result = (
            df
            .groupby(vendor_col)
            .agg(
                avg_unit_rate=("unit_price", "mean"),
                min_unit_rate=("unit_price", "min"),
                max_unit_rate=("unit_price", "max"),
                transactions=("unit_price", "count")
            )
            .reset_index()
            .sort_values("avg_unit_rate")
        )

        # ---- MARK BEST VENDOR ----
        result["Best Vendor"] = "No"
        result.loc[result["avg_unit_rate"].idxmin(), "Best Vendor"] = "Yes"

        return result
