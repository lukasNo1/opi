# OPI - Option passive income bot

### Requirements

- A TD Ameritrade account with options privileges
- All python packages from requirements.txt installed
- General understanding of the stock market and options

If you don't understand what's written here or what the code of this bot does, then don't use it!

### Setup instructions

1. Register and create an app on [developer.tdameritrade.com](https://developer.tdameritrade.com/) to get an api key
2. copy configuration.example.py to configuration.py and adjust it to your needs
3. Run setupApi.py to get an api token
4. Run main.py

## Factsheet

This bot seeks to generate passive income from option premiums through writing covered calls on stocks and ETF's

The bot will sell a covered call each month on the assets you select

The covered call will be the first OTM call per default (current asset price + 1$, adjustable in the configuration for more growth)

The bot buys back (rolls) the option contract each month, one day before expiration

---

You need to own at least 100 of the underlying asset you want the bot to sell the covered calls on

Alternatively you can also hold an ITM call option (preferably deep ITM LEAP) representing said asset

The bot will check if you actually have enough shares or options in the account to cover the cc's

---

### Configuration

    # how many cc's to write
    'amountOfHundreds': 1,

    # only write cc's at or over current asset price + this value
    'minGapToATM': 1,

    # don't write cc's with strikes below this value
    'minStrike': 0,

    # only write that cc if you can get this value or above in premium (per contract)
    'minYield': 3.00,

    # prevent paying for rollups (can override minGapToATM, minStrike and minYield if ITM!)
    'rollWithoutDebit': True,

    # if we can't get filled on an order, how much is the bot allowed to
    # reduce the price from mid price to try and get a fill (percentage 0-100)
    'allowedPriceReductionPercent': 2

The bot will inform you about important events either directly in the console or over email.

(For emails you need to add credentials for a smtp server in configuration.py and set the 'botAlert' setting to "email")

### CC expiration date

The bot will try to write a cc which expires on the third friday of next month.
If that date is not available because it falls on a holiday f.ex., it will write a cc with expiration on the thursday preceding said friday

If you are running the bot the first time on an asset and there is enough time left, it will write the cc's on the third friday of the **current** month

### Rollups: Further explanation

A 'rollup' is the process of rolling to a higher strike price than the current one.

The setting `rollWithoutDebit` is enabled by default.

If you deactivate it, you should have some spare cash in the account to pay for rollup costs, because the new contract can have less premium than the current one,
if the asset price went up.

If `rollWithoutDebit` is enabled, the bot will roll to a contract with the strike being the ATM price + `minGapToATM` (normal behavior).

If that results in debit, it rolls to the highest possible contract with credit instead (current cc strike price as minimum).

### Risks

**Volatility risk** - Less volatility, more spread, less option premium

Do not use this bot with assets that have low volatility or too few options

**Options** - Covered calls are the least risky options, nonetheless, if you don't know what you're doing or fuck up the configuration above, you can lose a lot or even all of your money

**Selling free contracts** - It should be obvious, but do not set the `allowedPriceReductionPercent` config to 100 as that can result in a 100% price reduction
which allows the bot to give away the options for free.

### Quick analysis: Is this a drop in replacement for covered call ETFs (like QYLD)?
If you're interested: [Analysis](misc/qyld_analysis.md)