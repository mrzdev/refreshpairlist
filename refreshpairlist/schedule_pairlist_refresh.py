from .refresh_pairlist import RefreshPairlist
import argparse, time, logging, functools, schedule
from pathlib import Path
from schedule import every, get_jobs, idle_seconds, run_pending
from typing import Callable, Optional

logging.basicConfig()
schedule_logger = logging.getLogger('schedule')
schedule_logger.setLevel(level=logging.INFO)

# Create the parser
parser = argparse.ArgumentParser(description='Refresh pairlist for Freqtrade.')
# Add the arguments
parser.add_argument('--strategy', type=str, required=True, help='The strategy name to use.')
parser.add_argument('--config', type=str, required=True, help='The configuration file name to update.')
parser.add_argument('--db-name', type=str, required=True, help='The db name of the selected strategy.')
parser.add_argument('--db-url', type=str, required=False, help='The optional db url of the selected strategy. (defaults to main freqtrade directory)')

# Parse the arguments
args = parser.parse_args()

def log_elapsed_time(func: Callable):
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

def find_freqtrade() -> Optional[Path]:
    """
        Find out where freqtrade is installed
    """
    freqtrade_path = None
    try:
        import freqtrade
        # Get the path of the freqtrade module
        freqtrade_module_path = Path(freqtrade.__file__).resolve()
        # Navigate to the parent directory (root of the Freqtrade package)
        freqtrade_path = freqtrade_module_path.parent.parent
    except ImportError:
        schedule_logger.error("Freqtrade installation not found")
        raise ModuleNotFoundError("Freqtrade installation not found. Please install Freqtrade.")
    return freqtrade_path

@log_elapsed_time
def refresh_pairlist():
    """
        Call a pairlist refreshing task
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
    # Resolve the configs_path and db_url relative to the Freqtrade installation path
    freqtrade_path = find_freqtrade()
    db_name = args.db_name
    strategy_name = args.strategy
    partial_config_path = args.config
    config_path = freqtrade_path.joinpath(partial_config_path)
    custom_db_url = args.db_url
    if custom_db_url:
        db_url = f"{custom_db_url}/{db_name}"
    else:
        db_url = f"sqlite:///{freqtrade_path}/{db_name}"
    RefreshPairlist(config_path, db_url, strategy_name)()

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