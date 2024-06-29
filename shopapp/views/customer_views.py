from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from shopapp.models.account import Customer
from shopapp.services.account_services import create_customer, login_user
from shopapp.serializers import CustomerSerializer

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'login', 'register']:
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        print(request.data)  # 요청 데이터 로깅
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not serializer.is_valid():
            print(serializer.errors)  # 유효성 검사 오류 로깅
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['post'])
    def login(self, request):
        cust_username = request.data.get('cust_username')
        cust_password = request.data.get('cust_password')

        if not cust_username or not cust_password:
            return Response({"error": "cust_username and cust_password must be provided"}, status=status.HTTP_400_BAD_REQUEST)

        tokens = login_user(cust_username, cust_password)
        if "error" in tokens:
            return Response(tokens, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(tokens, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        print(request.data)  # 요청 데이터 로깅
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print(serializer.errors)  # 유효성 검사 오류 로깅
        serializer.is_valid(raise_exception=True)
        user = create_customer(serializer.validated_data)
        return Response(CustomerSerializer(user).data, status=status.HTTP_201_CREATED)
