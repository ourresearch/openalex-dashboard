from django.contrib import admin
from django.utils.html import format_html


from data.models import Concept, Journal, Publisher


class ConceptAdmin(admin.ModelAdmin):
    list_display = (
        "field_of_study_id",
        "display_name",
        "wikidata_id",
        "created_date",
        "updated_date",
    )
    fields = (
        "field_of_study_id",
        "display_name",
        "description",
        "wikidata_id",
        "wikipedia_id",
        "level",
        "created_date",
        "updated_date",
    )
    search_fields = ("display_name",)
    readonly_fields = (
        "field_of_study_id",
        "description",
        "display_name",
        "level",
        "created_date",
        "updated_date",
    )

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


class JournalAdmin(admin.ModelAdmin):
    list_display = ("journal_id", "display_name", "paper_count")
    fields = (
        "journal_id",
        "display_name",
        "apc_prices",
        "apc_found",
        "webpage_link",
        "publisher_id",
        "wikidata_id",
        "publisher_not_found",
        "paper_count",
        "issns",
    )
    search_fields = ("display_name", "journal_id")
    readonly_fields = (
        "journal_id",
        "display_name",
        "wikidata_id",
        "paper_count",
        "issns",
    )

    def get_queryset(self, request):
        qs = super(JournalAdmin, self).get_queryset(request)
        return qs.filter(
            paper_count__gt=0, apc_prices=[], is_in_doaj=False, apc_found__isnull=True
        ).exclude(type="repository")

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_module_permission(self, request):
        return is_editor_or_superuser(request.user)

    def has_view_permission(self, request, obj=None):
        return is_editor_or_superuser(request.user)

    def has_change_permission(self, request, obj=None):
        return is_editor_or_superuser(request.user)

    def webpage_link(self, obj):
        if obj.webpage:
            return format_html("<a href='{url}'>{url}</a>", url=obj.webpage)
        else:
            return "-"

    webpage_link.short_description = "Webpage"  # Sets column name in admin


class PublisherAdmin(admin.ModelAdmin):
    list_display = (
        "publisher_id",
        "display_name",
        "wikidata_id",
    )
    fields = (
        "publisher_id",
        "display_name",
        "wikidata_id",
        "ror_id",
        "alternate_titles",
        "country_code",
        "is_approved",
    )
    list_filter = ("is_approved",)
    search_fields = ("display_name", "publisher_id", "alternate_titles", "wikidata_id")
    readonly_fields = ("publisher_id", "alternate_titles", "country_code")

    # permissions

    def has_module_permission(self, request):
        return is_editor_or_superuser(request.user)

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return is_editor_or_superuser(request.user)

    def has_add_permission(self, request):
        return is_editor_or_superuser(request.user)

    def has_change_permission(self, request, obj=None):
        return is_editor_or_superuser(request.user)


def is_editor_or_superuser(user):
    if user.is_superuser:
        return True
    if user.groups.filter(name="Editors").exists():
        return True
    return False


admin.site.register(Concept, ConceptAdmin)
admin.site.register(Journal, JournalAdmin)
admin.site.register(Publisher, PublisherAdmin)
