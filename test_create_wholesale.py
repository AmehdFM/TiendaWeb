import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tiendaderopademo.settings')
django.setup()

from store.models import WholesaleClient

print("Creating wholesale client...")
client = WholesaleClient.objects.create(
    name="Test Script Client",
    company="Test Co",
    is_active=True
)
print(f"Success! Client ID: {client.id}")
