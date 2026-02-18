"""
REST API Views with Row-Level Security
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from datetime import timedelta, datetime
from decimal import Decimal
import csv
import io

from .serializers import (
    UserSerializer, UserRegistrationSerializer,
    TransactionSerializer, CategorySerializer, BudgetSerializer,
    BulkTransactionSerializer, AnalyticsSerializer,
    SpendingByCategorySerializer, MonthlyTrendSerializer
)
from transactions.models import Transaction, Category, Budget
from tasks.tasks import bulk_categorize_transactions, calculate_investment_returns

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    User management viewset
    RLS: Users can only access their own data
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # RLS: Users can only see their own profile
        return User.objects.filter(id=self.request.user.id)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """Update current user profile"""
        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """User registration endpoint"""
    serializer = UserRegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    
    return Response({
        'message': 'User registered successfully',
        'user': UserSerializer(user).data
    }, status=status.HTTP_201_CREATED)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    Category management viewset
    RLS: Users see system categories + their own custom categories
    """
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    
    def get_queryset(self):
        # RLS: System categories + user's custom categories
        return Category.objects.filter(
            Q(is_system=True) | Q(user=self.request.user)
        )
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user, is_system=False)


class TransactionViewSet(viewsets.ModelViewSet):
    """
    Transaction management viewset with automatic categorization
    RLS: Users can only access their own transactions
    """
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['description', 'notes']
    ordering_fields = ['date', 'amount', 'created_at']
    ordering = ['-date', '-created_at']
    
    def get_queryset(self):
        # RLS: Users can only see their own transactions
        queryset = Transaction.objects.filter(user=self.request.user)
        
        # Additional filters
        transaction_type = self.request.query_params.get('type', None)
        category = self.request.query_params.get('category', None)
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if transaction_type:
            queryset = queryset.filter(type=transaction_type)
        if category:
            queryset = queryset.filter(category_id=category)
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def bulk_upload(self, request):
        """
        Bulk upload transactions from CSV file
        Expected format: date,amount,type,description,category(optional)
        """
        serializer = BulkTransactionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        csv_file = request.FILES['file']
        decoded_file = csv_file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)
        
        created_count = 0
        errors = []
        
        for row_num, row in enumerate(reader, start=2):
            try:
                transaction_data = {
                    'date': row.get('date'),
                    'amount': row.get('amount'),
                    'type': row.get('type', 'expense'),
                    'description': row.get('description'),
                }
                
                # Optional category
                category_name = row.get('category', '').strip()
                if category_name:
                    category = Category.objects.filter(
                        Q(name__iexact=category_name, user=request.user) |
                        Q(name__iexact=category_name, is_system=True)
                    ).first()
                    if category:
                        transaction_data['category'] = category.id
                
                trans_serializer = TransactionSerializer(
                    data=transaction_data,
                    context={'request': request}
                )
                
                if trans_serializer.is_valid():
                    trans_serializer.save()
                    created_count += 1
                else:
                    errors.append({
                        'row': row_num,
                        'errors': trans_serializer.errors
                    })
            
            except Exception as e:
                errors.append({
                    'row': row_num,
                    'error': str(e)
                })
        
        return Response({
            'message': f'Uploaded {created_count} transactions',
            'created': created_count,
            'errors': errors
        })
    
    @action(detail=False, methods=['post'])
    def bulk_categorize(self, request):
        """Trigger bulk categorization of uncategorized transactions"""
        task = bulk_categorize_transactions.delay(request.user.id)
        return Response({
            'message': 'Bulk categorization started',
            'task_id': task.id
        })


class BudgetViewSet(viewsets.ModelViewSet):
    """
    Budget management viewset
    RLS: Users can only access their own budgets
    """
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # RLS: Users can only see their own budgets
        return Budget.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Get detailed budget status"""
        budget = self.get_object()
        
        return Response({
            'budget': BudgetSerializer(budget, context={'request': request}).data,
            'spending': float(budget.get_spending()),
            'remaining': float(budget.amount - budget.get_spending()),
            'percentage_used': budget.get_percentage_used(),
            'is_over_budget': budget.is_over_budget(),
            'should_alert': budget.should_alert(),
        })


class AnalyticsViewSet(viewsets.ViewSet):
    """
    Analytics endpoints for financial insights
    RLS: All analytics are user-specific
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get financial summary for specified period"""
        period = request.query_params.get('period', 'month')  # day, week, month, year
        
        today = timezone.now().date()
        
        if period == 'day':
            start_date = today
        elif period == 'week':
            start_date = today - timedelta(days=7)
        elif period == 'month':
            start_date = today - timedelta(days=30)
        elif period == 'year':
            start_date = today - timedelta(days=365)
        else:
            start_date = today - timedelta(days=30)
        
        transactions = Transaction.objects.filter(
            user=request.user,
            date__gte=start_date,
            date__lte=today
        )
        
        total_income = transactions.filter(type='income').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        total_expenses = transactions.filter(type='expense').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        total_investments = transactions.filter(type='investment').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        net_savings = total_income - total_expenses - total_investments
        
        transaction_count = transactions.count()
        average_transaction = transactions.aggregate(
            avg=Avg('amount')
        )['avg'] or Decimal('0.00')
        
        data = {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'total_investments': total_investments,
            'net_savings': net_savings,
            'transaction_count': transaction_count,
            'average_transaction': average_transaction,
        }
        
        serializer = AnalyticsSerializer(data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def spending_by_category(self, request):
        """Get spending breakdown by category"""
        period = request.query_params.get('period', 'month')
        today = timezone.now().date()
        
        if period == 'month':
            start_date = today - timedelta(days=30)
        elif period == 'year':
            start_date = today - timedelta(days=365)
        else:
            start_date = today - timedelta(days=30)
        
        spending_data = Transaction.objects.filter(
            user=request.user,
            type='expense',
            date__gte=start_date,
            date__lte=today
        ).values('category__name').annotate(
            amount=Sum('amount'),
            count=Count('id')
        ).order_by('-amount')
        
        total = sum(item['amount'] for item in spending_data if item['amount'])
        
        result = []
        for item in spending_data:
            amount = item['amount'] or Decimal('0.00')
            percentage = float((amount / total * 100)) if total > 0 else 0
            result.append({
                'category': item['category__name'] or 'Uncategorized',
                'amount': amount,
                'count': item['count'],
                'percentage': percentage
            })
        
        serializer = SpendingByCategorySerializer(result, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def monthly_trends(self, request):
        """Get monthly income/expense trends for the past year"""
        today = timezone.now().date()
        months = []
        
        for i in range(12):
            month_date = today - timedelta(days=30*i)
            month_start = month_date.replace(day=1)
            
            if month_date.month == 12:
                month_end = month_date.replace(day=31)
            else:
                next_month = month_date.replace(month=month_date.month + 1, day=1)
                month_end = next_month - timedelta(days=1)
            
            transactions = Transaction.objects.filter(
                user=request.user,
                date__gte=month_start,
                date__lte=month_end
            )
            
            income = transactions.filter(type='income').aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0.00')
            
            expenses = transactions.filter(type='expense').aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0.00')
            
            investments = transactions.filter(type='investment').aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0.00')
            
            months.append({
                'month': month_start.strftime('%B %Y'),
                'income': income,
                'expenses': expenses,
                'investments': investments,
                'net': income - expenses - investments
            })
        
        months.reverse()
        serializer = MonthlyTrendSerializer(months, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def calculate_investment_returns(self, request):
        """Calculate investment returns"""
        interval = request.data.get('interval', 'monthly')
        task = calculate_investment_returns.delay(request.user.id, interval)
        
        return Response({
            'message': 'Investment calculation started',
            'task_id': task.id
        })
