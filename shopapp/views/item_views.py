from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from shopapp.models.account import Customer
from shopapp.views.permissions import IsCustomer
from shopapp.models.item import Item, ItemImage, ItemOption, Category, Like, Cart
from shopapp.serializers import ItemSerializer, ItemImageSerializer, ItemOptionSerializer, LikeSerializer, CartSerializer
import json
from django.db.models import Count

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all().order_by('item_create_date')
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def add_item(self, request):
        return self.create(request)
    
    # 기업이 상품 등록
    def create(self, request, *args, **kwargs):
        print("Request data:", request.data)  # 로그 추가
        # Parse the form data from the request
        item_data = {
            "cate_no": request.data.get('cate_no'),
            "item_name": request.data.get('item_name'),
            "item_description": request.data.get('item_description'),
            "item_price": request.data.get('item_price'),
            "item_soldout": request.data.get('item_soldout'),
            "item_is_display": request.data.get('item_is_display'),
            "item_company": request.data.get('item_company'),
        }

        options_data = json.loads(request.data.get('options'))

        # Validate and save Item
        item_serializer = ItemSerializer(data=item_data)
        if not item_serializer.is_valid():
            print("Serializer errors:", item_serializer.errors)
        item_serializer.is_valid(raise_exception=True)
        item = item_serializer.save()
        
        # Handle ItemImage
        images = request.FILES.getlist('images')
        for image in images:
            ItemImage.objects.create(file=image, item_no=item)
        
        # Handle ItemOption
        for option_data in options_data:
            option_data['item_no'] = item.id
            option_serializer = ItemOptionSerializer(data=option_data)
            option_serializer.is_valid(raise_exception=True)
            option_serializer.save()
        
        return Response(ItemSerializer(item).data, status=status.HTTP_201_CREATED)
    
    # 카테고리 별 상품 보기
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def categorized(self, request):
        cate_no = request.query_params.get('cate_no', None)
        if cate_no is None:
            return Response({"error": "Category ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            category = Category.objects.get(pk=cate_no)
        except Category.DoesNotExist:
            return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

        items = Item.objects.filter(cate_no=category).order_by('-item_create_date')
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)
    
    # 좋아요가 많은 상품 4개 가져오기
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def popular(self, request):
        popular_items = Item.objects.annotate(like_count=Count('like')).order_by('-like_count')[:4]
        serializer = self.get_serializer(popular_items, many=True)
        return Response(serializer.data)
    
    # 신상품 4개 가져오기
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def newest(self, request):
        new_items = Item.objects.order_by('-item_create_date')[:4]
        serializer = self.get_serializer(new_items, many=True)
        return Response(serializer.data)

    # 상품 상세보기
    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def info(self, request, pk=None):
        print(f"Requested item ID: {pk}")  # 로그 추가
        try:
            item = Item.objects.get(pk=pk)
        except Item.DoesNotExist:
            return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)
    
        serializer = self.get_serializer(item)
        return Response(serializer.data)

    # 상품 좋아요
    @action(detail=True, methods=['post'], permission_classes=[IsCustomer])
    def like(self, request, pk=None):
        print(f"Auth: {request.auth}")  # JWT 토큰 내용 출력
        print(f"User: {request.user}")  # 현재 사용자 정보 출력
        item = self.get_object()
        
        # JWT 토큰에서 username
        customer_username = request.auth.get('username')
        if not customer_username:
            raise PermissionDenied("Customer information not found in the token.")
        
        customer = get_object_or_404(Customer, cust_username=customer_username)
        
        like, created = Like.objects.get_or_create(cust_no=customer, item_no=item)

        if not created:
            like.delete()
            return Response({'status': 'like_removed'}, status=status.HTTP_200_OK)
        
        serializer = LikeSerializer(like)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # 상품 좋아요 상태 확인
    @action(detail=True, methods=['get'], permission_classes=[IsCustomer])
    def like_status(self, request, pk=None):
        item = self.get_object()
        
        customer_username = request.auth.get('username')
        if not customer_username:
            raise PermissionDenied("Customer information not found in the token.")
        
        customer = get_object_or_404(Customer, cust_username=customer_username)
        
        is_liked = Like.objects.filter(cust_no=customer, item_no=item).exists()
        return Response({'is_liked': is_liked})
    
    # 장바구니에 추가
    @action(detail=False, methods=['post'], permission_classes=[IsCustomer])
    def add_to_cart(self, request):
        # JWT 토큰에서 username을 가져옵니다.
        customer_username = request.auth.get('username')
        if not customer_username:
            raise PermissionDenied("Customer information not found in the token.")
        
        customer = get_object_or_404(Customer, cust_username=customer_username)
        
        # 요청에서 수량과 옵션 정보를 가져옵니다.
        quantity = request.data.get('quantity', 1)
        option_data = request.data.get('option')
        
        if not option_data or 'item_no' not in option_data:
            return Response({"error": "Option data and item_no are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # 상품 가져오기
        item = get_object_or_404(Item, id=option_data['item_no'])
        
        # 옵션 데이터 유효성 검사
        option_serializer = ItemOptionSerializer(data=option_data)
        if not option_serializer.is_valid():
            return Response(option_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # 옵션 가져오기 또는 생성
        option, created = ItemOption.objects.get_or_create(
            item_no=item,
            opt_color=option_data['opt_color'],
            opt_size=option_data['opt_size'],
            defaults={
                'opt_item_soldout': option_data['opt_item_soldout'],
                'opt_stock': option_data['opt_stock']
            }
        )
        
        if not created:
            # 기존 옵션이 있다면 재고 확인
            if option.opt_stock < quantity:
                return Response({"error": "Not enough stock"}, status=status.HTTP_400_BAD_REQUEST)
            
            # 재고 업데이트
            option.opt_stock -= quantity
            option.save()
        
        # 장바구니에 추가 또는 수량 업데이트
        cart_item, created = Cart.objects.get_or_create(
            cust_no=customer,
            opt_no=option,
            defaults={'cart_order_amount': quantity}
        )
        
        if not created:
            cart_item.cart_order_amount += quantity
            cart_item.save()

        serializer = CartSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # 장바구니 보기
    @action(detail=False, methods=['get'], permission_classes=[IsCustomer])
    def view_cart(self, request):
        customer_username = request.auth.get('username')
        if not customer_username:
            raise PermissionDenied("Customer information not found in the token.")
        
        customer = get_object_or_404(Customer, cust_username=customer_username)
        
        cart_items = Cart.objects.filter(cust_no=customer)
        serializer = CartSerializer(cart_items, many=True)
        return Response(serializer.data)