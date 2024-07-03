from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from shopapp.models.account import User
from shopapp.models.item import Review, Item
from shopapp.models.order import OrderProduct
from shopapp.views.permissions import IsCustomer
from shopapp.serializers import ReviewSerializer
from django.db import transaction

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all().order_by('review_create_date')
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    
    # 리뷰 작성
    @transaction.atomic
    @action(detail=False, methods=['post'], permission_classes=[IsCustomer])
    def create_review(self, request):
        print(f"Received files: {request.FILES}")
        print(f"Received data: {request.data}")
        customer_username = request.auth.get('username')
        if not customer_username:
            raise PermissionDenied("Customer information not found in the token.")
        
        customer = get_object_or_404(User, username=customer_username)
        if not customer.is_customer:
            raise PermissionDenied("Only customers can write reviews")
        
        order_product_id = request.data.get('order_product_id')
        order_product = get_object_or_404(OrderProduct, id=order_product_id, order_no__cust_no=customer)
        
        if order_product.review_enabled != 'Y':
            raise PermissionDenied("Review is not enabled for this order product.")
        
        # 리뷰 데이터 유효성 검사
        review_star = request.data.get('review_star')
        review_contents = request.data.get('review_contents')
        
        if review_star is None:
            raise ValidationError("Review star is required.")
    
        try:
            review_star = int(review_star)
            if not 1 <= review_star <= 5:
                raise ValidationError("Review star must be between 1 and 5.")
        except ValueError:
            raise ValidationError("Review star must be a valid integer.")
        
        if len(review_contents) > 500:  # 예시로 500자 제한
            raise ValidationError("Review content is too long. Maximum 500 characters allowed.")
        
        review_image = request.FILES.get('review_image')        
        
        try:
            with transaction.atomic():
                review = Review.objects.create(
                    orderproduct_no=order_product,
                    item=order_product.opt_no.item_no,
                    review_star=review_star,
                    review_contents=review_contents,
                    review_image=review_image
                )
            
                # order_product_status 업데이트
                order_product.order_product_status = '구매완료'
                order_product.review_enabled = 'N'  # 리뷰 작성 완료
                order_product.save()
            
            serializer = ReviewSerializer(review, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            print(f"Error creating review: {str(e)}")
            return Response({"error": "Failed to create review"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    # 작성한 리뷰 불러오기
    @action(detail=False, methods=['get'], permission_classes=[IsCustomer])
    def my_reviews(self, request):
        customer_username = request.user.username
        if not customer_username:
            return Response({"error": "Customer information not found."}, status=status.HTTP_400_BAD_REQUEST)

        # OrderProduct를 통해 리뷰를 필터링
        reviews = Review.objects.select_related(
            'orderproduct_no__order_no__cust_no', 
            'item'
        ).filter(orderproduct_no__order_no__cust_no__username=customer_username)
        serializer = ReviewSerializer(reviews, many=True)
        
        return Response(serializer.data)