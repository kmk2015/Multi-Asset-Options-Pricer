from Instrument import Instrument
import datetime as datetime
import json
import numpy as np


class CDS(Instrument):
    """
    This is a CDX class to calculate approximate levels of annuities and forwards.
    The approximations here are good enough to use to price spread based options on cdxig, itraxx main and snr-fin
    These approximations have been checked versus market quotes and the values produced are within market bid ask
    Price based options on CDXHY can also be priced by first converting price based spot and strike levels into
    spread based levels
    """
    def __init__(self, *, name, trade_date, expiry_date, coupon, recovery, day_count, pv_ccy):
        """
        :param name: name
        :param trade_date: date time
        :param expiry_date: cds maturity date, datetime
        :param coupon: couppn in bps/annum
        :param recovery: cds recovery rate
        :param day_count: days in year, full day count conventions will be implemented in later versions
        :param pv_ccy:
        """
        self._name = name
        self._trade_date = trade_date
        self._expiry_date = expiry_date
        self._coupon = coupon
        self._recovery = recovery
        self._day_count = day_count
        self._pv_ccy = pv_ccy

    def __str__(self):
        return str(json.dumps(self.__dict__, default=str))

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def trade_date(self):
        return self._trade_date

    @trade_date.setter
    def trade_date(self, value):
        if isinstance(value, datetime.datetime):
            self._trade_date = value
        else:
            raise Exception("trade_date must be of type datetime.datetime")

    @property
    def expiry_date(self):
        return self._expiry_date

    @expiry_date.setter
    def expiry_date(self, value):
        if isinstance(value, datetime.datetime):
            self._expiry_date = value
        else:
            raise Exception("expiry_date must be of type datetime.datetime")

    @property
    def day_count(self):
        return self._day_count

    @day_count.setter
    def day_count(self, value):
        self._day_count = value


    @property
    def coupon(self):
        return self._coupon

    @coupon.setter
    def coupon(self, value):
        self._coupon = value

    @property
    def pv_ccy(self):
        return self._pv_ccy

    def pv(self, spot, rd):
        pass

    def hazard_rate(self, *, spot):
        """
        :param spot: level of spot cds spread in bps/annum
        :return: hazard rate in absolute units
        """
        return spot/(1-self._recovery)/1e4*365/360

    def forward_annuity(self, *, spot, rd, forward_start_date):
        """
        :param spot: level of spot cds spread in bps/annum
        :param rd: flat interest rate for discounting, in practice, one uses the full ISDA swap curve for this
        :param forward_start_date: starting day of the CDS forward
        :return: returns the annuity of a CDS forward
        """
        time_fraction =  (self._expiry_date - forward_start_date).days / self._day_count
        hazard_rate = spot/1e4/(1 - self._recovery)
        pv01 = (1 - np.exp(-(hazard_rate + rd )*time_fraction))/(hazard_rate + rd)*365/360
        return pv01

    def forward_level(self, *, spot, rd, forward_start_date):
        """
        :param spot: level of spot cds spread in bps/annum
        :param rd: flat interest rate for discounting, in practice, one uses the full ISDA swap curve for this
        :param forward_start_date: starting day of the CDS forward
        :return: level of forward, approximate but very good when compared to dealer calculations for 3 months and less
        """
        time_fraction =  (forward_start_date - self._trade_date).days / self._day_count
        pv01 = self.forward_annuity(spot=spot, rd=rd, forward_start_date=forward_start_date)
        return spot + spot* time_fraction/pv01


if __name__=='__main__':
    cdxig = CDS(name= 'CDXIG', trade_date = datetime.datetime(2019, 8,6),expiry_date=datetime.datetime(2024,6,20),
                coupon = 100, recovery = 0.4, day_count=365, pv_ccy='USD')
    print(cdxig)
    forward_annuity = cdxig.forward_annuity(spot=59.5, rd=0.022, forward_start_date=datetime.datetime(2019,8,6))
    print(forward_annuity)
