from django.db import models
from django.contrib.auth.models import User

class MothSighting(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # === ALL MAPMATE COLUMNS ===
    code = models.CharField("Code", max_length=20, blank=True, default="")
    taxon = models.CharField("Taxon (Scientific Name)", max_length=300)
    vernacular = models.CharField("Vernacular (Common Name)", max_length=300, blank=True, default="")
    location = models.CharField("Site / Location", max_length=300, blank=True, default="")
    grid_reference = models.CharField("Grid Ref", max_length=20, blank=True, default="")
    county = models.CharField("Vice County", max_length=100, blank=True, default="Suffolk")
    quantity = models.IntegerField("Quantity", default=1)
    stage = models.CharField("Stage", max_length=50, blank=True, default="")
    sighting_date = models.DateField("Date Sighted")
    recorder = models.CharField("Recorder", max_length=200, blank=True, default="")
    determiner = models.CharField("Determiner", max_length=200, blank=True, default="")
    method = models.CharField("Method", max_length=200, blank=True, default="")
    comment = models.TextField("Comment", blank=True, default="")
    
    # Extra fields
    status = models.CharField("Status", max_length=100, blank=True, default="")
    refers_to = models.CharField("Refers To", max_length=300, blank=True, default="")
    weather = models.CharField("Weather / Conditions", max_length=200, blank=True, default="")

    class Meta:
        ordering = ['-sighting_date']

    def __str__(self):
        return f"{self.taxon} — {self.sighting_date}"