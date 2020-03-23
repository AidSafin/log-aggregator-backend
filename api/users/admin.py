from django.contrib import admin
from django.contrib.auth import get_user_model

from users.models import UserToken

admin.site.register(get_user_model(), admin.ModelAdmin)
admin.site.register(UserToken, admin.ModelAdmin)
