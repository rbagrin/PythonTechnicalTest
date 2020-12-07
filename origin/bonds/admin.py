from django.contrib import admin

from .models import Bond

@admin.register(Bond)
class BondAdmin(admin.ModelAdmin):
    list_display = ['isin', 'size', 'currency', 'maturity', 'lei', 'user']
