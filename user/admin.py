from django.contrib import admin
from .models import User, UserAddress, OTP


admin.site.register(User)
admin.site.register(UserAddress)
admin.site.register(OTP)