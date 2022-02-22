from Options import Option
from CDS import CDS
import datetime as datetime
import numpy as np


class CDSSwaption(Option):
    """
    This is a CDX Swaption class to quickly calculate prices and greeks of cds swaptions in the absence of a
    full cds pricer and option pricer such as CDSO on Bloomberg.
    The approximations here are good enough to use to price spread based options on cdxig, itraxx main and snr-fin
    These approximations have been checked versus market quotes and the values produced are within market bid ask
    Price based options on CDXHY can also be priced by first converting price based spot and strike levels into
    spread based levels
    """


    def __init__(self, *, name, trade_date,
                 expiry_date, pay_or_rec, strike,
                 day_count, pv_ccy):

        super().__init__(name, trade_date, expiry_date, pay_or_rec, strike, day_count, pv_ccy)

    def __str__(self):
        return super().__str__()

    def pv(self, *, spot, sigma, rd, cds):
        """
        :param spot: level of spot cds spread in bps/annum
        :param sigma:
        :param rd: flat interest rate for discounting, in practice, one uses the full ISDA swap curve for this
        :param cds: cds object with cds details like maturity, recovery
        :return: returns the pv in bps upfront for cds swaption
        """

        time_to_expiry = (self._expiry_date - self._trade_date).days / self._day_count

        forward_annuity_at_spot = cds.forward_annuity(spot=spot, rd=rd, forward_start_date=self._expiry_date)
        forward_annuity_at_strike = cds.forward_annuity(spot=self._strike, rd=rd, forward_start_date=self._expiry_date)
        forward = cds.forward_level(spot=spot, rd=rd, forward_start_date=self._expiry_date)
        hazard = cds.hazard_rate(spot=spot)

        adjusted_strike = cds.coupon + (self._strike - cds.coupon) * (
                    forward_annuity_at_strike / forward_annuity_at_spot /
                    np.exp(-hazard * time_to_expiry))

        if self._call_or_put.lower() in ['pay', 'payer', 'call', 'c']:
            call_or_put = 'call'
        elif self._call_or_put.lower() in ['rec', 'receiver', 'put', 'p']:
            call_or_put = 'put'
        price = super().blackscholes(forward, adjusted_strike, time_to_expiry, sigma, call_or_put)
        price = price * forward_annuity_at_spot
        return price

    def delta(self, *, spot, sigma, rd, cds, bump=10):
        """
        :param spot: level of spot cds spread in bps/annum
        :param sigma:
        :param rd: flat interest rate for discounting, in practice, one uses the full ISDA swap curve for this
        :param cds: cds object with cds details like maturity, recovery
        :param bump: amount by which underlying is shifted to calculate numerical delta
        :return: delta, so a return of 2.5 means 250,000 dollars/basis point/1BB notional of the swaption
        """

        pv_up = self.pv(spot=spot + bump, sigma=sigma, rd=rd, cds=cds)
        pv_down = self.pv(spot=spot - bump, sigma=sigma, rd=rd, cds=cds)

        return (pv_up - pv_down) / bump / 2.0

    def gamma(self, *, spot, sigma, rd, cds, bump=10):
        """
        :param spot: level of spot cds spread in bps/annum
        :param sigma:
        :param rd: flat interest rate for discounting, in practice, one uses the full ISDA swap curve for this
        :param cds: cds object with cds details like maturity, recovery
        :param bump: amount by which underlying is shifted to calculate numerical gamma
        :return: gamma, so a return of 0.144 means 14,400 dv01/basis point/1BB notional of the swaption
        """

        delta_up = self.delta(spot=spot + bump, sigma=sigma, rd=rd, cds=cds)
        delta_down = self.delta(spot=spot - bump, sigma=sigma, rd=rd, cds=cds)

        return (delta_up - delta_down) / bump / 2

    def vega(self, *, spot, sigma, rd, cds, bump=1):
        """
        :param spot: level of spot cds spread in bps/annum
        :param sigma:
        :param rd: flat interest rate for discounting, in practice, one uses the full ISDA swap curve for this
        :param cds: cds object with cds details like maturity, recovery
        :param bump: amount by which underlying is shifted to calculate numerical gamma
        :return: vega, so a return of 0.367 means 36,700 dollars/volatility point/1BB notional of the swaption
          """

        pv_up = self.pv(spot=spot, sigma=sigma + bump / 100, rd=rd, cds=cds)
        pv_down = self.pv(spot=spot, sigma=sigma - bump / 100, rd=rd, cds=cds)

        return (pv_up - pv_down) / bump / 2


if __name__ == '__main__':
    cdxig_payer = CDSSwaption(name='cdxig_payer', trade_date=datetime.datetime(2019, 8, 6),
                              expiry_date=datetime.datetime(2019, 9, 18), pay_or_rec='pay',
                              strike=60, day_count=365, pv_ccy='USD')

    cdxig_rec = CDSSwaption(name='cdxig_rec', trade_date=datetime.datetime(2019, 8, 6),
                            expiry_date=datetime.datetime(2019, 9, 18), pay_or_rec='rec',
                            strike=60, day_count=365, pv_ccy='USD')

    cdxig = CDS(name='CDXIG', trade_date=datetime.datetime(2019, 8, 6),
                expiry_date=datetime.datetime(2024, 6, 20), coupon=100, recovery=.4, day_count=365, pv_ccy='USD')

    print(cdxig_payer)
    print(cdxig_rec)
    print(cdxig, '\n')

    print('Level of Forward to Expiry Date: ',
          cdxig.forward_level(spot=59.5, rd=2.2 / 100, forward_start_date=datetime.datetime(2019, 9, 18)), '\n')

    print('PV in bps upfront of  payer: ', cdxig_payer.pv(spot=59.5, sigma=56 / 100, rd=2.2 / 100, cds=cdxig))
    print('DV01 for  payer: ', cdxig_payer.delta(spot=59.5, sigma=56 / 100, rd=2.2 / 100, cds=cdxig, bump=1))
    print('Gamma for  payer: ', cdxig_payer.gamma(spot=59.5, sigma=56 / 100, rd=2.2 / 100, cds=cdxig, bump=1))

    print('Vega for  payer: ', cdxig_payer.vega(spot=59.5, sigma=56 / 100, rd=2.2 / 100, cds=cdxig), '\n')

    print('PV in bps upfront of ATM rec: ', cdxig_rec.pv(spot=59.5, sigma=56 / 100, rd=2.2 / 100, cds=cdxig))
    print('DV01 for ATM rec: ', cdxig_rec.delta(spot=59.5, sigma=56 / 100, rd=2.2 / 100, cds=cdxig, bump=1))
    print('Gamma for  rec: ', cdxig_rec.gamma(spot=59.5, sigma=56 / 100, rd=2.2 / 100, cds=cdxig, bump=1))
    print('Vega for  rec: ', cdxig_rec.vega(spot=59.5, sigma=56 / 100, rd=2.2 / 100, cds=cdxig))
