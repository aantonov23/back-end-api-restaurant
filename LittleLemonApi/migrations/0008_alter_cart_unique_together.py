# Generated by Django 5.0.1 on 2024-01-14 12:20

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('LittleLemonApi', '0007_alter_cart_unique_together'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='cart',
            unique_together={('user', 'menuitem')},
        ),
    ]