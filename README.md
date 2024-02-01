# refreshpairlist :rocket:
## Dynamic Pairlist for FreqAI (freqtrade)  
     
### Installation    
```Install from PyPi:```    
```console
  pip install refreshpairlist
```
:arrow_right: Remember to correctly configure api_server in your freqtrade configuration file.   

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
