from rest_framework import serializers
from .models import Customer, ManagerAccount, CompanyAccount, Item, ItemImage, ItemOption, Category, Cart, Order, OrderProduct, Like, Review

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'cust_username', 'cust_name', 'cust_password', 'cust_gender', 'cust_birthday', 'cust_address', 'cust_email', 'cust_create_date']

class ManagerSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = ManagerAccount
        fields = ['id', 'manager_id', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        manager = ManagerAccount.objects.create(**validated_data)
        manager.set_password(password)
        manager.save()
        return manager

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyAccount
        fields = ['id', 'company_id', 'company_pwd']
        
class ItemImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemImage
        fields = ['id', 'file', 'item_no']

class ItemOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemOption
        fields = ['id', 'item_no', 'opt_color', 'opt_size', 'opt_item_soldout', 'opt_stock']
        
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'main_cate_name', 'cate_name']

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'review_star', 'review_contents', 'review_create_date', 'review_image']
        
class ItemSerializer(serializers.ModelSerializer):
    cate_no = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=True)
    images = ItemImageSerializer(many=True, read_only=True, source='itemimage_set')
    options = ItemOptionSerializer(many=True, read_only=True, source='itemoption_set')
    category = CategorySerializer(source='cate_no', read_only=True)
    likes = serializers.SerializerMethodField()
    reviews = ReviewSerializer(many=True, read_only=True)
    item_description = serializers.CharField(max_length=100)

    class Meta:
        model = Item
        fields = ['id', 'cate_no', 'category', 'item_name', 'item_description', 'item_price', 'item_soldout', 'item_is_display', 'item_company', 'images', 'options', 'likes', 'reviews']

    def get_likes(self, obj):
        return Like.objects.filter(item_no=obj).count()
    
class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'cust_no', 'cart_order_amount', 'opt_no', 'cart_create_date']
        
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'cust_no', 'order_create_date', 'order_payment_status', 'order_payment_method', 'order_total_price', 'cust_address']
        
class OrderProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderProduct
        fields = ['id', 'order_no', 'order_amount', 'order_payment_status', 'order_payment_method', 'order_total_price', 'cust_address']
        
class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'cust_no', 'item_no']