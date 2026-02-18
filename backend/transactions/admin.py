from django.contrib import admin
from .models import Category, Transaction, Budget

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'user', 'is_system', 'created_at']
    list_filter = ['type', 'is_system', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['date', 'user', 'description', 'amount', 'type', 'category', 'auto_categorized', 'created_at']
    list_filter = ['type', 'auto_categorized', 'date', 'created_at']
    search_fields = ['description', 'notes', 'user__email']
    ordering = ['-date', '-created_at']
    date_hierarchy = 'date'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(user=request.user)
        return qs

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'amount', 'period', 'start_date', 'end_date', 'get_percentage_used']
    list_filter = ['period', 'alert_enabled', 'created_at']
    search_fields = ['user__email', 'category__name']
    ordering = ['-created_at']
    
    def get_percentage_used(self, obj):
        return f"{obj.get_percentage_used():.1f}%"
    get_percentage_used.short_description = 'Budget Used'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(user=request.user)
        return qs
