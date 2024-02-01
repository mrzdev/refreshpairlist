import logging
import os
import json
import time
from datetime import datetime
from requests_ratelimiter import LimiterSession
from pathlib import Path
from freqtrade.data.btanalysis import load_trades_from_db
from base64 import b64encode
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

class RefreshPairlist:
    """
        Refresh the freqtrade's pairlist in configuration file and possibly
        reload the bot for changes to take effect while using freqai-oriented
        strategies.
    """

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

    def read_config(self) -> Optional[Dict]:
        """
            Read the config file by provided path
        """
        config = None
        with open(self._config_path, "r+") as jsonFile:
            config = json.load(jsonFile)
            jsonFile.close()
        return config

    @staticmethod
    def get_remote_pairlist_params(config: Optional[Dict]) -> Dict:
        """
            User-defined parameters for the remotepairlist api request.
            Customize to your needs in your config file under 
            ["freqai"]["remote_pairlist_params"]:

            filter: exclude certain pairs if applies to market
            minv: min. volatility
            maxv: max. volatility
            mina: min. age
            maxa: max. age
            sort: sort pairlist by
            limit: the number of pairs to update with
            sort2: second sorting method of choice
        """
        config_remote_pairlist_params = \
            config.get("freqai", {}).get("remote_pairlist_params", None)
        # default params
        exchange = config.get("exchange", {}).get("name", "binance")
        market = config.get("trading_mode", "futures")
        stake_currency = config.get("stake_currency", "USDT")
        params = dict(
            r=1,
            filter="meme+cpanic+ftoken+leveraged",
            minv=0.1,
            maxv=0.35,
            mina=150,
            maxa=-1,
            sort="marketcap",
            exchange=exchange,
            market=market,
            stake=stake_currency,
            limit=11,
            stake_currency=stake_currency,
            sort2="rolling_volume_7"
        )
        if config_remote_pairlist_params is not None:
            params.update(config_remote_pairlist_params)
        return params

    def get_pairlist(self, config: Optional[Dict]) -> List:
        """
            Request the pairlist with user-defined settings from the
            remotepairlist api.
        """
        logger.info(f"Pulling a fresh pairlist from http://remotepairlist.com/")
        params = self.get_remote_pairlist_params(config)
        url = "http://remotepairlist.com/"
        try:
            resp_json = self._session.request('GET', url, params=params, timeout=30).json()
            fresh_pairlist = resp_json["pairs"]
        except Exception:
            fresh_pairlist = []
        return fresh_pairlist

    def replace_config_whitelist(self, requested_pairlist: List) -> List:
        """
            Replace the pair_whitelist with updated pairlist excluding the ones
            that are blacklisted.
        """
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
        """
            Check if any trade is currently opened.
        """
        logger.info(f"Checking for open trades...")
        trades = load_trades_from_db(self._db_url, self._strategy_name)
        is_trade_open = trades.is_open.any()
        return is_trade_open

    @staticmethod
    def get_settings_from_config(config: Optional[Dict]) -> Dict:
        """
            Retrieve auth information from the config dictionary.
        """
        user_info = dict(
            ip_address=config.get("api_server", {}).get("listen_ip_address", None),
            listen_port=config.get("api_server", {}).get("listen_port", None),
            username=config.get("api_server", {}).get("username", None),
            password=config.get("api_server", {}).get("password", None)
        )
        return user_info

    def get_access_token(self, username: Optional[str], password: Optional[str], ip_address: Optional[str], port: Optional[str]) -> Optional[str]:
        """
            Login to the api server to obtain the Bearer access token.
        """
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

    def reload_bot(self, config: Optional[Dict]) -> None:
        """
            Reload the bot leveraging info provided in the configuration file.
        """
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
        """
            Refresh the pairlist in the configuration file and reload the bot.
        """
        if not self.is_trade_opened():
            config = self.read_config()
            updated_pairlist = self.get_pairlist(config)
            if len(updated_pairlist) > 0:
                current_whitelist = self.replace_config_whitelist(updated_pairlist)
                logger.info(f"Updated the {self._config_path} pairlist to {current_whitelist}")
                logger.info(f"Reloading the bot...")
                self.reload_bot(config)
        else:
            logger.warning(f"Trade detected, skipping")
