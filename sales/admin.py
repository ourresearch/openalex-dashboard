import datetime

from django.contrib import admin, messages
from django.core import serializers
from django.http import HttpResponse
import shortuuid

from sales.heroku_api import HerokuAPI
from sales.models import APIKey, RatelimitExempt
from sales.zendesk_api import ZendeskAPI


class ApiKeyAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "name",
        "key",
        "organization",
        "created",
        "expires",
        "is_demo",
        "active",
        "notes",
        "premium_domain",
        "zendesk_organization_id",
    )
    search_fields = [
        "email",
        "name",
        "key",
        "organization",
        "notes",
        "premium_domain",
        "zendesk_organization_id",
    ]

    actions = ["test_action", "zendesk_sync"]

    def get_form(self, request, obj=None, **kwargs):
        form = super(ApiKeyAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields["key"].initial = shortuuid.uuid()
        # set expires field to one year from now
        form.base_fields["expires"].initial = (
            datetime.date.today() + datetime.timedelta(days=365)
        )
        return form

    def save_model(self, request, obj, form, change: bool) -> None:
        super().save_model(request, obj, form, change)
        # Extra actions:
        self.zendesk_create_or_update(request, obj)

    def has_module_permission(self, request):
        return is_sales_or_superuser(request.user)

    def has_delete_permission(self, request, obj=None):
        return is_sales_or_superuser(request.user)

    def has_view_permission(self, request, obj=None):
        return is_sales_or_superuser(request.user)

    def has_add_permission(self, request):
        return is_sales_or_superuser(request.user)

    def has_change_permission(self, request, obj=None):
        return is_sales_or_superuser(request.user)

    @admin.action(description="Test Action")
    def test_action(self, request, queryset):
        for obj in queryset:
            print(obj.email)
        response = HttpResponse(content_type="application/json")
        serializers.serialize("json", queryset, stream=response)
        return response

    @admin.action(description="Zendesk Sync")
    def zendesk_sync(self, request, queryset):
        for obj in queryset:
            self.zendesk_create_or_update(request, obj)

    def zendesk_create_or_update(self, request, obj):
        zendesk_user = ZendeskAPI(
            email=obj.email,
            name=obj.name,
            organization_id=obj.zendesk_organization_id,
            organization_name=obj.organization,
            domain_name=obj.premium_domain,
        )
        r = zendesk_user.create_or_update_user(premium=True)
        messages.info(request, " -- ".join(r["msg"]))


class RatelimitExemptAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "email",
        "created",
        "expires",
        "active",
        "zendesk_ticket",
        "name",
        "notes",
    )
    search_fields = [
        "email",
        "name",
        "notes",
    ]

    # actions = ["test_action", "zendesk_sync"]

    def get_form(self, request, obj=None, **kwargs):
        form = super(RatelimitExemptAdmin, self).get_form(request, obj, **kwargs)
        # set expires field to one year from now
        form.base_fields["expires"].initial = (
            datetime.date.today() + datetime.timedelta(days=365)
        )
        return form

    def save_model(self, request, obj, form, change: bool) -> None:
        super().save_model(request, obj, form, change)
        # Extra actions:
        heroku_api = HerokuAPI()
        all_objs = RatelimitExempt.objects.filter(active=True)
        emails = ";".join([o.email for o in all_objs])
        update_dict = {"TOP_SECRET_UNLIMITED_EMAILS": emails}
        r = heroku_api.update_config_vars(
            app_name="openalex-api-proxy", update_dict=update_dict
        )
        messages.info(
            request,
            f"heroku api returned status code {r.status_code}. There are {len(all_objs)} rate-limit exempt emails.",
        )

    def has_module_permission(self, request):
        return is_sales_or_superuser(request.user)

    def has_delete_permission(self, request, obj=None):
        return is_sales_or_superuser(request.user)

    def has_view_permission(self, request, obj=None):
        return is_sales_or_superuser(request.user)

    def has_add_permission(self, request):
        return is_sales_or_superuser(request.user)

    def has_change_permission(self, request, obj=None):
        return is_sales_or_superuser(request.user)


def is_sales_or_superuser(user):
    if user.is_superuser:
        return True
    if user.groups.filter(name="Sales").exists():
        return True
    return False


admin.site.register(APIKey, ApiKeyAdmin)
admin.site.register(RatelimitExempt, RatelimitExemptAdmin)
