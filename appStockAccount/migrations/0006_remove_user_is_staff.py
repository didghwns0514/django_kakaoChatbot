# Generated by Django 3.2.9 on 2022-01-11 17:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appStockAccount', '0005_user_is_staff'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='is_staff',
        ),
    ]
