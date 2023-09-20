# refreshpairlist :rocket:
## Dynamic Pairlist for FreqAI (freqtrade)  
:arrow_right: Be sure to edit *schedule_pairlist_refresh.py* with your running strategy information.  
:arrow_right: Remember to correctly configure api_server in your freqtrade configuration file.        

To update pairlist daily just run:    

__`python schedule_pairlist_refresh.py`__

### Requirements:  
- requests_ratelimiter
- rocketry  

Update: There is an ongoing rocketry issue with the pydantic v2 versions (causing dependency conflict with freqtrade).  
The hotfix is to install both rocketry and red-bird from these forks until the fixes get merged: 
```
pip install git+https://github.com/ManiMozaffar/rocketry
pip install git+https://github.com/ManiMozaffar/red-bird
```
