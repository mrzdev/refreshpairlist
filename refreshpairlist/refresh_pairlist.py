import logging
import os
import json
import time
from datetime import datetime
from requests_ratelimiter import LimiterSession
from pathlib import Path
from freqtrade.data.btanalysis import load_trades_from_db
from base64 import b64encode

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

class RefreshPairlist:
    """Refresh the freqtrade's pairlist in configuration file and possibly
    reload the bot for changes to take effect while using freqai-oriented
    strategies."""

    def __init__(self, config_path: Path, db_url: str, strategy_name: str):
        """
        :param config_path: the path to the folder where your configuration file is
        :param db_url: url of freqtrade's trades db
        :param strategy_name: the name of the currently running freqtrade strategy
        """
        self._config_path = config_path
        self._db_url = db_url
        self._strategy_name = strategy_name
        # just a protection to not spam anything in case of an incorrect usage
        self._session = LimiterSession(per_minute=5)

    # TODO: pull info from configuration file here
    @staticmethod
    def get_pairlist_robot_params() -> dict:
        """User-defined parameters for the pairlist.robot api request, adjust
        to your needs:

        filter: filter out some pairs
        minv: min. volatility
        maxv: max. volatility
        mina: min. age (see train_period_days parameter in your config)
        maxa: max. age
        sort: sort pairlist by
        exchange: set the same as in your config
        market: set the same as in your config
        limit: the number of pairs to update with
        stake: see "stake_currency" in your config
        stake_currency: see "stake_currency" in your config
        sort2: second sorting method of choice
        """
        params = dict(
            r=1,
            filter="meme+cpanic+ftoken+leveraged",
            minv=0.1,
            maxv=0.35,
            mina=150,
            maxa=-1,
            sort="marketcap",
            exchange="binance",
            market="futures",
            stake="USDT",
            limit=11,
            stake_currency="USDT",
            sort2="rolling_volume_7"
        )
        return params

    def get_pairlist(self) -> list:
        """Request the pairlist with user-defined settings from the
        pairlist.robot api."""
        logger.info(f"Pulling a fresh pairlist from http://remotepairlist.com/")
        params = self.get_pairlist_robot_params()
        url = "http://remotepairlist.com/"
        try:
            resp_json = self._session.request('GET', url, params=params, timeout=30).json()
            fresh_pairlist = resp_json["pairs"]
        except Exception:
            fresh_pairlist = []
        return fresh_pairlist

    def replace_config_whitelist(self, requested_pairlist: list) -> list:
        """Replace the pair_whitelist with updated pairlist excluding the ones
        that are blacklisted."""
        with open(self._config_path, "r+") as jsonFile:
            config = json.load(jsonFile)
            jsonFile.truncate(0)
            jsonFile.seek(0)
            filtered_pairlist = [c for c in requested_pairlist \
                        if c not in config["exchange"]["pair_blacklist"]]
            config["exchange"]["pair_whitelist"] = filtered_pairlist
            json.dump(config, jsonFile, indent=4)
            jsonFile.close()
        return filtered_pairlist

    def is_trade_opened(self) -> bool:
        """Check if any trade is currently opened."""
        logger.info(f"Checking for open trades...")
        trades = load_trades_from_db(self._db_url, self._strategy_name)
        is_trade_open = trades.is_open.any()
        return is_trade_open

    @staticmethod
    def get_settings_from_config(config) -> dict:
        """Retrieve crucial information from the config dictionary."""
        user_info = dict(
            ip_address=config.get("api_server", {}).get("listen_ip_address", None),
            listen_port=config.get("api_server", {}).get("listen_port", None),
            username=config.get("api_server", {}).get("username", None),
            password=config.get("api_server", {}).get("password", None)
        )
        return user_info

    def get_access_token(self, username: str, password: str, ip_address: str, port: str) -> str:
        """Login to the api server to obtain the Bearer access token."""
        login = f"{username}:{password}"
        base64_hash = b64encode(login.encode()).decode('UTF-8')
        headers = {
            "Authorization": f"Basic {base64_hash}"
        }
        url = f"http://{ip_address}:{port}/api/v1/token/login"
        try:
            resp_json = self._session.request('POST', url, headers=headers, timeout=30).json()
        except Exception:
            resp_json = {}
        access_token = resp_json.get('access_token', None)
        return access_token

    def reload_bot(self) -> None:
        """Reload the bot leveraging info provided in the configuration
        file."""
        with open(self._config_path, "r+") as jsonFile:
            config = json.load(jsonFile)
            jsonFile.close()
        user_info = self.get_settings_from_config(config)
        ip_address = user_info["ip_address"]
        port = user_info["listen_port"]
        username = user_info["username"]
        password = user_info["password"]
        access_token = self.get_access_token(username, password, ip_address, port)
        if access_token:
            url = f"http://{ip_address}:{port}/api/v1/reload_config"
            headers = {
                "Authorization": f"Bearer {access_token}"
            }
            resp_json = self._session.request('POST', url, headers=headers, timeout=30).json()
            status = resp_json.get("status", "")
            logger.info(f"Setting bot status to: {status}")
        else:
            logger.warning(f"Obtaining access token failed - check your config")

    def __call__(self) -> None:
        """Refresh the pairlist in the configuration file and reload the
        bot."""
        if not self.is_trade_opened():
            updated_pairlist = self.get_pairlist()
            if len(updated_pairlist) > 0:
                current_whitelist = self.replace_config_whitelist(updated_pairlist)
                logger.info(f"Updated the {self._config_path} pairlist to {current_whitelist}")
                logger.info(f"Reloading the bot...")
                self.reload_bot()
        else:
            logger.warning(f"Trade detected, skipping")
