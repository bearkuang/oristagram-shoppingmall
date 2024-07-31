from django.db import models
from django.db.models import F, Case, When
from shopapp.models.account import User

class Category(models.Model):
    id = models.AutoField(primary_key=True)
    main_cate_name = models.CharField(max_length=20)
    cate_name = models.CharField(max_length=20)

class Item(models.Model):
    id = models.AutoField(primary_key=True)
    cate_no = models.ForeignKey(Category, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=20)
    item_description = models.CharField(max_length=100)
    item_price = models.DecimalField(max_digits=10, decimal_places=0)
    item_create_date = models.DateTimeField(auto_now_add=True)
    item_soldout = models.CharField(max_length=1, default='N')
    item_is_display = models.CharField(max_length=1)
    item_company = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_company': True})
    sales_count = models.IntegerField(default=0)
    likes_count = models.IntegerField(default=0)

    def increment_likes(self, amount=1):
        self.likes_count = F('likes_count') + amount
        self.save(update_fields=['likes_count'])

    def decrement_likes(self, amount=1):
        self.likes_count = F('likes_count') - amount
        self.likes_count = Case(
            When(likes_count__gte=0, then=F('likes_count')),
            default=0
        )
        self.save(update_fields=['likes_count'])

class ItemOption(models.Model):
    id = models.AutoField(primary_key=True)
    item_no = models.ForeignKey(Item, on_delete=models.CASCADE)
    opt_color = models.CharField(max_length=10)
    opt_size = models.CharField(max_length=10, default='FREE')
    opt_item_soldout = models.CharField(max_length=1, default='N')
    opt_stock = models.IntegerField(default=0)

class Review(models.Model):
    id = models.AutoField(primary_key=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='reviews')
    orderproduct_no = models.ForeignKey('OrderProduct', on_delete=models.CASCADE)
    review_star = models.DecimalField(max_digits=1, decimal_places=0)
    review_contents = models.CharField(max_length=150)
    review_create_date = models.DateTimeField(auto_now_add=True)
    review_image = models.ImageField(upload_to='review_images', null=True, blank=True)

class ItemImage(models.Model):
    id = models.AutoField(primary_key=True)
    file = models.ImageField(upload_to='items/', blank=False, null=False)
    item_no = models.ForeignKey(Item, on_delete=models.CASCADE)

class Like(models.Model):
    id = models.AutoField(primary_key=True)
    cust_no = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_company': False})
    item_no = models.ForeignKey(Item, on_delete=models.CASCADE)

class Cart(models.Model):
    id = models.AutoField(primary_key=True)
    cust_no = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_company': False})
    cart_order_amount = models.IntegerField()
    opt_no = models.ForeignKey(ItemOption, on_delete=models.CASCADE)
    cart_create_date = models.DateTimeField(auto_now_add=True)
