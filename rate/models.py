from django.db import models
from user.models import User
from market.models import MarketModel
from product.models import ProductModel

class RateModel(models.Model):
    product = models.ForeignKey(
        ProductModel, 
        on_delete=models.CASCADE, 
        related_name="rates",
        null=True, 
        blank=True
    )
    market = models.ForeignKey(
        MarketModel, 
        on_delete=models.CASCADE, 
        related_name="rates",
        null=True, 
        blank=True
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=300)
    rate = models.FloatField()
    anonym = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.product.name

