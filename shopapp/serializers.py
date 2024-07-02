from rest_framework import serializers
from .models import User, Item, ItemImage, ItemOption, Category, Cart, Order, OrderProduct, Like, Review

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'name', 'gender', 'birthday', 'address', 'email', 'create_date', 'is_staff', 'is_active', 'is_company']
        
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user

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
    option = ItemOptionSerializer(source='opt_no', read_only=True)
    item = ItemSerializer(source='opt_no.item_no', read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'item', 'option', 'cart_order_amount', 'cart_create_date']
        
class OrderProductSerializer(serializers.ModelSerializer):
    item = ItemSerializer(source='opt_no.item_no', read_only=True)
    option = ItemOptionSerializer(source='opt_no', read_only=True)
    
    class Meta:
        model = OrderProduct
        fields = ['id', 'item', 'option', 'order_amount', 'review_enabled', 'order_product_status']

class OrderSerializer(serializers.ModelSerializer):
    order_products = OrderProductSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'cust_no', 'order_create_date', 'order_payment_status', 'order_payment_method', 'order_total_price', 'cust_address', 'order_products']
        
class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'cust_no', 'item_no']
