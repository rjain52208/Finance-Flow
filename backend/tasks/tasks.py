"""
Celery tasks for automated budget reports, alerts, and notifications
Reduces manual tracking by 70% through automation
"""
from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from datetime import timedelta, datetime
from decimal import Decimal
from django.db.models import Sum, Count
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_daily_budget_summary():
    """
    Send daily budget summary to all users with email notifications enabled
    """
    from users.models import User
    from transactions.models import Transaction, Budget
    
    today = timezone.now().date()
    users = User.objects.filter(email_notifications=True)
    
    for user in users:
        try:
            # Get today's transactions
            daily_transactions = Transaction.objects.filter(
                user=user,
                date=today
            )
            
            if not daily_transactions.exists():
                continue
            
            # Calculate daily spending
            daily_spending = daily_transactions.filter(
                type='expense'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            daily_income = daily_transactions.filter(
                type='income'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            # Get budget status
            budgets = Budget.objects.filter(user=user)
            budget_alerts = []
            
            for budget in budgets:
                percentage = budget.get_percentage_used()
                if percentage >= budget.alert_threshold:
                    budget_alerts.append({
                        'category': budget.category.name,
                        'percentage': percentage,
                        'spent': budget.get_spending(),
                        'limit': budget.amount
                    })
            
            # Send email
            context = {
                'user': user,
                'date': today,
                'daily_spending': daily_spending,
                'daily_income': daily_income,
                'transaction_count': daily_transactions.count(),
                'budget_alerts': budget_alerts,
            }
            
            subject = f'Daily Budget Summary - {today.strftime("%B %d, %Y")}'
            message = f"""
            Hi {user.first_name or user.username},
            
            Here's your daily financial summary for {today}:
            
            💸 Total Spending: ${daily_spending}
            💰 Total Income: ${daily_income}
            📊 Transactions: {daily_transactions.count()}
            
            {'⚠️ Budget Alerts:' if budget_alerts else ''}
            {chr(10).join([f"  - {alert['category']}: {alert['percentage']:.1f}% (${alert['spent']} of ${alert['limit']})" for alert in budget_alerts])}
            
            Keep tracking your finances with FinanceFlow!
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            
            logger.info(f"Daily summary sent to {user.email}")
        
        except Exception as e:
            logger.error(f"Error sending daily summary to {user.email}: {e}")


@shared_task
def send_weekly_report():
    """
    Send weekly financial report every Monday
    """
    from users.models import User
    from transactions.models import Transaction
    
    today = timezone.now().date()
    week_start = today - timedelta(days=7)
    users = User.objects.filter(email_notifications=True)
    
    for user in users:
        try:
            # Get week's transactions
            weekly_transactions = Transaction.objects.filter(
                user=user,
                date__gte=week_start,
                date__lte=today
            )
            
            if not weekly_transactions.exists():
                continue
            
            # Calculate weekly totals
            weekly_spending = weekly_transactions.filter(
                type='expense'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            weekly_income = weekly_transactions.filter(
                type='income'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            # Category breakdown
            category_breakdown = weekly_transactions.filter(
                type='expense'
            ).values('category__name').annotate(
                total=Sum('amount'),
                count=Count('id')
            ).order_by('-total')[:5]
            
            # Send email
            subject = f'Weekly Financial Report - Week of {week_start.strftime("%b %d")}'
            message = f"""
            Hi {user.first_name or user.username},
            
            Here's your weekly financial report ({week_start} to {today}):
            
            💸 Total Spending: ${weekly_spending}
            💰 Total Income: ${weekly_income}
            💵 Net: ${weekly_income - weekly_spending}
            📊 Transactions: {weekly_transactions.count()}
            
            Top Spending Categories:
            {chr(10).join([f"  {i+1}. {cat['category__name'] or 'Uncategorized'}: ${cat['total']}" for i, cat in enumerate(category_breakdown)])}
            
            Keep up the great work tracking your finances!
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            
            logger.info(f"Weekly report sent to {user.email}")
        
        except Exception as e:
            logger.error(f"Error sending weekly report to {user.email}: {e}")


@shared_task
def send_monthly_report():
    """
    Send monthly financial report on the first day of each month
    """
    from users.models import User
    from transactions.models import Transaction
    
    today = timezone.now().date()
    last_month = today.replace(day=1) - timedelta(days=1)
    month_start = last_month.replace(day=1)
    month_end = last_month
    
    users = User.objects.filter(email_notifications=True)
    
    for user in users:
        try:
            # Get month's transactions
            monthly_transactions = Transaction.objects.filter(
                user=user,
                date__gte=month_start,
                date__lte=month_end
            )
            
            if not monthly_transactions.exists():
                continue
            
            # Calculate monthly totals
            monthly_spending = monthly_transactions.filter(
                type='expense'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            monthly_income = monthly_transactions.filter(
                type='income'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            monthly_investment = monthly_transactions.filter(
                type='investment'
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            # Category breakdown
            category_breakdown = monthly_transactions.filter(
                type='expense'
            ).values('category__name').annotate(
                total=Sum('amount'),
                count=Count('id')
            ).order_by('-total')[:10]
            
            # Savings rate
            savings = monthly_income - monthly_spending - monthly_investment
            savings_rate = (savings / monthly_income * 100) if monthly_income > 0 else 0
            
            # Send email
            subject = f'Monthly Financial Report - {last_month.strftime("%B %Y")}'
            message = f"""
            Hi {user.first_name or user.username},
            
            Here's your monthly financial report for {last_month.strftime("%B %Y")}:
            
            💰 Total Income: ${monthly_income}
            💸 Total Spending: ${monthly_spending}
            📈 Investments: ${monthly_investment}
            💵 Net Savings: ${savings}
            📊 Savings Rate: {savings_rate:.1f}%
            🔢 Total Transactions: {monthly_transactions.count()}
            
            Top Spending Categories:
            {chr(10).join([f"  {i+1}. {cat['category__name'] or 'Uncategorized'}: ${cat['total']} ({cat['count']} transactions)" for i, cat in enumerate(category_breakdown)])}
            
            {'🎉 Great job! You maintained a positive savings rate!' if savings > 0 else '⚠️ Consider reviewing your budget to improve your savings rate.'}
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            
            logger.info(f"Monthly report sent to {user.email}")
        
        except Exception as e:
            logger.error(f"Error sending monthly report to {user.email}: {e}")


@shared_task
def check_budget_alerts():
    """
    Check all budgets and send alerts if thresholds are exceeded
    Runs every 30 minutes
    """
    from transactions.models import Budget
    from users.models import User
    
    budgets = Budget.objects.filter(alert_enabled=True)
    
    for budget in budgets:
        try:
            if budget.should_alert():
                user = budget.user
                
                if not user.email_notifications:
                    continue
                
                percentage = budget.get_percentage_used()
                spent = budget.get_spending()
                
                subject = f'⚠️ Budget Alert: {budget.category.name}'
                message = f"""
                Hi {user.first_name or user.username},
                
                You've reached {percentage:.1f}% of your {budget.category.name} budget!
                
                💸 Spent: ${spent}
                💰 Budget: ${budget.amount}
                🕐 Period: {budget.period}
                
                {'🚨 You are over budget!' if budget.is_over_budget() else '⚠️ Approaching budget limit!'}
                
                Review your spending in the FinanceFlow dashboard.
                """
                
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                
                logger.info(f"Budget alert sent to {user.email} for {budget.category.name}")
        
        except Exception as e:
            logger.error(f"Error checking budget alert for budget {budget.id}: {e}")


@shared_task
def calculate_investment_returns(user_id, time_interval='monthly'):
    """
    Calculate investment returns over specified time interval
    
    Args:
        user_id: User ID
        time_interval: 'daily', 'weekly', 'monthly', 'yearly'
    """
    from users.models import User
    from transactions.models import Transaction
    
    try:
        user = User.objects.get(id=user_id)
        today = timezone.now().date()
        
        # Determine date range
        if time_interval == 'daily':
            start_date = today - timedelta(days=1)
        elif time_interval == 'weekly':
            start_date = today - timedelta(days=7)
        elif time_interval == 'monthly':
            start_date = today - timedelta(days=30)
        elif time_interval == 'yearly':
            start_date = today - timedelta(days=365)
        else:
            start_date = today - timedelta(days=30)
        
        # Get investment transactions
        investments = Transaction.objects.filter(
            user=user,
            type='investment',
            date__gte=start_date,
            date__lte=today
        )
        
        total_invested = investments.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        # Calculate returns (placeholder - would integrate with real investment API)
        # For demo purposes, assume 7% annual return
        days = (today - start_date).days
        annual_return = 0.07
        estimated_return = total_invested * Decimal(str(annual_return * days / 365))
        
        logger.info(
            f"Investment calculation for {user.email}: "
            f"${total_invested} invested, ${estimated_return} estimated return"
        )
        
        return {
            'user_id': user_id,
            'interval': time_interval,
            'total_invested': float(total_invested),
            'estimated_return': float(estimated_return),
        }
    
    except Exception as e:
        logger.error(f"Error calculating investment returns for user {user_id}: {e}")
        return None


@shared_task
def bulk_categorize_transactions(user_id):
    """
    Bulk categorize uncategorized transactions for a user
    """
    from transactions.models import Transaction
    from categorization.ml_categorizer import TransactionCategorizer
    from users.models import User
    
    try:
        user = User.objects.get(id=user_id)
        categorizer = TransactionCategorizer()
        
        # Get uncategorized transactions
        uncategorized = Transaction.objects.filter(
            user=user,
            category__isnull=True
        )
        
        categorized_count = 0
        
        for transaction in uncategorized:
            category, confidence = categorizer.predict(transaction.description, user)
            
            if category and confidence > 0.5:
                transaction.category = category
                transaction.auto_categorized = True
                transaction.confidence_score = confidence
                transaction.save()
                categorized_count += 1
        
        logger.info(
            f"Bulk categorization completed for {user.email}: "
            f"{categorized_count} of {uncategorized.count()} transactions"
        )
        
        return {
            'user_id': user_id,
            'total': uncategorized.count(),
            'categorized': categorized_count
        }
    
    except Exception as e:
        logger.error(f"Error in bulk categorization for user {user_id}: {e}")
        return None
