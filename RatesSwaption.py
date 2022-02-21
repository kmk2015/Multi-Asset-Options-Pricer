from Options import Option
import datetime as datetime


class RatesSwaption(Option):

    def __init__(self, name, trade_date, expiry_date, pay_or_rec, strike, day_count, pv_ccy):

        super().__init__(name, trade_date, expiry_date, pay_or_rec, strike, day_count, pv_ccy)

    def __str__(self):
        return super().__str__()

    def pv(self, forward, sigma, annuity):
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

    def delta(self, forward, sigma, annuity, bump=10):
        """
        :param forward: Forward is in basis points
        :param sigma: Sigma is Annual Black Normal Volatility in Basis Points/Yr
        :param annuity: Annuity is per 10000 Notional, so for a 10yr swap, approximately 10
        :param bump: the amount by which the forward is bumped to calculate the numerical dv01
        :return: the returned value is dv01/10000 Notional, payers have positive dv01 and receivers negative dv01
        """
        pv_up = self.pv(forward + bump, sigma, annuity)
        pv_down = self.pv(forward - bump, sigma, annuity)

        return (pv_up - pv_down)/bump/2.0

    def gamma(self, forward, sigma, annuity, bump=10):
        """
        :param forward: Forward is in basis points
        :param sigma: Sigma is Annual Black Normal Volatility in Basis Points/Yr
        :param annuity: Annuity is per 10000 Notional, so for a 10yr swap, approximately 10
        :param bump: the amount by which the forward is bumped to calculate the numerical gamma
        :return: the returned value is gamma/10000 Notional,
        """

        delta_up = self.delta(forward + bump, sigma, annuity)
        delta_down = self.delta(forward - bump, sigma, annuity)

        return (delta_up - delta_down)/bump/2

    def vega(self, forward, sigma, annuity, bump=5):
        """
        :param forward: Forward is in basis points
        :param sigma: Sigma is Annual Black Normal Volatility in Basis Points/Yr
        :param annuity: Annuity is per 10000 Notional, so for a 10yr swap, approximately 10
        :param bump: the amount by which the sigma is bumped to calculate the numerical gamma
        :return: the returned value is vega/10000 Notional,
        """

        pv_up = self.pv(forward, sigma + bump, annuity)
        pv_down = self.pv(forward, sigma - bump, annuity)

        return (pv_up - pv_down)/bump/2


if __name__== '__main__':
    payr_swaption = RatesSwaption('RatesPayer', datetime.datetime(2017,1,31), datetime.datetime(2018,1,31),'Payer',180,365,'USD')
    print(payr_swaption)

    print('PV for 100mm notional of ATM payer: ',payr_swaption.pv(180, 100,10)*100e6/1e4)
    print('dv01 for 100mm notional of ATM payer: ', payr_swaption.delta(180, 100, 10)*100e6/1e4)
    print('gamma for 100mm notional of ATM payer: ', payr_swaption.gamma(180, 100, 10)*100e6/1e4)
    print('vega for 100mm notional of ATM payer: ', payr_swaption.vega(180, 100, 10)*100e6/1e4)

    recr_swaption = RatesSwaption('RatesRecr', datetime.datetime(2017,1,31), datetime.datetime(2018,1,31),'Rec',180,365,'USD')
    print(recr_swaption)

    print('PV for 100mm notional of ATM receiver: ',recr_swaption.pv(180, 100,10)*100e6/1e4)
    print('dv01 for 100mm notional of ATM receiver: ', recr_swaption.delta(180, 100, 10)*100e6/1e4)
    print('gamma for 100mm notional of ATM receiver: ', recr_swaption.gamma(180, 100, 10)*100e6/1e4)
    print('vega for 100mm notional of ATM receiver: ', recr_swaption.vega(180, 100, 10)*100e6/1e4)