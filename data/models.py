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


class Publisher(models.Model):
    publisher_id = models.BigIntegerField(primary_key=True)
    display_name = models.CharField(max_length=255)
    alternate_titles = models.CharField(max_length=255, blank=True, null=True)
    wikidata_id = models.CharField(max_length=255, blank=True, null=True)
    country_code = models.CharField(max_length=255, blank=True, null=True)
    parent_publisher = models.BigIntegerField(blank=True, null=True)
    ror_id = models.CharField(max_length=255, blank=True, null=True)
    hierarchy_level = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.display_name

    class Meta:
        verbose_name = "Publisher"
        verbose_name_plural = "Publishers"
        db_table = "publisher"


class Journal(models.Model):
    journal_id = models.BigIntegerField(primary_key=True)
    display_name = models.CharField(max_length=255)
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True)
    issn = models.CharField(max_length=10, blank=True, null=True)
    webpage = models.CharField(max_length=255, blank=True, null=True)
    issns = models.JSONField(blank=True, null=True)
    is_oa = models.BooleanField(blank=True, null=True)
    is_in_doaj = models.BooleanField(blank=True, null=True)
    match_name = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    fatcat_id = models.CharField(max_length=255, blank=True, null=True)
    wikidata_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.display_name

    class Meta:
        verbose_name = "Journal"
        verbose_name_plural = "Journals"
        db_table = "journal"
        ordering = ["display_name", "publisher"]
