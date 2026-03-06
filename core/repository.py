class PriceRepository:
    def __init__(self, df):
        self.df = df

    def aggregate_time_series(self, item_code):
        subset = self.df[self.df["item_code"] == item_code]

        return (
            subset
            .groupby("po_date")["unit_price"]
            .mean()
            .sort_index()
        )
