from django.contrib import admin

from data.models import Concept


class ConceptAdmin(admin.ModelAdmin):
    list_display = (
        "field_of_study_id",
        "display_name",
        "wikidata_id",
        "created_date",
        "updated_date",
    )
    search_fields = ("display_name",)
    readonly_fields = (
        "field_of_study_id",
        "description",
        "created_date",
        "updated_date",
    )

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Concept, ConceptAdmin)
