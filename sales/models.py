from django.db import models
from functools import cached_property


class APIKey(models.Model):
    email = models.CharField(max_length=255, null=False, unique=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    key = models.CharField(max_length=255, null=False)
    created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True, null=False)
    expires = models.DateField(null=True)
    is_demo = models.BooleanField(default=False, null=False)
    organization = models.CharField(max_length=500, null=True, blank=True)
    notes = models.CharField(max_length=500, null=True, blank=True)
    premium_domain = models.CharField(max_length=255, null=True, blank=True)
    zendesk_organization_id = models.BigIntegerField(null=True, blank=True)

    class Meta:
        db_table = "api_key"
        verbose_name = "API Key"
        verbose_name_plural = "API Keys"

    def __str__(self):
        return self.email

    @cached_property
    def zendesk_api(self):
        from sales.zendesk_api import ZendeskAPI

        return ZendeskAPI(
            email=self.email,
            organization_id=self.zendesk_organization_id,
            organization_name=self.organization,
            domain_name=self.premium_domain,
        )

class RatelimitExempt(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=255, null=False, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    expires = models.DateField(null=True, blank=True)
    zendesk_ticket = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    notes = models.CharField(max_length=255, null=True, blank=True)
    active = models.BooleanField(default=True, null=False)

    class Meta:
        db_table = "ratelimit_exempt"
        verbose_name = "High Rate-Limit Email"
        verbose_name_plural = "High Rate-Limit Emails"