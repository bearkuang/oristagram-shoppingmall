from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from django.db import transaction
from shopapp.models.account import User
from shopapp.views.permissions import IsCustomer
from shopapp.models.order import Order, OrderProduct
from shopapp.models.item import ItemOption, Cart, Item
from shopapp.serializers import OrderSerializer, OrderProductSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('order_create_date')
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsCustomer]
    
    # 장바구니에서 상품 선택하여 구매
    @action(detail=False, methods=['post'], permission_classes=[IsCustomer])
    def order_from_cart(self, request):
        customer_username = request.auth.get('username')
        if not customer_username:
            raise PermissionDenied("Customer information not found in the token.")
        
        customer = get_object_or_404(User, username=customer_username)
        
        order_data = request.data
        
        with transaction.atomic():
            order = Order.objects.create(
                cust_no=customer,
                order_payment_status=order_data.get('order_payment_status', '결제완료'),
                order_payment_method=order_data.get('order_payment_method', '신용/체크'),
                order_total_price=order_data.get('order_total_price', 0),
                cust_address=order_data.get('cust_address', customer.address)
            )
            
            cart_items = order_data.get('cart_items', [])
            for cart_item_id in cart_items:
                cart_item = get_object_or_404(Cart, id=cart_item_id, cust_no=customer)
                self._create_order_product(order, cart_item.opt_no, cart_item.cart_order_amount)
                cart_item.delete()
        
        order_serializer = OrderSerializer(order)
        return Response(order_serializer.data, status=status.HTTP_201_CREATED)

    # 상품 상세 페이지에서 직접 구매
    @action(detail=False, methods=['post'], permission_classes=[IsCustomer])
    def order_direct(self, request):
        print(f"User: {request.user}")
        print(f"Is authenticated: {request.user.is_authenticated}")
        print(f"Is company: {getattr(request.user, 'is_company', None)}")
        print(f"Is customer: {getattr(request.user, 'is_customer', None)}")
        customer_username = request.auth.get('username')
        if not customer_username:
            raise PermissionDenied("Customer information not found in the token.")
        
        customer = get_object_or_404(User, username=customer_username)
        if customer.is_company:
            raise PermissionDenied("Only customers can place orders.")
        
        order_data = request.data
        
        with transaction.atomic():
            order = Order.objects.create(
                cust_no=customer,
                order_payment_status=order_data.get('order_payment_status', '결제완료'),
                order_payment_method=order_data.get('order_payment_method', '신용/체크'),
                order_total_price=order_data.get('order_total_price', 0),
                cust_address=order_data.get('cust_address', customer.address)
            )
            
            item_id = order_data.get('item_id')
            option_id = order_data.get('option_id')
            quantity = order_data.get('quantity', 1)
            
            item = get_object_or_404(Item, id=item_id)
            option = get_object_or_404(ItemOption, id=option_id, item_no=item)
            self._create_order_product(order, option, quantity)
        
        order_serializer = OrderSerializer(order)
        return Response(order_serializer.data, status=status.HTTP_201_CREATED)
    
    # 재고 업데이트
    def _create_order_product(self, order, item_option, quantity):
        # 재고 확인 및 업데이트
        if item_option.opt_stock < quantity:
            raise PermissionDenied(f"Not enough stock for item option {item_option.id}")
        
        item_option.opt_stock -= quantity
        item_option.save()
        
        # 주문 상품 생성
        OrderProduct.objects.create(
            order_no=order,
            order_amount=quantity,
            opt_no=item_option,
            review_enabled='N',  # 초기에는 리뷰 작성 불가능
            order_product_status='주문완료',
            delivery_status='준비중'
        )

    # 내 주문 목록
    @action(detail=False, methods=['get'], permission_classes=[IsCustomer])
    def my_orders(self, request):
        customer_username = request.auth.get('username')
        if not customer_username:
            raise PermissionDenied("Customer information not found in the token.")
        
        customer = get_object_or_404(User, username=customer_username)
        
        orders = Order.objects.filter(cust_no=customer).order_by('-order_create_date')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
