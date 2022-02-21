from Options import Option
import datetime as datetime
import numpy as np


class EquityIndexOption(Option):

    def __init__(self, *, name, trade_date,
                 expiry_date, call_or_put, strike,
                 day_count, pv_ccy):

        super().__init__(name, trade_date, expiry_date, call_or_put, strike, day_count, pv_ccy)

    def __str__(self):
        return super().__str__()

    def pv(self, *, spot, sigma, rd, rf):
        """
        :param spot: underlying spot rate
        :param sigma: annual log normal volatility year, 16% Annual Volatility should be input as 16/100
        :param rd: cost of funding/risk-free rate, 2% Annual Rate should be input as 2.0/100.0
        :param rf: Annualized dividend rate, 2% Annual dividends should be input as 2.0/100
        :return: price in points of index
        """

        time_to_expiry = (self._expiry_date - self._trade_date).days / self._day_count

        if self._call_or_put.lower() in ['pay', 'payer', 'call', 'c']:
            call_or_put = 'call'
        elif self._call_or_put.lower() in ['rec', 'receiver', 'put', 'p']:
            call_or_put = 'put'
        forward = spot * np.exp((rd - rf) * time_to_expiry)
        price = super().blackscholes(forward, self._strike, time_to_expiry, sigma, call_or_put)
        price = price * np.exp(-rd * time_to_expiry)
        return price

    def delta(self, *, spot, sigma, rd, rf, bump=10):
        """
        :param spot: underlying spot rate
        :param sigma: annual log normal volatility year, 16% Annual Volatility should be input as 16/100
        :param rd: cost of funding/risk-free rate, 2% Annual Rate should be input as 2.0/100.0
        :param rf: Annualized dividend rate, 2% Annual dividends should be input as 2.0/100
        :param bump: amount by which underlying is shifted to calculate numerical delta
        :return: delta in absolute units, so a returned value of 0.5 means 50 delta
       """
        pv_up = self.pv(spot=spot + bump, sigma=sigma, rd=rd, rf=rf)
        pv_down = self.pv(spot=spot - bump, sigma=sigma, rd=rd, rf=rf)

        return (pv_up - pv_down) / bump / 2.0

    def gamma(self, *, spot, sigma, rd, rf, bump=10):
        """
        :param spot: underlying spot rate
        :param sigma: annual log normal volatility year, 16% Annual Volatility should be input as 16/100
        :param rd: cost of funding/risk-free rate, 2% Annual Rate should be input as 2.0/100.0
        :param rf: Annualized dividend rate, 2% Annual dividends should be input as 2.0/100
        :param bump: amount by which underlying is shifted to calculate numerical gamma
        :return: gamma in units of delta
        """
        delta_up = self.delta(spot=spot + bump, sigma=sigma, rd=rd, rf=rf)
        delta_down = self.delta(spot=spot - bump, sigma=sigma, rd=rd, rf=rf)

        return (delta_up - delta_down) / bump / 2

    def vega(self, *, spot, sigma, rd, rf, bump=1):
        """
        :param spot: underlying spot rate
        :param sigma: annual log normal volatility year, 16% Annual Volatility should be input as 16/100
        :param rd: cost of funding/risk-free rate, 2% Annual Rate should be input as 2.0/100.0
        :param rf: Annualized dividend rate, 2% Annual dividends should be input as 2.0/100
        :param bump: amount by which volatility is shifted to calculate numerical vega
        :return: the returned value is vega/1 percentage point for 1 unit of underlying
        """

        pv_up = self.pv(spot=spot, sigma=sigma + bump / 100, rd=rd, rf=rf)
        pv_down = self.pv(spot=spot, sigma=sigma - bump / 100, rd=rd, rf=rf)

        return (pv_up - pv_down) / bump / 2


if __name__ == '__main__':
    spx_call = EquityIndexOption(name='SPX', trade_date=datetime.datetime(2017, 1, 31),
                                 expiry_date=datetime.datetime(2018, 1, 31), call_or_put='call',
                                 strike=4400, day_count=365, pv_ccy='USD')
    print(spx_call)

    print('PV for 1 unit of ATM call: ', spx_call.pv(spot=4400, sigma=16 / 100, rd=0.02, rf=0.02))
    print('delta for 1 unit of ATM call: ', spx_call.delta(spot=4400, sigma=16 / 100, rd=0.02, rf=0.02))
    print('gamma for 1 unit of ATM call: ', spx_call.gamma(spot=4400, sigma=16 / 100, rd=0.02, rf=0.02))
    print('vega for 1 unit of ATM call: ', spx_call.vega(spot=4400, sigma=16 / 100, rd=0.02, rf=0.02))

    spx_put = EquityIndexOption(name='SPX', trade_date=datetime.datetime(2017, 1, 31),
                                expiry_date=datetime.datetime(2018, 1, 31), call_or_put='put',
                                strike=4400, day_count=365, pv_ccy='USD')
    print(spx_put)

    print('PV for 1 unit of ATM put: ', spx_put.pv(spot=4400, sigma=16 / 100, rd=0.02, rf=0.02))
    print('delta for 1 unit of ATM put: ', spx_put.delta(spot=4400, sigma=16 / 100, rd=0.02, rf=0.02))
    print('gamma for 1 unit of ATM put: ', spx_put.gamma(spot=4400, sigma=16 / 100, rd=0.02, rf=0.02))
    print('vega for 1 unit of ATM put: ', spx_put.vega(spot=4400, sigma=16 / 100, rd=0.02, rf=0.02))
