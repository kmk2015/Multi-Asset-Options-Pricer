from Options import Option
import datetime as datetime
import numpy as np


class EquityIndexOption(Option):

    def __init__(self, name, trade_date, expiry_date, pay_or_rec, strike, day_count, pv_ccy):

        super().__init__(name, trade_date, expiry_date, pay_or_rec, strike, day_count, pv_ccy)

    def __str__(self):
        return super().__str__()

    def pv(self, spot, sigma, rd, rf):
        """
        :param spot: underlying spot rate
        :param sigma: annual log normal volatility year, 16% Annual Volatility should be input as 16/100
        :param rd: cost of funding/risk-free rate, 2% Annual Rate should be input as 2.0/100.0
        :param rf: Annualized dividend rate, 2% Annual dividends should be input as 2.0/100
        :return: price in points of index
        """

        time_to_expiry = (self._expiry_date - self._trade_date).days/self._day_count

        if self._call_or_put.lower() in ['pay', 'payer', 'call', 'c']:
            call_or_put = 'call'
        elif self._call_or_put.lower() in ['rec', 'receiver', 'put','p']:
            call_or_put = 'put'
        forward = spot * np.exp((rd-rf)*time_to_expiry)
        price = super().blackscholes(forward, self._strike,time_to_expiry, sigma, call_or_put)
        price = price * np.exp(-rd*time_to_expiry)
        return price

    def delta(self, spot, sigma, rd, rf, bump=10):
        """
        :param spot: underlying spot rate
        :param sigma: annual log normal volatility year, 16% Annual Volatility should be input as 16/100
        :param rd: cost of funding/risk-free rate, 2% Annual Rate should be input as 2.0/100.0
        :param rf: Annualized dividend rate, 2% Annual dividends should be input as 2.0/100
        :param bump: amount by which underlying is shifted to calculate numerical delta
        :return: delta in absolute units, so a returned value of 0.5 means 50 delta
       """
        pv_up = self.pv(spot + bump, sigma, rd, rf)
        pv_down = self.pv(spot- bump, sigma, rd, rf)

        return (pv_up - pv_down)/bump/2.0

    def gamma(self, spot, sigma, rd, rf, bump=10):
        """
        :param spot: underlying spot rate
        :param sigma: annual log normal volatility year, 16% Annual Volatility should be input as 16/100
        :param rd: cost of funding/risk-free rate, 2% Annual Rate should be input as 2.0/100.0
        :param rf: Annualized dividend rate, 2% Annual dividends should be input as 2.0/100
        :param bump: amount by which underlying is shifted to calculate numerical gamma
        :return: gamma in units of delta
        """
        delta_up = self.delta(spot + bump, sigma, rd, rf)
        delta_down = self.delta(spot - bump, sigma, rd, rf)

        return (delta_up - delta_down)/bump/2

    def vega(self, spot, sigma, rd, rf, bump=1):
        """
        :param forward: Forward is in basis points
        :param sigma: Sigma is Annual Black Normal Volatility in Basis Points/Yr
        :param annuity: Annuity is per 10000 Notional, so for a 10yr swap, approximately 10
        :param bump: the amount by which the sigma is bumped to calculate the numerical gamma, should be in vol points
        :return: the returned value is vega/1 percentage point for 1 unit of underlying
        """

        pv_up = self.pv(spot, sigma + bump/100, rd, rf)
        pv_down = self.pv(spot, sigma - bump/100, rd, rf)

        return (pv_up - pv_down)/bump/2


if __name__== '__main__':
    spx_call = EquityIndexOption('SPX', datetime.datetime(2017,1,31), datetime.datetime(2018,1,31),'call',4400,365,'USD')
    print(spx_call)

    print('PV for 1 unit of ATM call: ',spx_call.pv(4400,16/100, 0.02,0.02))
    print('delta for 1 unit of ATM call: ', spx_call.delta(4400,16/100, 0.02,0.02))
    print('gamma for 1 unit of ATM call: ', spx_call.gamma(4400,16/100, 0.02,0.02))
    print('vega for 1 unit of ATM call: ', spx_call.vega(4400, 16 / 100, 0.02, 0.02))

    spx_put = EquityIndexOption('SPX', datetime.datetime(2017, 1, 31), datetime.datetime(2018, 1, 31), 'put', 4400, 365,'USD')
    print(spx_put)

    print('PV for 1 unit of ATM put: ', spx_put.pv(4400, 16 / 100, 0.02, 0.02))
    print('delta for 1 unit of ATM put: ', spx_put.delta(4400, 16 / 100, 0.02, 0.02))
    print('gamma for 1 unit of ATM put: ', spx_put.gamma(4400, 16 / 100, 0.02, 0.02))
    print('vega for 1 unit of ATM put: ', spx_put.vega(4400, 16 / 100, 0.02, 0.02))