
from statsmodels.tsa.arima.model import ARIMA

class PriceAnalytics:
    def __init__(self, series):
        self.series = series

    def forecast(self, steps=6):
        model = ARIMA(self.series, order=(1,1,1))
        fit = model.fit()
        return fit.forecast(steps)
