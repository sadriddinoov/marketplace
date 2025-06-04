from django.db import models

class MarketModel(models.Model):
    name = models.CharField(max_length=300)
    description = models.TextField()
    location = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

