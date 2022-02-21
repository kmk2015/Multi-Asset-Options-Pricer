from Options import Option
import datetime as datetime


class RatesSwaption(Option):

    def __init__(self, *, name, trade_date, expiry_date, pay_or_rec, strike, day_count, pv_ccy):

        super().__init__(name, trade_date, expiry_date, pay_or_rec, strike, day_count, pv_ccy)

    def __str__(self):
        return super().__str__()

    def pv(self, *, forward, sigma, annuity):
        """
        :param forward: Forward is in basis points
        :param sigma: Sigma is Annual Black Normal Volatility in Basis Points/Yr
        :param annuity: Annuity is per 10000 Notional, so for a 10yr swap, approximately 10
        :return:   PV is returned in bps upfront
        """

        time_to_expiry = (self._expiry_date - self._trade_date).days/self._day_count

        if self._call_or_put.lower() in ['pay', 'payer']:
            call_or_put = 'call'
        elif self._call_or_put.lower() in ['rec', 'receiver']:
            call_or_put = 'put'

        bps_running = super().blacknormal(forward, self._strike, time_to_expiry, sigma, call_or_put)
        bps_upfront = annuity * bps_running

        return bps_upfront

    def delta(self, *, forward, sigma, annuity, bump=10):
        """
        :param forward: Forward is in basis points
        :param sigma: Sigma is Annual Black Normal Volatility in Basis Points/Yr
        :param annuity: Annuity is per 10000 Notional, so for a 10yr swap, approximately 10
        :param bump: the amount by which the forward is bumped to calculate the numerical dv01
        :return: the returned value is dv01/10000 Notional, payers have positive dv01 and receivers negative dv01
        """
        pv_up = self.pv(forward=forward + bump, sigma=sigma, annuity=annuity)
        pv_down = self.pv(forward=forward - bump, sigma=sigma, annuity=annuity)

        return (pv_up - pv_down)/bump/2.0

    def gamma(self, *, forward, sigma, annuity, bump=10):
        """
        :param forward: Forward is in basis points
        :param sigma: Sigma is Annual Black Normal Volatility in Basis Points/Yr
        :param annuity: Annuity is per 10000 Notional, so for a 10yr swap, approximately 10
        :param bump: the amount by which the forward is bumped to calculate the numerical gamma
        :return: the returned value is gamma/10000 Notional,
        """

        delta_up = self.delta(forward=forward + bump, sigma=sigma, annuity=annuity)
        delta_down = self.delta(forward=forward - bump, sigma=sigma, annuity=annuity)

        return (delta_up - delta_down)/bump/2

    def vega(self, *, forward, sigma, annuity, bump=5):
        """
        :param forward: Forward is in basis points
        :param sigma: Sigma is Annual Black Normal Volatility in Basis Points/Yr
        :param annuity: Annuity is per 10000 Notional, so for a 10yr swap, approximately 10
        :param bump: the amount by which the sigma is bumped to calculate the numerical gamma
        :return: the returned value is vega/10000 Notional,
        """

        pv_up = self.pv(forward=forward, sigma=sigma + bump, annuity=annuity)
        pv_down = self.pv(forward=forward, sigma=sigma - bump, annuity=annuity)

        return (pv_up - pv_down)/bump/2


if __name__== '__main__':
    payr_swaption = RatesSwaption(name='RatesPayer', trade_date=datetime.datetime(2017,1,31),
                                  expiry_date=datetime.datetime(2018,1,31),pay_or_rec='Payer',
                                  strike=180,day_count=365,pv_ccy='USD')
    print(payr_swaption)

    print('PV for 100mm notional of ATM payer: ',payr_swaption.pv(forward=180, sigma=100,annuity=10)*100e6/1e4)
    print('dv01 for 100mm notional of ATM payer: ', payr_swaption.delta(forward=180, sigma=100,annuity=10)*100e6/1e4)
    print('gamma for 100mm notional of ATM payer: ', payr_swaption.gamma(forward=180, sigma=100,annuity=10)*100e6/1e4)
    print('vega for 100mm notional of ATM payer: ', payr_swaption.vega(forward=180, sigma=100,annuity=10)*100e6/1e4)

    recr_swaption = RatesSwaption(name='RatesPayer', trade_date=datetime.datetime(2017, 1, 31),
                                  expiry_date=datetime.datetime(2018, 1, 31), pay_or_rec='rec',
                                  strike=180, day_count=365, pv_ccy='USD')
    print(recr_swaption)

    print('PV for 100mm notional of ATM receiver: ',recr_swaption.pv(forward=180, sigma=100,annuity=10)*100e6/1e4)
    print('dv01 for 100mm notional of ATM receiver: ', recr_swaption.delta(forward=180, sigma=100,annuity=10)*100e6/1e4)
    print('gamma for 100mm notional of ATM receiver: ', recr_swaption.gamma(forward=180, sigma=100,annuity=10)*100e6/1e4)
    print('vega for 100mm notional of ATM receiver: ', recr_swaption.vega(forward=180, sigma=100,annuity=10)*100e6/1e4)