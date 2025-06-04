from django.urls import path
from .views import (
    signup, login, resend_otp_view, verify_otp, me,
    reset_password, update_password, update_user,
    create_address, list_addresses, update_address, delete_address
)

urlpatterns = [
    # User
    path('signup/', signup, name='user-signup'),
    path('login/', login, name='user-login'),
    path("resend_otp/", resend_otp_view, name="resend-otp"),
    path("verify-otp/", verify_otp, name="verify-otp"),
    path('me/', me, name='user-me'),
    path('reset-password/', reset_password, name='user-reset-password'),
    path('update-password/', update_password, name='user-update-password'),
    path('update-user/', update_user, name='user-update'),

    # UserAdress

    path('address/create/', create_address, name='address-create'),
    path('address/list/', list_addresses, name='address-list'),
    path('address/<int:pk>/update/', update_address, name='address-update'),
    path('address/<int:pk>/delete/', delete_address, name='address-delete'),
]