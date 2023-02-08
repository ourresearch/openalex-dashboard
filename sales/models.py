from django.db import models


class APIKey(models.Model):
    email = models.CharField(max_length=255, null=False, unique=True)
    key = models.CharField(max_length=255, null=False)
    created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True, null=False)
    expires = models.DateField(null=True)
    is_demo = models.BooleanField(default=False, null=False)
    organization = models.CharField(max_length=500, null=True, blank=True)
    notes = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        db_table = "api_key"

    def __str__(self):
        return self.email
