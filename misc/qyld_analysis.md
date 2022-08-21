# Can I use this a replacement for covered call ETFs?

Answer: It is a replacement for covered call ETF's yes, but there are some key differences, like shown below on the example "QYLD".

## Comparison to the QYLD covered call ETF

This bot was actually first created to be a drop in replacement for QYLD, with no fees and high adjustability in strategy (also it allows you to cover with options instead of shares which is nice).

The bot follows the same basic principles as QYLD, but has some important differences.


1. This bot sells cc's on QQQ, not the NDX directly like QYLD

2. This bot rolls the sold contracts (meaning buys them back before expiration)
   
   QYLD doesn't need to do that, because they sell cash settled options (meaning on expiration you don't get assigned shares, you just pay cash if they are ITM)

3. This bot liquidates the cc's the day before expiration, 30 minutes after market open

   QYLD's options are also liquidated on the day before expiration, but directly at market open. Also it happens automatically (they sell AM european-style options)

4. This bot will sell a new covered call at the same time it buys the expiring one's back, QYLD sells new contracts only on monday after expiry date

5. The bot itself doesn't have any expenses. If you run the bot with QQQ shares, you have to pay the expense ratio of this ETF of 0.20%
   
   With QYLD the expense ratio is 0.60% at the time of writing

The expiration dates on the cc's are the same.


**Coverage**

The bot can cover with either shares or call options of the underlying stock.

QYLD buys every single stock in the nasdaq and uses that to cover.

**Revenue**:

100% of the revenue this bot makes stays in cash. It does not sell or buy any underlying stocks.

QYLD distributes the lower of a) half of the premiums received or b) 1% of NAV as dividends. The rest of the received premium is reinvested into the fund.


**What if the bot / QYLD doesn't generate any revenue in a month?**

This can be the case if the nasdaq goes up massively, and we would have to sell the new cc's with less premium than the current ones are worth.

The bot would just pay for the roll in this case instead of receiving premium (if 'rollWithoutDebit' is disabled).

QYLD would sell off stocks to get the cash for buying back the cc's (I am pretty sure thats how they handle it, however I didn't find a credible source for this, so please fact check me on this one).

---

Also, for the bot to behave like QYLD, you would have to set everything in your QQQ config settings to 0 or False (except 'amountOfHundreds').


Sources:

https://www.globalxetfs.com/funds/qyld/

Especially the “Top Holdings” table where you can see exactly what calls QYLD sells (at the very bottom).

https://www.globalxetfs.com/content/files/Covered-Call-Rpt-21jun24.pdf
