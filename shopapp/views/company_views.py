from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from shopapp.models.account import User
from shopapp.models.item import ItemImage
from shopapp.services.account_services import create_company, login_company
from shopapp.serializers import UserSerializer, ItemSerializer, ItemOptionSerializer
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

        tokens = login_user(username, password)
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
            "item_is_display": request.data.get('item_is_display'),
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