from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from shopapp.models import Category
from shopapp.serializers import CategorySerializer

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'], url_path='main-categories')
    def get_main_categories(self, request):
        main_categories = Category.objects.values_list('main_cate_name', flat=True).distinct()
        return Response(main_categories)

    @action(detail=False, methods=['get'], url_path='sub-categories')
    def get_sub_categories(self, request):
        main_cate_name = request.query_params.get('main_cate_name')
        if not main_cate_name:
            return Response({"error": "main_cate_name is required"}, status=400)
        
        sub_categories = Category.objects.filter(main_cate_name=main_cate_name).values('id', 'cate_name')
        return Response(sub_categories)
