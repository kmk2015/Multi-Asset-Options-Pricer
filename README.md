# Multi-Asset-Options-Pricer
This is options pricer for options on multiple asset classes:
1. Equity Indices
2. Foreign Exchange
3. Interest Rates Swaptions
4. CDS Swaptions

While some of the details like calendars and day count conventions are not implemented currently, the pricing and greeks are close to what one would one would see when transacting in the market.  

In the case of CDS swaptions, the current pricing module is much faster than a conventional full blown CDS option pricer such as CDSO on bloomberg. The standard/accurate implementations typically involve numerical integration which makes them clunky/slow especially when one is pricing multiple swaptions in a tool like Excel. The pricer in this package is quite valuable when one is trading in fast moving markets or in the case of backtesting on years of data involving pricing 100s of swaptions and speed is important.

