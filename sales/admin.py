import datetime

from django.contrib import admin
import shortuuid

from sales.models import APIKey


class ApiKeyAdmin(admin.ModelAdmin):
    using = "api_keys"  # this is the name of the database in project/settings.py
    list_display = (
        "email",
        "key",
        "organization",
        "created",
        "expires",
        "is_demo",
        "active",
        "notes",
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super(ApiKeyAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields["key"].initial = shortuuid.uuid()
        # set expires field to one year from now
        form.base_fields[
            "expires"
        ].initial = datetime.date.today() + datetime.timedelta(days=365)
        return form


admin.site.register(APIKey, ApiKeyAdmin)
