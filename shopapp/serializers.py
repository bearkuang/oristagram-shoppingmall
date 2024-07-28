from rest_framework import serializers
from django.db.models import Count, Avg
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
    customer_username = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id', 'orderproduct_no', 'item', 'review_star', 'review_contents', 'review_image', 'review_create_date', 'customer_username']

    def get_customer_username(self, obj):
        return obj.orderproduct_no.order_no.cust_no.username

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'email']

class ItemSerializer(serializers.ModelSerializer):
    cate_no = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=True)
    images = ItemImageSerializer(many=True, read_only=True, source='itemimage_set')
    options = ItemOptionSerializer(many=True, read_only=True, source='itemoption_set')
    category = CategorySerializer(source='cate_no', read_only=True)
    likes = serializers.IntegerField(source='likes_count', read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    item_description = serializers.CharField(max_length=100)
    item_company = CompanySerializer(read_only=True)
    rating_stats = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    sales_count = serializers.IntegerField(read_only=True)
    poplularity_score = serializers.FloatField(read_only=True)

    class Meta:
        model = Item
        fields = ['id', 'cate_no', 'category', 'item_name', 'item_description', 'item_price', 'item_soldout', 'item_is_display', 'item_company', 'images', 'options', 'likes', 'reviews', 'rating_stats', 'average_rating', 'sales_count', 'poplularity_score']

    def get_likes(self, obj):
        return Like.objects.filter(item_no=obj).count()
    
    def get_rating_stats(self, obj):
        stats = Review.objects.filter(item=obj).aggregate(
            total=Count('id'),
            average=Avg('review_star')
        )
        rating_counts = Review.objects.filter(item=obj).values('review_star').annotate(count=Count('review_star'))
        
        return {
            'total_reviews': stats['total'],
            'average_rating': round(stats['average'], 2) if stats['average'] else None,
            'rating_stats': {str(item['review_star']): item['count'] for item in rating_counts}
        }
    
    def get_average_rating(self, obj):
        avg = Review.objects.filter(item=obj).aggregate(Avg('review_star'))['review_star__avg']
        return round(avg, 2) if avg else None
    
class CartSerializer(serializers.ModelSerializer):
    option = ItemOptionSerializer(source='opt_no', read_only=True)
    item = ItemSerializer(source='opt_no.item_no', read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'item', 'option', 'cart_order_amount', 'cart_create_date']
        
class OrderProductSerializer(serializers.ModelSerializer):
    item = ItemSerializer(source='opt_no.item_no', read_only=True)
    option = ItemOptionSerializer(source='opt_no', read_only=True)
    company = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderProduct
        fields = ['id', 'item', 'option', 'order_amount', 'review_enabled', 'order_product_status', 'company', 'delivery_status']

    def get_company(self, obj):
        return CompanySerializer(obj.opt_no.item_no.item_company).data

class OrderSerializer(serializers.ModelSerializer):
    order_products = OrderProductSerializer(many=True, read_only=True)
    customer = UserSerializer(source='cust_no', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'order_create_date', 'order_payment_status', 'order_payment_method', 'order_total_price', 'cust_address', 'order_products']

class CompanyOrderSerializer(serializers.ModelSerializer):
    order_products = serializers.SerializerMethodField()
    customer = UserSerializer(source='cust_no', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'order_create_date', 'order_payment_status', 'order_payment_method', 'order_total_price', 'cust_address', 'order_products']

    def get_order_products(self, obj):
        company = self.context.get('company')
        products = obj.order_products.filter(opt_no__item_no__item_company=company)
        return OrderProductSerializer(products, many=True).data
    
class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'cust_no', 'item_no']
