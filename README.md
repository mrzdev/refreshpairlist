# refreshpairlist :rocket:
## Dynamically refresh pairlist of your freqai strategy (freqtrade)  
:arrow_right: Be sure to edit *schedule_pairlist_refresh.py* with your running strategy information.  
:arrow_right: Remember to correctly configure api_server in your freqtrade configuration file.        

To update pairlist daily just run:    

__`python schedule_pairlist_refresh.py`__

### Requirements:  
- requests_ratelimiter
- rocketry
