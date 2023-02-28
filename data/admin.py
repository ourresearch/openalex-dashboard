from django.contrib import admin

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
        "publisher_id",
        "wikidata_id",
        "paper_count",
        "issns",
        "webpage",
    )
    search_fields = ("display_name", "publisher")
    readonly_fields = (
        "journal_id",
        "display_name",
        "wikidata_id",
        "paper_count",
        "issns",
        "webpage",
    )

    def get_queryset(self, request):
        qs = super(JournalAdmin, self).get_queryset(request)
        return (
            qs.filter(paper_count__gt=0, publisher_id__isnull=True)
            .exclude(type="repository")
            .exclude(institution_id__isnull=False)
        )

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
    search_fields = ("display_name",)
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
