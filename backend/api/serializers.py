"""
Serializers for REST API
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from transactions.models import Transaction, Category, Budget

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """User serializer for registration and profile"""
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone_number', 'currency', 'monthly_budget',
            'email_notifications', 'budget_alert_threshold',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name'
        ]
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class CategorySerializer(serializers.ModelSerializer):
    """Category serializer"""
    transaction_count = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'type', 'description', 'icon', 'color',
            'is_system', 'transaction_count', 'total_amount',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_system', 'created_at', 'updated_at']
    
    def get_transaction_count(self, obj):
        user = self.context['request'].user
        return obj.transactions.filter(user=user).count()
    
    def get_total_amount(self, obj):
        from django.db.models import Sum
        user = self.context['request'].user
        total = obj.transactions.filter(user=user).aggregate(
            total=Sum('amount')
        )['total']
        return float(total) if total else 0.0


class TransactionSerializer(serializers.ModelSerializer):
    """Transaction serializer"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_icon = serializers.CharField(source='category.icon', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'date', 'amount', 'type', 'description',
            'category', 'category_name', 'category_icon', 'category_color',
            'auto_categorized', 'confidence_score',
            'notes', 'receipt_url', 'tags',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'auto_categorized', 'confidence_score',
            'created_at', 'updated_at'
        ]
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class BulkTransactionSerializer(serializers.Serializer):
    """Serializer for bulk transaction upload"""
    file = serializers.FileField()
    
    def validate_file(self, value):
        if not value.name.endswith('.csv'):
            raise serializers.ValidationError("Only CSV files are supported")
        return value


class BudgetSerializer(serializers.ModelSerializer):
    """Budget serializer with spending calculations"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    current_spending = serializers.SerializerMethodField()
    percentage_used = serializers.SerializerMethodField()
    is_over_budget = serializers.SerializerMethodField()
    
    class Meta:
        model = Budget
        fields = [
            'id', 'category', 'category_name', 'amount', 'period',
            'start_date', 'end_date', 'alert_enabled', 'alert_threshold',
            'current_spending', 'percentage_used', 'is_over_budget',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    
    def get_current_spending(self, obj):
        return float(obj.get_spending())
    
    def get_percentage_used(self, obj):
        return obj.get_percentage_used()
    
    def get_is_over_budget(self, obj):
        return obj.is_over_budget()


class AnalyticsSerializer(serializers.Serializer):
    """Serializer for analytics data"""
    total_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_expenses = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_investments = serializers.DecimalField(max_digits=12, decimal_places=2)
    net_savings = serializers.DecimalField(max_digits=12, decimal_places=2)
    transaction_count = serializers.IntegerField()
    average_transaction = serializers.DecimalField(max_digits=12, decimal_places=2)


class SpendingByCategorySerializer(serializers.Serializer):
    """Serializer for spending by category"""
    category = serializers.CharField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    count = serializers.IntegerField()
    percentage = serializers.FloatField()


class MonthlyTrendSerializer(serializers.Serializer):
    """Serializer for monthly trends"""
    month = serializers.CharField()
    income = serializers.DecimalField(max_digits=12, decimal_places=2)
    expenses = serializers.DecimalField(max_digits=12, decimal_places=2)
    investments = serializers.DecimalField(max_digits=12, decimal_places=2)
    net = serializers.DecimalField(max_digits=12, decimal_places=2)
