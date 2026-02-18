"""
Transaction and Category models with Row-Level Security support
"""
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal

class Category(models.Model):
    """
    Transaction categories (both system-defined and user-defined)
    """
    CATEGORY_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
        ('investment', 'Investment'),
    ]
    
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=CATEGORY_TYPES)
    description = models.TextField(blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='categories',
        null=True,
        blank=True,
        help_text="Null for system categories, set for user-defined categories"
    )
    is_system = models.BooleanField(default=False)
    icon = models.CharField(max_length=50, blank=True, help_text="Icon name or emoji")
    color = models.CharField(max_length=7, default='#3B82F6', help_text="Hex color code")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'categories'
        ordering = ['name']
        unique_together = [['name', 'user']]
        indexes = [
            models.Index(fields=['user', 'type']),
            models.Index(fields=['is_system']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.type})"


class Transaction(models.Model):
    """
    Financial transactions with automatic categorization
    Implements Row-Level Security through user foreign key and database policies
    """
    TRANSACTION_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
        ('investment', 'Investment'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transactions',
        db_index=True  # Critical for RLS performance
    )
    
    # Transaction details
    date = models.DateField(db_index=True)
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    description = models.CharField(max_length=500)
    
    # Categorization
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='transactions',
        null=True,
        blank=True
    )
    auto_categorized = models.BooleanField(default=False, help_text="Was this auto-categorized by ML?")
    confidence_score = models.FloatField(null=True, blank=True, help_text="ML confidence score (0-1)")
    
    # Additional fields
    notes = models.TextField(blank=True)
    receipt_url = models.URLField(blank=True)
    tags = models.JSONField(default=list, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'transactions'
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['user', 'category']),
            models.Index(fields=['user', 'type']),
            models.Index(fields=['date']),
        ]
        # PostgreSQL RLS will be enabled through migrations
    
    def __str__(self):
        return f"{self.date} - {self.description} (${self.amount})"
    
    def save(self, *args, **kwargs):
        # Auto-categorize if category not set
        if not self.category and not self.pk:
            from categorization.ml_categorizer import TransactionCategorizer
            categorizer = TransactionCategorizer()
            predicted_category, confidence = categorizer.predict(self.description, self.user)
            if predicted_category and confidence > 0.5:
                self.category = predicted_category
                self.auto_categorized = True
                self.confidence_score = confidence
        
        super().save(*args, **kwargs)


class Budget(models.Model):
    """
    Budget tracking per category
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='budgets',
        db_index=True
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='budgets'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    period = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('yearly', 'Yearly'),
        ],
        default='monthly'
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    alert_enabled = models.BooleanField(default=True)
    alert_threshold = models.IntegerField(default=80, help_text="Alert at % of budget")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'budgets'
        ordering = ['-created_at']
        unique_together = [['user', 'category', 'period', 'start_date']]
        indexes = [
            models.Index(fields=['user', 'start_date', 'end_date']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.category.name} - ${self.amount}/{self.period}"
    
    def get_spending(self):
        """Calculate current spending for this budget period"""
        from django.db.models import Sum
        
        filters = {
            'user': self.user,
            'category': self.category,
            'date__gte': self.start_date,
        }
        
        if self.end_date:
            filters['date__lte'] = self.end_date
        
        total = Transaction.objects.filter(**filters).aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        return total
    
    def get_percentage_used(self):
        """Get percentage of budget used"""
        if self.amount == 0:
            return 0
        spending = self.get_spending()
        return float((spending / self.amount) * 100)
    
    def is_over_budget(self):
        """Check if over budget"""
        return self.get_spending() > self.amount
    
    def should_alert(self):
        """Check if alert should be sent"""
        return self.alert_enabled and self.get_percentage_used() >= self.alert_threshold
