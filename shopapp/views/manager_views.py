from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from shopapp.models.account import User
from shopapp.services.account_services import create_manager, login_user
from shopapp.serializers import UserSerializer

class ManagerAccountViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_staff=True)
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
        user = create_manager(serializer.validated_data)
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

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def approve_company(self, request, pk=None):
        try:
            company = User.objects.get(pk=pk, is_company=True)
            company.is_active = True
            company.save()
            return Response({"status": "Company approved successfully"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "Company not found", "code": "company_not_found"}, status=status.HTTP_404_NOT_FOUND)