from django.db import models

class Order(models.Model):
    id = models.AutoField(primary_key=True)
    cust_no = models.ForeignKey('Customer', on_delete=models.CASCADE)
    order_create_date = models.DateTimeField(auto_now_add=True)
    order_payment_status = models.CharField(max_length=15, null=True, default='결제완료')
    order_payment_method = models.CharField(max_length=15, default='신용/체크')
    order_total_price = models.DecimalField(max_digits=5, decimal_places=0)
    cust_address = models.CharField(max_length=256)

class OrderProduct(models.Model):
    id = models.AutoField(primary_key=True)
    order_no = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_products')
    order_amount = models.IntegerField()
    opt_no = models.ForeignKey('ItemOption', on_delete=models.CASCADE)
    review_enabled = models.CharField(max_length=255, null=True, default='N')
    order_product_status = models.CharField(max_length=15, default='주문완료')