# Generated by Django 5.0.6 on 2024-07-27 05:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopapp', '0005_orderproduct_delivery_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='sales_count',
            field=models.IntegerField(default=0),
        ),
    ]
