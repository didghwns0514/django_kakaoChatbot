# Generated by Django 3.1.7 on 2021-02-27 18:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parseapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stocklistdata',
            name='timestamp',
            field=models.DateTimeField(auto_now=True),
        ),
    ]