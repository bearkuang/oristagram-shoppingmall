# Generated by Django 5.0.6 on 2024-06-30 07:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopapp', '0006_item_item_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderproduct',
            name='order_no',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_products', to='shopapp.order'),
        ),
        migrations.AlterField(
            model_name='orderproduct',
            name='order_product_status',
            field=models.CharField(default='주문완료', max_length=15),
        ),
    ]