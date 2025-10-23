from django.contrib import admin
from .models import Wallet

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'balance')
    search_fields = ('usuario__username',)
