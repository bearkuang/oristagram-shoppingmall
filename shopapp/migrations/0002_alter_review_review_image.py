# Generated by Django 5.0.6 on 2024-07-04 12:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='review_image',
            field=models.ImageField(blank=True, null=True, upload_to='review_images'),
        ),
    ]
