# Multi-Asset-Options-Pricer
This is options pricer for options on multiple asset classes:
1. Equity Indices
2. Foreign Exchange
3. Interest Rates Swaptions
4. CDS Swaptions

While some of the details like calendars and day count conventions are not implemented currently, based on my experience, the pricing and greeks are close to what one would one would see when transacting in the market and in the case of CDS swaptions, much faster than a conventional full blown CDS option pricer - whose standard implementations typically involve numerical integration. This is quite valuable when one is trading in fast moving markets or in the case of backtesting where speed is important. 

