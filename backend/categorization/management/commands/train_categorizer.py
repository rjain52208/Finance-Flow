from django.core.management.base import BaseCommand
from categorization.ml_categorizer import TransactionCategorizer
from transactions.models import Category

class Command(BaseCommand):
    help = 'Train the transaction categorization model'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-categories',
            action='store_true',
            help='Create default system categories before training',
        )

    def handle(self, *args, **options):
        if options['create_categories']:
            self.stdout.write('Creating default system categories...')
            self.create_default_categories()
        
        self.stdout.write('Training transaction categorization model...')
        
        categorizer = TransactionCategorizer()
        accuracy = categorizer.train()
        
        self.stdout.write(
            self.style.SUCCESS(f'Model trained successfully with {accuracy*100:.2f}% accuracy')
        )
    
    def create_default_categories(self):
        """Create default system categories"""
        categories = [
            # Expense categories
            {'name': 'Groceries', 'type': 'expense', 'icon': '🛒', 'color': '#10B981'},
            {'name': 'Dining', 'type': 'expense', 'icon': '🍽️', 'color': '#F59E0B'},
            {'name': 'Transportation', 'type': 'expense', 'icon': '🚗', 'color': '#3B82F6'},
            {'name': 'Utilities', 'type': 'expense', 'icon': '💡', 'color': '#8B5CF6'},
            {'name': 'Entertainment', 'type': 'expense', 'icon': '🎬', 'color': '#EC4899'},
            {'name': 'Healthcare', 'type': 'expense', 'icon': '🏥', 'color': '#EF4444'},
            {'name': 'Shopping', 'type': 'expense', 'icon': '🛍️', 'color': '#F97316'},
            {'name': 'Housing', 'type': 'expense', 'icon': '🏠', 'color': '#0EA5E9'},
            {'name': 'Education', 'type': 'expense', 'icon': '📚', 'color': '#6366F1'},
            {'name': 'Fitness', 'type': 'expense', 'icon': '💪', 'color': '#14B8A6'},
            {'name': 'Travel', 'type': 'expense', 'icon': '✈️', 'color': '#06B6D4'},
            {'name': 'Insurance', 'type': 'expense', 'icon': '🛡️', 'color': '#64748B'},
            {'name': 'Subscriptions', 'type': 'expense', 'icon': '📱', 'color': '#A855F7'},
            {'name': 'Personal Care', 'type': 'expense', 'icon': '💅', 'color': '#F472B6'},
            {'name': 'Pets', 'type': 'expense', 'icon': '🐕', 'color': '#FB923C'},
            {'name': 'Charity', 'type': 'expense', 'icon': '❤️', 'color': '#DC2626'},
            {'name': 'Taxes', 'type': 'expense', 'icon': '📋', 'color': '#475569'},
            
            # Income categories
            {'name': 'Income', 'type': 'income', 'icon': '💰', 'color': '#22C55E'},
            
            # Investment categories
            {'name': 'Investment', 'type': 'investment', 'icon': '📈', 'color': '#3B82F6'},
        ]
        
        for cat_data in categories:
            Category.objects.get_or_create(
                name=cat_data['name'],
                is_system=True,
                defaults=cat_data
            )
            self.stdout.write(f"  ✓ {cat_data['name']}")
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(categories)} system categories'))
