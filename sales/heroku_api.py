import os
from functools import cached_property
from typing import Dict
import requests


class HerokuAPI:
    """connect to the Heroku API"""

    def __init__(
        self,
    ) -> None:
        self.base_url = "https://api.heroku.com/apps"
        self.token = os.getenv("HEROKU_API_KEY")
        self.headers = {
            "Accept": "application/vnd.heroku+json; version=3",
            "Authorization": f"Bearer: {self.token}",
        }

    def get_config_vars(self, app_name: str) -> Dict:
        url = f"{self.base_url}/{app_name}/config-vars"
        r = requests.get(url, headers=self.headers)
        r.raise_for_status()
        return r.json()

    def update_config_vars(self, app_name: str, update_dict: Dict) -> requests.Response:
        url = f"{self.base_url}/{app_name}/config-vars"
        headers = self.headers
        headers["Content-Type"] = "application/json"
        print(f"token: {self.token[:10]}...{self.token[-4:]}")

        #debugging:
        r = requests.get(url, headers=headers)
        print(f"debug: status code: {r.status_code}")
        config_vars = r.json()
        print("content")
        print(r.content)
        print("headers")
        print(r.headers)

        r = requests.patch(url, headers=headers, json=update_dict)
        print(r)
        print(r.content)
        # r.raise_for_status()
        return r
