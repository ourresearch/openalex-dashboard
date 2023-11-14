import json

import requests

from currency_converter import CurrencyConverter
from django.db import models
from django.core.exceptions import ValidationError


class Concept(models.Model):
    field_of_study_id = models.BigIntegerField(primary_key=True)
    display_name = models.CharField(max_length=255)
    level = models.IntegerField()
    wikidata_id = models.CharField(max_length=255, blank=True, null=True)
    wikipedia_id = models.CharField(max_length=255, blank=True, null=True)
    wikidata_json = models.JSONField(blank=True, null=True, editable=False)
    wikipedia_json = models.JSONField(blank=True, null=True, editable=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.display_name

    @property
    def description(self):
        if self.wikipedia_json:
            try:
                parsed_description = (
                    self.wikipedia_json.get("query", {})
                    .get("pages", {})[0]
                    .get("terms", "")
                    .get("description", "")[0]
                )
            except IndexError:
                parsed_description = None
            return parsed_description

    class Meta:
        verbose_name = "Concept"
        verbose_name_plural = "Concepts"
        db_table = "concept"


class Publisher(models.Model):
    publisher_id = models.BigAutoField(primary_key=True)
    display_name = models.CharField(max_length=255)
    alternate_titles = models.CharField(max_length=255, blank=True, null=True)
    wikidata_id = models.CharField(max_length=255, blank=True, null=True)
    country_code = models.CharField(max_length=255, blank=True, null=True)
    parent_publisher = models.BigIntegerField(blank=True, null=True)
    ror_id = models.CharField(max_length=255, blank=True, null=True)
    hierarchy_level = models.IntegerField(blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.display_name

    def save(self, *args, **kwargs):
        if not self.hierarchy_level:
            self.hierarchy_level = 0
        self.alternate_titles = self.get_alternate_titles()
        self.country_code = self.get_country_code()
        if not self.ror_id:
            self.ror_id = self.find_ror_id()
        super(Publisher, self).save(*args, **kwargs)

    def get_alternate_titles(self):
        wikidata_alternate_titles = self.get_wikidata_alternate_titles()
        ror_alternate_titles = self.get_ror_alternate_titles()
        alternate_titles = []
        if wikidata_alternate_titles:
            alternate_titles.extend(wikidata_alternate_titles)
        if ror_alternate_titles:
            alternate_titles.extend(ror_alternate_titles)
        # remove duplicates
        alternate_titles = list(set(alternate_titles))
        return json.dumps(alternate_titles)

    def get_wikidata_alternate_titles(self):
        if self.wikidata_id:
            wikidata_id = (
                self.wikidata_id.replace("https://wikidata.org/entity/", "")
                .replace("https://www.wikidata.org/entity/", "")
                .replace("https://wikidata.org/wiki/", "")
                .replace("https://www.wikidata.org/wiki/", "")
            )
            url = f"https://www.wikidata.org/w/api.php?action=wbgetentities&ids={wikidata_id}&languages=en&format=json"
            response = requests.get(url)
            if response.status_code == 200:
                json_response = response.json()
                try:
                    alises = (
                        json_response.get("entities", {})
                        .get(wikidata_id, {})
                        .get("aliases", {})
                        .get("en", [])
                    )
                    alternate_titles = [a["value"] for a in alises]
                    return alternate_titles
                except IndexError:
                    return None

    def get_ror_alternate_titles(self):
        if self.ror_id:
            url = f"https://api.ror.org/organizations/{self.ror_id}"
            response = requests.get(url)
            if response.status_code == 200:
                json_response = response.json()
                try:
                    alternate_titles = json_response.get("aliases", [])
                    return alternate_titles
                except IndexError:
                    return None

    def get_country_code(self):
        if self.ror_id:
            url = f"https://api.ror.org/organizations/{self.ror_id}"
            response = requests.get(url)
            if response.status_code == 200:
                json_response = response.json()
                try:
                    country_code = json_response.get("country", {}).get(
                        "country_code", None
                    )
                    return country_code
                except IndexError:
                    return None

    def find_ror_id(self):
        # search by wikidata id
        if self.wikidata_id:
            wikidata_id = (
                self.wikidata_id.replace("https://wikidata.org/entity/", "")
                .replace("https://www.wikidata.org/entity/", "")
                .replace("https://wikidata.org/wiki/", "")
                .replace("https://www.wikidata.org/wiki/", "")
            )
            url = f"https://api.ror.org/organizations?query={wikidata_id}"
            response = requests.get(url)
            if response.status_code == 200:
                json_response = response.json()
                try:
                    ror_id = json_response.get("items", [])[0].get("id", None)
                    return ror_id
                except IndexError:
                    return None

        # then search by name
        url = 'https://api.ror.org/organizations?query="{display_name}"'.format(
            display_name=self.display_name
        )
        response = requests.get(url)
        if response.status_code == 200:
            json_response = response.json()
            try:
                ror_id = json_response.get("items", [])[0].get("id", None)
                return ror_id
            except IndexError:
                return None

    class Meta:
        verbose_name = "Publisher"
        verbose_name_plural = "Publishers"
        db_table = "publisher"


class Journal(models.Model):
    journal_id = models.BigAutoField(primary_key=True)
    display_name = models.CharField(max_length=255)
    publisher_id = models.BigIntegerField(blank=True, null=True)
    issn = models.CharField(max_length=10, blank=True, null=True)
    apc_prices = models.JSONField(blank=True, null=True)
    apc_usd = models.IntegerField(blank=True, null=True)
    apc_found = models.BooleanField(blank=True, null=True)
    merge_into_id = models.BigIntegerField(blank=True, null=True)
    webpage = models.CharField(max_length=255, blank=True, null=True)
    issns = models.JSONField(blank=True, null=True)
    is_oa = models.BooleanField(blank=True, null=True)
    is_in_doaj = models.BooleanField(blank=True, null=True)
    match_name = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    fatcat_id = models.CharField(max_length=255, blank=True, null=True)
    wikidata_id = models.CharField(max_length=255, blank=True, null=True)
    paper_count = models.IntegerField(blank=True, null=True)
    institution_id = models.BigIntegerField(blank=True, null=True)
    publisher_not_found = models.BooleanField(blank=True, null=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.display_name

    def clean(self):
        super().clean()  # keeps the parent class clean() behavior

        try:
            if self.apc_prices:  # if apc_prices is not None or not empty
                # validate each item in the list
                for item in self.apc_prices:
                    if (
                        not isinstance(item, dict)
                        or "price" not in item
                        or "currency" not in item
                    ):
                        raise ValidationError(
                            'Invalid format for apc_prices. Each item must be a dictionary with "price" and "currency" keys'
                        )
                    if not isinstance(item["price"], int):
                        raise ValidationError(
                            "Invalid format for apc_prices. Price should be an integer."
                        )
                    if (
                        not isinstance(item["currency"], str)
                        or len(item["currency"]) != 3
                    ):
                        raise ValidationError(
                            "Invalid format for apc_prices. Currency should be a string that is three letters long."
                        )
        except json.JSONDecodeError:
            raise ValidationError("apc_prices should be a valid JSON string.")

    # set apc_usd based on apc_prices. Use the USD price if available, if not convert to USD using the exchange rate
    def set_apc_usd(self):
        # try usd first
        if self.apc_prices:
            for item in self.apc_prices:
                if item["currency"] == "USD":
                    self.apc_usd = item["price"]
                    break

        # if still not set, convert using the first available currency and convert using currency_converter
        if not self.apc_usd and self.apc_prices:
            currency = self.apc_prices[0]["currency"]
            price = self.apc_prices[0]["price"]
            c = CurrencyConverter()
            self.apc_usd = c.convert(price, currency, "USD")

    def save(self, *args, **kwargs):
        self.clean()
        self.set_apc_usd()
        super().save(*args, **kwargs)  # Call the "real" save() method.

    class Meta:
        verbose_name = "Journal"
        verbose_name_plural = "Journals"
        db_table = "journal"
        ordering = ["-paper_count"]
