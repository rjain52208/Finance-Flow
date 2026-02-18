"""
ASGI config for financeflow project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financeflow.settings')

application = get_asgi_application()
