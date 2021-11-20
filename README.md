# OPI - Option passive income bot


**IN DEVELOPMENT!!!**

## Preface

Do not use this bot without understanding the risks behind it. You can lose all your money!

If you don't understand what's written here or what the code of this bot does, then dont use it!


## Factsheet

This bot seeks to generate passive income from option premiums through writing covered calls on stocks and ETF's

The bot will sell a covered call each month on the assets you select

The covered call will always be the first OTM call (current asset price + 1$, adjustable in the configuration for more growth)

The bot buys back (rolls) the option contract each month, one day before expiration

---

You need to own at least 100 of the underlying asset you want the bot to sell the covered calls on

Alternatively you can also hold a deep ITM call option (LEAP) representing said asset

(ATTENTION! the bot does not check if you actually have the amount you say you have in the configuration)

---

Also, you should have some spare cash in the account to pay for rollup costs (roll to a higher strike price with less premium than the current one)

If you want to prohibit this, you can set the "rollCalendar" setting in the config to True

Know that this option when used constantly will decline your returns more and more, as the asset climbs higher and the extrinsic value of that option falls



### Risks

Volatility risk - Less volatility, more spread, less option premium

Do not use this bot with assets that have low volatility or too few options

General risks with stocks and options

If you want to use this bot you should know about the risks investing in the stock market and especially options.


### Configuration

    # how many cc's to write
    'amountOfHundreds': 1,

    # only buy cc's at or over current asset price + this value
    'minGapToATM': 1,

    # don't write cc's with strikes below this value
    # if this is ITM, ATM price gets used instead
    'minStrike': 0,

    # write cc's around this far out, bot gets the nearest contract possible
    'days': 31,

    # allow x days less or more
    'daysSpread': 10,

    # only write that cc if you can get this value or above in premium
    'minYield': 300,

    # if we need to roll, only roll calendar (OVERWRITES minGapToATM, minStrike and minYield!!!)
    'rollCalendar': False,

    # None, email ### what should happen if the bot can't find a cc with the given configuration to write
    'writeRequirementsNotMetAlert': None



