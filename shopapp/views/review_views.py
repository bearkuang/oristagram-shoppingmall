from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from shopapp.models.account import Customer
from shopapp.models.item import Review
from shopapp.views.permissions import IsCustomer
from shopapp.serializers import ReviewSerializer
import json
from django.db.models import Count

class ReviewViewSet(viewsets.ModleViewSet):
    queryset = Review.objects.all().order_by('review_create_date')
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    
    # 리뷰 생성
    @action(detail=False, methods=['post'], permission_classes=[IsCustomer])
    def create_review(self, request):
        customer_username = request.auth.get('username')
        if not customer_username:
            raise PermissionDenied("Customer information not found in the token.")
        
        customer = get_object_or_404(Customer, cust_username=customer_username)
        
        order_product_id = request.data.get('order_product_id')
        order_product = get_object_or_404(OrderProduct, id=order_product_id, order_no__cust_no=customer)
        
        if order_product.review_enabled != 'Y':
            raise PermissionDenied("Review is not enabled for this order product.")
        
        # 리뷰 생성 로직
        review = Review.objects.create(
            orderproduct_no=order_product,
            review_star=request.data.get('review_star'),
            review_contents=request.data.get('review_contents'),
            review_image=request.data.get('review_image')
        )
        
        # order_product_status 업데이트
        order_product.order_product_status = '구매완료'
        order_product.review_enabled = 'N'  # 리뷰 작성 완료
        order_product.save()
        
        serializer = ReviewSerializer(review)
        return Response(serializer.data, status=status.HTTP_201_CREATED)