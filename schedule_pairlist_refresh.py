from refresh_pairlist import RefreshPairlist
from rocketry import Rocketry
from rocketry.conds import daily
from pathlib import Path

app = Rocketry()

@app.task(daily, execution="async")
def schedule_task():
    """
        Schedule a daily pairlist refreshing task, you need to change it with your info:
            configs_path: a folder where your config is stored
            db_url: url of the freqtrade's database to check for open trades as we don't want
                to risk removing the pair with an opened trade
            config_name: a config name which is being used by the currently running strategy
        Use case:
            Useful for freqai because you can't use dynamic pairlist with refresh period,
            freqai needs a static pairlist to work correctly, but the workaround is to simply
            replace the ["exchange"]["pair_whitelist"] in the configuration file with your desired
            pairlist, and reload the bot using internal freqtrade's api server which you
            need to have configured in order for this to work!
        Note:
            You need permissions to edit the configuration file.
            The refresh_pairlist script changes the bot status to RELOAD_CONFIG and
            it's important to know it won't likely reload the bot instantly. It is
            expected here.
    """
    configs_path = Path("user_data/configs/")
    db_url = "sqlite:///db.dryrun.sqlite"
    strategy_name = "MyAwesomeStrategy"
    config_name = "freqai_config.json"
    RefreshPairlist(configs_path, db_url, strategy_name, config_name)()

if __name__ == "__main__":
    app.run()