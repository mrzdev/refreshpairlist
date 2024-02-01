from refresh_pairlist import RefreshPairlist
from schedule import every, get_jobs, idle_seconds, run_pending
import time, logging, functools
from pathlib import Path
from typing import Callable

logging.basicConfig()
schedule_logger = logging.getLogger('schedule')
schedule_logger.setLevel(level=logging.INFO)

def log_elapsed_time(func: Callable) -> Callable:
    """
        log the elapsed time of each job.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_timestamp = time.time()
        schedule_logger.info('Running job "%s"' % func.__name__)
        result = func(*args, **kwargs)
        schedule_logger.info('Job "%s" completed in %d seconds' % (func.__name__, time.time() - start_timestamp))
        return result

    return wrapper

@log_elapsed_time
def refresh_pairlist():
    """
        Call a pairlist refreshing task (you need to fill it with your info):
            configs_path: a folder where your config is stored
                (assuming freqtrade is located up by one directory if cloned!)
            db_url: url of the freqtrade's database to check for open trades as we don't want
                to risk removing the pair with an opened trade
                (assuming freqtrade is located up by one directory if cloned!)
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
    configs_path = Path("../user_data/configs/")
    db_url = "sqlite:///../db.dryrun.sqlite"
    strategy_name = "MyAwesomeStrategy"
    config_name = "freqai_config.json"
    RefreshPairlist(configs_path, db_url, strategy_name, config_name)()

def schedule_task(enable_initial_refresh: bool = True):
    """
        Schedule and wait to run a task.
    """
    if enable_initial_refresh: refresh_pairlist()
    every().day.at("00:00").do(refresh_pairlist)
    while True:
        schedule_logger.info(f"Scheduled task: {get_jobs()}")
        n = idle_seconds()
        if n is None:
            # no more jobs
            break
        elif n > 0:
            # sleep exactly the right amount of time
            time.sleep(n)
        run_pending()

if __name__ == "__main__":
    schedule_task()