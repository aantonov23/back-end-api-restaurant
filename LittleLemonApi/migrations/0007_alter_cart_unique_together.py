# Generated by Django 5.0.1 on 2024-01-14 11:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('LittleLemonApi', '0006_orderitem'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='cart',
            unique_together=set(),
        ),
    ]