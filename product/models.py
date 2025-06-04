from django.db import models
from market.models import MarketModel

class ProductModel(models.Model):
    market = models.ForeignKey(MarketModel,on_delete=models.CASCADE,related_name="product")
    name = models.CharField(max_length=300)
    description = models.TextField()
    category = models.CharField(max_length=300)
    price = models.PositiveIntegerField()
    discount = models.PositiveIntegerField()
    available = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

