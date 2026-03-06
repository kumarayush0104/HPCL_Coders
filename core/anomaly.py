# core/anomaly.py
# ===============================
# Anomaly Detection per Item Code
# ===============================

class AnomalyDetector:
    def __init__(self, df):
        self.df = df

    def detect(self, item_code, z_thresh=2.0):
        """
        Detect price anomalies for a given item_code
        using Z-score on unit_price.
        """

        # ---- Filter by item_code ----
        subset = self.df[self.df["item_code"] == item_code].copy()

        if subset.empty:
            return subset

        mean = subset["unit_price"].mean()
        std = subset["unit_price"].std()

        if std == 0 or std is None:
            return subset.iloc[0:0]

        subset["z_score"] = (subset["unit_price"] - mean) / std
        subset["anomaly"] = subset["z_score"].abs() > z_thresh

        return subset[subset["anomaly"]]
