from django.contrib import admin
from userauths.models import User, Profile

class UserAdmin(admin.ModelAdmin):
    search_fields  = ['username', 'email', 'id']
    list_filter = ['roles']
    list_display = ['username', 'email', 'roles', 'id']
    list_per_page = 500

class ProfileAdmin(admin.ModelAdmin):
    search_fields  = ['user', 'shop_name']
    list_display = ['user', 'full_name', 'profile_image', 'wallet']
    list_per_page = 1000


admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)