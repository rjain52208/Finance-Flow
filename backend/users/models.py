"""
Custom User model for FinanceFlow
"""
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom User model with additional fields
    """
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    currency = models.CharField(max_length=3, default='USD')
    monthly_budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Email notifications preferences
    email_notifications = models.BooleanField(default=True)
    budget_alert_threshold = models.IntegerField(default=80, help_text="Alert when budget usage exceeds this percentage")
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.email
