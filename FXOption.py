from Options import Option
import datetime as datetime
import numpy as np


class FXOption(Option):
    """
    FX Vanilla Option
    Note : conventions related to differences in value dates will be implemented in future versions
    Conventions related to day counts will be implemented in future versions
    pv currency has to be either the domestic or foreign currency. pv in a third currency(quanto) not implemented
    need to implement pv, delta, gamma  as percentage per unit notional of foreign currency
    """

    def __init__(self, *, name, trade_date,
                 expiry_date, call_or_put, strike,
                 day_count, pv_ccy, ccy):

        super().__init__(name, trade_date, expiry_date, call_or_put, strike, day_count, pv_ccy)
        self._ccy = ccy
        if pv_ccy not in [ccy[0:3], ccy[3:6]]:
            raise Exception("PV CCY has to be either the domestic or foreign currency of the pair")

    def __str__(self):
        return super().__str__()

    def pv(self, *, spot, sigma, rd, rf):
        """
        :param spot: underlying spot rate
        :param sigma: annual log normal volatility year, 16% Annual Volatility should be input as 16/100
        :param rd: cost of funding in domestic currency, 2% Annual Rate should be input as 2.0/100.0
        :param rf: cost of funding in foreign currency, 2% Annual dividends should be input as 2.0/100
        :return: price in specified pv currency
        """

        time_to_expiry = (self._expiry_date - self._trade_date).days / self._day_count

        if self._call_or_put.lower() in ['pay', 'payer', 'call', 'c']:
            call_or_put = 'call'
        elif self._call_or_put.lower() in ['rec', 'receiver', 'put', 'p']:
            call_or_put = 'put'
        forward = spot * np.exp((rd - rf) * time_to_expiry)
        price = super().blackscholes(forward, self._strike, time_to_expiry, sigma, call_or_put)
        price = price * np.exp(-rd * time_to_expiry)
        if self._pv_ccy == self._ccy[0:3]:
            return price/spot
        elif self._pv_ccy == self._ccy[3:6]:
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
        delta = (pv_up - pv_down) / bump / 2.0

        if self._pv_ccy == self._ccy[0:3]:
            return delta/bump*spot
        elif self._pv_ccy == self._ccy[3:6]:
            return delta

    def gamma(self, *, spot, sigma, rd, rf, bump=10):
        """
        :param spot: underlying spot rate
        :param sigma: annual log normal volatility year, 16% Annual Volatility should be input as 16/100
        :param rd: cost of funding/risk-free rate, 2% Annual Rate should be input as 2.0/100.0
        :param rf: Annualized dividend rate, 2% Annual dividends should be input as 2.0/100
        :param bump: amount by which underlying is shifted to calculate numerical gamma
        :return: gamma in units of delta
        """
        delta_up = self.delta(spot=spot + bump, sigma=sigma, rd=rd, rf=rf, bump=bump)
        delta_down = self.delta(spot=spot - bump, sigma=sigma, rd=rd, rf=rf, bump=bump)

        return (delta_up - delta_down) / bump / 2.

    def vega(self, *, spot, sigma, rd, rf, bump=1):
        """
        :param forward: Forward is in basis points
        :param sigma: Sigma is Annual Black Normal Volatility in Basis Points/Yr
        :param annuity: Annuity is per 10000 Notional, so for a 10yr swap, approximately 10
        :param bump: the amount by which the sigma is bumped to calculate the numerical gamma, should be in vol points
        :return: the returned value is vega/1 percentage point for 1 unit of pv currency
        """

        pv_up = self.pv(spot=spot, sigma=sigma + bump / 100, rd=rd, rf=rf)
        pv_down = self.pv(spot=spot, sigma=sigma - bump / 100, rd=rd, rf=rf)

        return (pv_up - pv_down) / bump / 2


if __name__ == '__main__':
    eurusd_call = FXOption(name='EURUSD', trade_date=datetime.datetime(2017, 1, 31),
                                 expiry_date=datetime.datetime(2018, 1, 31), call_or_put='call',
                                 strike=1.14, day_count=365, pv_ccy='USD', ccy='EURUSD')
    print(eurusd_call)

    print('PV for 1 unit of ATM call: ', eurusd_call.pv(spot=1.14, sigma=6 / 100, rd=25e-4, rf=-50/1e4))
    print('delta for 1 unit of ATM call: ', eurusd_call.delta(spot=1.14, sigma=6 / 100, rd=25e-4, rf=-50/1e4, bump=10e-4))
    print('gamma for 1 unit of ATM call: ', eurusd_call.gamma(spot=1.14, sigma=6 / 100, rd=25e-4, rf=-50/1e4,bump=10e-4))
    print('vega for 1 unit of ATM call: ', eurusd_call.vega(spot=1.14, sigma=6 / 100, rd=25e-4, rf=-50/1e4))

    usdjpy_call = FXOption(name='usdjpy', trade_date=datetime.datetime(2017, 1, 31),
                                 expiry_date=datetime.datetime(2018, 1, 31), call_or_put='call',
                                 strike=110, day_count=365, pv_ccy='USD', ccy='USDJPY')
    print(usdjpy_call)

    print('PV for 1 unit of ATM call: ', usdjpy_call.pv(spot=110, sigma=6 / 100, rd=25e-4, rf=-0/1e4))
    print('delta for 1 unit of ATM call: ', usdjpy_call.delta(spot=110, sigma=6 / 100, rd=25e-4, rf=-0/1e4, bump=1))
    print('gamma for 1 unit of ATM call: ', usdjpy_call.gamma(spot=110, sigma=6 / 100, rd=25e-4, rf=-0/1e4,bump=1))
    print('vega for 1 unit of ATM call: ', usdjpy_call.vega(spot=110, sigma=6 / 100, rd=25e-4, rf=-0/1e4))

