# Generated by Django 5.0.6 on 2024-08-03 12:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopapp', '0010_alter_review_orderproduct_no'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderproduct',
            name='order_no',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='order_products', to='shopapp.order'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='review',
            name='orderproduct_no',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='shopapp.orderproduct'),
            preserve_default=False,
        ),
    ]
