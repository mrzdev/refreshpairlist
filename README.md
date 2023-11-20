# refreshpairlist :rocket:
## Dynamic Pairlist for FreqAI (freqtrade)  
     
### Installation    
```In your main freqtrade directory, run:```    
```console
  git clone https://github.com/mrzdev/refreshpairlist.git
  cd refreshpairlist
  pip install -r requirements.txt
```    
:arrow_right: Be sure to update *schedule_pairlist_refresh.py* with the actual running strategy values.   
:arrow_right: Remember to correctly configure api_server in your freqtrade configuration file.   

### Usage
```To update pairlist daily, run:```    
```console
  python schedule_pairlist_refresh.py
```    

### Requirements:  
- freqtrade
- requests_ratelimiter
- schedule
