from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from shopapp.models.account import CompanyAccount
from shopapp.models.item import ItemImage
from shopapp.services.account_services import create_company, login_company
from shopapp.serializers import CompanySerializer, ItemSerializer, ItemOptionSerializer

class CompanyAccountViewSet(viewsets.ModelViewSet):
    queryset = CompanyAccount.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create', 'login', 'register']:
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        company_id = request.data.get('company_id')
        company_pwd = request.data.get('company_pwd')

        if not company_id or not company_pwd:
            return Response({"error": "company_id and company_pwd must be provided"}, status=status.HTTP_400_BAD_REQUEST)

        tokens = login_company(company_id, company_pwd)
        if "error" in tokens:
            return Response(tokens, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(tokens, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = create_company(serializer.validated_data)
        return Response(CompanySerializer(user).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def add_item(self, request):
        company = self.request.user
        if company.activate != 1:
            return Response({"error": "Company account is not activated"}, status=status.HTTP_403_FORBIDDEN)
        
        item_serializer = ItemSerializer(data=request.data.get('item'))
        item_serializer.is_valid(raise_exception=True)
        item = item_serializer.save()
        
        # Handle ItemImage
        images = request.FILES.getlist('images')
        for image in images:
            ItemImage.objects.create(file=image, item_no=item)
        
        # Handle ItemOption
        options_data = request.data.get('options')
        for option_data in options_data:
            option_data['item_no'] = item.id
            option_serializer = ItemOptionSerializer(data=option_data)
            option_serializer.is_valid(raise_exception=True)
            option_serializer.save()
        
        return Response(ItemSerializer(item).data, status=status.HTTP_201_CREATED)
