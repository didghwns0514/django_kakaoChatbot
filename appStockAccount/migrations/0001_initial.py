# Generated by Django 3.2.9 on 2022-01-02 21:49

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('user_id', models.IntegerField(primary_key=True, serialize=False)),
                ('user_name', models.CharField(max_length=200)),
                ('user_regday', models.DateTimeField(default=django.utils.timezone.now)),
                ('user_payedday', models.DateTimeField(null=True)),
                ('user_isactive', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='MyStocks',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stock_number', models.IntegerField(default=0)),
                ('user_id', models.ForeignKey(default='dummy', on_delete=django.db.models.deletion.CASCADE, to='appStockAccount.user')),
            ],
        ),
    ]
