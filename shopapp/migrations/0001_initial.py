# Generated by Django 5.0.6 on 2024-06-27 12:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('main_cate_name', models.CharField(max_length=20)),
                ('cate_name', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='CompanyAccount',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('company_id', models.CharField(max_length=20, unique=True)),
                ('company_pwd', models.CharField(max_length=20)),
                ('activate', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('cust_username', models.CharField(max_length=20, unique=True)),
                ('cust_name', models.CharField(max_length=50)),
                ('cust_password', models.CharField(max_length=20)),
                ('cust_gender', models.CharField(default='F', max_length=1, null=True)),
                ('cust_birthday', models.DateField(null=True)),
                ('cust_address', models.CharField(max_length=256)),
                ('cust_email', models.CharField(max_length=256)),
                ('cust_create_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ManagerAccount',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('manager_id', models.CharField(max_length=20, unique=True)),
                ('manager_pwd', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('item_name', models.CharField(max_length=20)),
                ('item_price', models.DecimalField(decimal_places=0, max_digits=10)),
                ('item_create_date', models.DateTimeField(auto_now_add=True)),
                ('item_soldout', models.CharField(default='N', max_length=1)),
                ('item_is_display', models.CharField(max_length=1)),
                ('item_company', models.CharField(max_length=30)),
                ('cate_no', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shopapp.category')),
            ],
        ),
        migrations.CreateModel(
            name='ItemImage',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('file', models.ImageField(upload_to='items/')),
                ('item_no', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shopapp.item')),
            ],
        ),
        migrations.CreateModel(
            name='ItemOption',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('opt_color', models.CharField(max_length=10)),
                ('opt_size', models.CharField(default='FREE', max_length=5)),
                ('opt_item_soldout', models.CharField(default='N', max_length=1)),
                ('opt_stock', models.IntegerField(default=0)),
                ('item_no', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shopapp.item')),
            ],
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('cart_order_amount', models.IntegerField()),
                ('cart_create_date', models.DateTimeField(auto_now_add=True)),
                ('cust_no', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shopapp.customer')),
                ('opt_no', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shopapp.itemoption')),
            ],
        ),
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('cust_no', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shopapp.customer')),
                ('item_no', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shopapp.item')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('order_create_date', models.DateTimeField(auto_now_add=True)),
                ('order_payment_status', models.CharField(default='결제완료', max_length=15, null=True)),
                ('order_payment_method', models.CharField(default='신용/체크', max_length=15)),
                ('order_total_price', models.DecimalField(decimal_places=0, max_digits=5)),
                ('cust_address', models.CharField(max_length=256)),
                ('cust_no', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shopapp.customer')),
            ],
        ),
        migrations.CreateModel(
            name='OrderProduct',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('order_no', models.IntegerField()),
                ('order_amount', models.IntegerField()),
                ('review_enabled', models.CharField(default='N', max_length=255, null=True)),
                ('order_product_status', models.CharField(max_length=15)),
                ('opt_no', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shopapp.itemoption')),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('review_star', models.DecimalField(decimal_places=0, max_digits=1)),
                ('review_contents', models.CharField(max_length=150)),
                ('review_create_date', models.DateTimeField(auto_now_add=True)),
                ('review_image', models.CharField(default='0', max_length=300, null=True)),
                ('orderproduct_no', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shopapp.orderproduct')),
            ],
        ),
    ]