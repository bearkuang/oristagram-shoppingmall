# Generated by Django 5.0.6 on 2024-06-29 13:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopapp', '0005_review_item'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='item_description',
            field=models.CharField(default='깔금하고 단정한 여름 오피스 룩', max_length=100),
            preserve_default=False,
        ),
    ]