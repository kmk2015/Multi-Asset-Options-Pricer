# Multi-Asset-Options-Pricer
This package contains class files to price vanilla options/swaptions in multiple asset classes:
1. Equity Indices
2. Foreign Exchange
3. Interest Rates Swaptions
4. CDS Swaptions

While some of the details like calendars and day count conventions are not implemented currently, the pricing and greeks are close to what one would one would see when transacting in the market.  

In the case of CDS swaptions, the current pricing module is much faster than a conventional full blown CDS option pricer such as CDSO on bloomberg. The standard/accurate implementations typically involve numerical integration which makes them clunky/slow especially when one is pricing multiple swaptions in a tool like Excel. The pricer in this package is quite valuable when one is trading in fast moving markets or in the case of backtesting on years of data involving pricing 100s of swaptions and speed is important.

Further Work Needed:
1. FX Options 
  a. Implementing Calendars
  b. Implementing correct day counts to account for differences between trade dates, spot value dates, expiry date and expiry value dates.
  c. Returning Delta, Gamma in Notional terms
2. Rates Swaptions
  a. Implementing Calendars
3. CDS Swaptions
  a. Implementing options pricing for price based options (CDXHY)


