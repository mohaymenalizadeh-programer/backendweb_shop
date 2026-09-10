from django.contrib import admin
from .models import Verification, Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'email', 'national_code', 'card_number', 'newsletter')
    search_fields = ('user__username', 'first_name', 'last_name', 'national_code')

admin.site.register(Verification)