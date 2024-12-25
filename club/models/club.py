from django.db import models


class Club(models.Model):
    def __str__(self):
        return self.name

    name = models.CharField(max_length=255)
    image_url = models.CharField(max_length=255, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "clubs"
