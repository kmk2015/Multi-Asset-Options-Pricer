from abc import ABC, abstractmethod
import numpy as np
import scipy.stats as sp
import datetime as datetime
import json



class Instrument(ABC):
    def __init__(self):
        pass

class Option(Instrument):
    def __init__(self, name, trade_date, expiry_date, call_or_put, strike, day_count, pv_ccy):
        self._name = name
        self._trade_date = trade_date
        self._expiry_date = expiry_date
        self._call_or_put = call_or_put
        self._strike = strike
        self._day_count = day_count
        self._pv_ccy = pv_ccy

    def __str__(self):
        return str(json.dumps(self.__dict__,default=str))

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
    def call_or_put(self):
        return self._call_or_put

    @call_or_put.setter
    def call_or_put(self, value):
        if value in ['c', 'call', 'rec', 'receiver', 'p', 'put', 'pay', 'payer']:
            self._call_or_put = value
        else:
            raise Exception("Option Type has to be one of ['c', 'call', 'rec', 'receiver','p','put','pay','payer']")

    @property
    def strike(self):
        return self._strike

    @strike.setter
    def strike(self, value):
        if not (value > 0): raise Exception("strike must be greater than zero")
        self._strike = value

    @property
    def day_count(self):
        return self._day_count

    @day_count.setter
    def day_count(self, value):
        self._day_count = value

    @property
    def pv_ccy(self):
        return self._pv_ccy

    @abstractmethod
    def pv(self):
        pass

    @abstractmethod
    def delta(self):
        pass

    @abstractmethod
    def gamma(self):
        pass

    @abstractmethod
    def vega(self):
        pass

    @staticmethod
    def blackscholes(forward, strike, time_to_expiry, sigma, call_or_put):

        d1 = (np.log(forward / strike) + (0.5 * sigma ** 2) * time_to_expiry) / (sigma * np.sqrt(time_to_expiry))

        d2 = d1 - sigma * np.sqrt(time_to_expiry)

        if call_or_put.lower() in ['call', 'c']:

            price = forward * sp.norm(0, 1).cdf(d1) - strike * sp.norm.cdf(d2)

        elif call_or_put.lower() in ['put', 'p']:

            price = strike * sp.norm.cdf(-d2) - forward * strike * sp.norm.cdf(-d1)

        return price

    @staticmethod
    def blacknormal(forward, strike, time_to_expiry, sigma, call_or_put):

        d = (forward - strike) / (sigma * np.sqrt(time_to_expiry))

        if call_or_put.lower() in ['call', 'c']:

            price = (sp.norm.pdf(d) + d * sp.norm.cdf(d)) * sigma * np.sqrt(time_to_expiry)

        elif call_or_put.lower() in ['put', 'p']:

            price = (sp.norm.pdf(d) - d * sp.norm.cdf(-d)) * sigma * np.sqrt(time_to_expiry)

        return price