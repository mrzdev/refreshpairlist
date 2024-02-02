# refreshpairlist :rocket:
## Dynamic Pairlist for FreqAI (freqtrade)  
     
### Installation    
```console
  pip install refreshpairlist
```
:arrow_right: Remember to correctly configure api_server in your freqtrade configuration file.    
:arrow_right: Feel free to customize remotepairlist params under ["freqai"]["remote_pairlist_params"] in your freqtrade configuration file.

### Usage
```console
  refreshpairlist [-h] --strategy STRATEGY  --config CONFIG --db-name DB_NAME  [--db-url DB_URL]

  --strategy STRATEGY  The strategy name to use.
  --config CONFIG      The target configuration file path.
  --db-name DB_NAME    The db name of the selected strategy.
  --db-url DB_URL      The optional db url of the selected strategy. (defaults to main freqtrade directory)
```   
```To update pairlist daily, run:```    
```console
  refreshpairlist --strategy MyAwesomeStrategy \
                  --config user_data/configs/freqai_config.json \
                  --db-url sqlite:////home/user/freqtrade \
                  --db-name tradesv3.dryrun.sqlite
```    
```The default remotepairlist params set are following:```:
```json
    "remote_pairlist_params": {
      "filter": "meme+cpanic+ftok+leveraged",
      "minv": 0.1,
      "maxv": 0.35,
      "mina": 150,
      "maxa": -1,
      "sort": "marketcap",
      "limit": 11,
      "sort2": "rolling_volume_7"
    }
```
- filter: exclude certain pairs if applies to market    
- minv: min. volatility    
- maxv: max. volatility    
- mina: min. age    
- maxa: max. age    
- sort: sort pairlist by      
- limit: the number of pairs to update with     
- sort2: second sorting method of choice

See [remotepairlist](http://remotepairlist.com/) for more.

### Requirements:  
- freqtrade
- requests_ratelimiter
- schedule