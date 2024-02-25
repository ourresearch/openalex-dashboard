import os
from functools import cached_property
import requests


class ZendeskAPI:
    """An instance of this object represents one API Key associated with one user (email) and (optionally) an organization (domain)"""

    def __init__(
        self,
        email=None,
        name=None,
        organization_id=None,
        organization_name=None,
        domain_name=None,
    ) -> None:
        self.base_url = os.getenv("ZENDESK_API_BASE_URL")
        self.user = os.getenv("ZENDESK_USER_ACCOUNT")
        self.token = os.getenv("ZENDESK_API_TOKEN")
        self.auth = (f"{self.user}/token", self.token)

        self.email = email
        self.name = name
        self.organization_id = organization_id
        self.organization_name = organization_name
        self.domain_name = domain_name

    @cached_property
    def zendesk_user_id(self):
        return self.get_zendesk_user_id_from_email()

    def query_search_by_email(self, email):
        url = f'{self.base_url}/users/search.json'
        params = {
            'query': f'email:{email}'
        }
        print("making query")
        r = requests.get(url, params=params, auth=self.auth)
        r.raise_for_status()
        num_results = r.json()['count']
        if num_results == 1:
            return r.json()['users'][0]
        elif num_results == 0:
            return None
        else:
            raise RuntimeError(f"found {num_results} with email {email}")

    def get_zendesk_user_id_from_email(self):
        user = self.query_search_by_email(self.email)
        if user:
            return user['id']
        else:
            return None

    def create_user(self, premium=True):
        ret = {"msg": []}
        if self.name:
            name = self.name
        else:
            name = self.email
        user = {"email": self.email, "name": name}
        if not self.organization_id and self.organization_name is not None:
            user["organization"] = {"name": self.organization_name}
        if premium is True:
            user["tags"] = ["premium"]
        url = f'{self.base_url}/users.json'
        body = {"user": user}
        params = {"skip_verify_email": True}
        r = requests.post(url, params=params, json=body, auth=self.auth)
        if r.status_code > 299:
            ret["msg"].append("Error adding new user in Zendesk.")
        else:
            ret["msg"].append(f"Added new user in Zendesk: {self.email} ({r.json()['user']['id']})")
        return ret

    def update_user(self, premium=True):
        ret = {"msg": []}
        if self.name:
            user = {"name": self.name}
            url = f'{self.base_url}/users/{self.zendesk_user_id}.json'
            body = {"user": user}
            r = requests.put(url, json=body, auth=self.auth)
            if r.status_code > 299:
                ret["msg"].append(f"Error encountered updating user in Zendesk.")
            else:
                ret["msg"].append(f"Updated user in Zendesk: {self.email} ({self.zendesk_user_id})")
        if premium is True:
            url = f'{self.base_url}/users/{self.zendesk_user_id}/tags.json'
            body = {"tags": ["premium"]}
            r = requests.put(url, json=body, auth=self.auth)
            if r.status_code > 299:
                ret["msg"].append("Error encountered adding premium tag in Zendesk.")
            else:
                ret["msg"].append(f"Added premium tag to Zendesk user: {self.email} ({self.zendesk_user_id})")
        return ret

    def create_or_update_user(self, premium=True):
        """create or update user in zendesk with all available info"""
        if self.zendesk_user_id:
            return self.update_user(premium=premium)
        else:
            return self.create_user(premium=premium)
