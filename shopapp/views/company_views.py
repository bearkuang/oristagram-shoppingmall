from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Sum
from shopapp.models.account import User
from shopapp.models.item import ItemImage, Item
from shopapp.models.order import Order, OrderProduct
from shopapp.services.account_services import create_company, login_user
from .permissions import IsAuthenticatedCompany
from shopapp.serializers import UserSerializer, ItemSerializer, ItemOptionSerializer, CompanyOrderSerializer, OrderProductSerializer
import json

class CompanyAccountViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_company=True)
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'login', 'register']:
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = create_company(serializer.validated_data)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({"error": "Username and password must be provided"}, status=status.HTTP_400_BAD_REQUEST)

        tokens = login_user(username, password, is_company=True)
        if "error" in tokens:
            return Response(tokens, status=status.HTTP_400_BAD_REQUEST)

        return Response(tokens, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def add_item(self, request):
        print("Request data:", request.data)  # 디버깅을 위해 요청 데이터 출력

        item_data = {
            "cate_no": request.data.get('cate_no'),
            "item_name": request.data.get('item_name'),
            "item_description": request.data.get('item_description'),
            "item_price": request.data.get('item_price'),
            "item_soldout": request.data.get('item_soldout'),
            "item_is_display": 'N',
            "item_company": request.data.get('item_company'),
        }

        print("Item data:", item_data)  # 디버깅을 위해 아이템 데이터 출력

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
        options_data = json.loads(request.data.get('options', '[]'))
        for option_data in options_data:
            option_data['item_no'] = item.id
            option_serializer = ItemOptionSerializer(data=option_data)
            option_serializer.is_valid(raise_exception=True)
            option_serializer.save()

        return Response(ItemSerializer(item).data, status=status.HTTP_201_CREATED)
    
    # 주문 들어온 상품 보기
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticatedCompany])
    def company_orders(self, request):
        company = request.user
        orders = Order.objects.filter(order_products__opt_no__item_no__item_company=company).distinct()
        serializer = CompanyOrderSerializer(orders, many=True, context={'company': company})
        return Response(serializer.data)
    
    # 상품 배송 상태 업데이트
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticatedCompany])
    def update_delivery_status(self, request, pk=None):
        order_product = get_object_or_404(OrderProduct, pk=pk)
        new_status = request.data.get('delivery_status')
        
        if new_status not in dict(OrderProduct.DELIVERY_STATUS_CHOICES):
            return Response({"error": "Invalid delivery status"}, status=status.HTTP_400_BAD_REQUEST)
        
        order_product.delivery_status = new_status
        if new_status == '배송완료':
            order_product.review_enabled = 'Y'
        order_product.save()
        
        serializer = OrderProductSerializer(order_product)
        return Response(serializer.data)
    
    # 등록 중인 상품 보기
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticatedCompany])
    def added_items(self, request):
        company = request.user
        items = Item.objects.filter(item_company=company).only('id', 'item_name', 'item_price').order_by('-item_create_date')

        # 필터링
        status = request.query_params.get('status')
        if status == 'available':
            items = items.filter(item_soldout='N')
        elif status == 'soldout':
            items = items.filter(item_soldout='Y')

        category = request.query_params.get('cate_no')
        if category:
            items = items.filter(cate_no=category)

        serializer = ItemSerializer(items, many=True, context={'request': request})
        return Response(serializer.data)
    
    # 기업의 상품별 판매량
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticatedCompany])
    def item_sales(self, request):
        company = request.user
        items = Item.objects.filter(item_company=company).annotate(
            total_sales=Sum('orderproduct__order_amount')
        ).values('id', 'item_name', 'total_sales')
        
        return Response(list(items), status=status.HTTP_200_OK)