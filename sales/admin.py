import datetime

from django.contrib import admin
import shortuuid

from sales.models import APIKey


class ApiKeyAdmin(admin.ModelAdmin):
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
