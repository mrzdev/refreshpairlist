# refreshpairlist :rocket:
## Dynamic Pairlist for FreqAI (freqtrade)  
     
### Installation    
```console
  pip install refreshpairlist
```
:arrow_right: Remember to correctly configure api_server in your freqtrade configuration file.
:arrow_right: Customize remotepairlist params under ["freqai"]["remote_pairlist_params"] as you wish in your freqtrade configuration file, the defaults are following:

```json
    "remote_pairlist_params": {
      "filter": "meme+cpanic+ftok+leveraged",
      "minv": 0.1,
      "maxv": 0.35,
      "mina": 150,
      "maxa": -1,
      "sort": "marketcap",
      "exchange": "binance",
      "market": "futures",
      "stake": "USDT",
      "limit": 11,
      "stake_currency": "USDT",
      "sort2": "rolling_volume_7"
    }
```
filter: filter out some pairs

minv: min. volatility

maxv: max. volatility

mina: min. age 

maxa: max. age

sort: sort pairlist by

exchange: set the same as in your config

market: set the same as in your config

limit: the number of pairs to update with

stake: see "stake_currency" in your config

stake_currency: see "stake_currency" in your config

sort2: second sorting method of choice
See [remotepairlist](http://remotepairlist.com/) for more.
### Usage
```console
  refreshpairlist [-h] --strategy STRATEGY  --config CONFIG --db-name DB_NAME  [--db-url DB_URL]

  --strategy STRATEGY  The strategy name to use.
  --config CONFIG      The configuration file name to update.
  --db-name DB_NAME    The db name of the selected strategy.
  --db-url DB_URL      The optional db url of the selected strategy. (defaults to main freqtrade directory)
```   
```To update pairlist daily, run:```    
```console
  refreshpairlist --strategy MyAwesomeStrategy --config user_data/configs/freqai_config.json --db-url sqlite:////home/user/freqtrade --db-name tradesv3.dryrun.sqlite
```    

### Requirements:  
- freqtrade
- requests_ratelimiter
- schedule
