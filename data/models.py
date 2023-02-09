from django.db import models


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
