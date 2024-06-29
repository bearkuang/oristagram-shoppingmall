from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from shopapp.models.item import Item, ItemImage, ItemOption, Category
from shopapp.serializers import ItemSerializer, ItemImageSerializer, ItemOptionSerializer
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
