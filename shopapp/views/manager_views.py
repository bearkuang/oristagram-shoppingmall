from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from shopapp.models.account import ManagerAccount, CompanyAccount
from shopapp.services.account_services import create_manager, login_manager
from shopapp.serializers import ManagerSerializer, CompanySerializer

class ManagerAccountViewSet(viewsets.ModelViewSet):
    queryset = ManagerAccount.objects.all()
    serializer_class = ManagerSerializer
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
        manager_id = request.data.get('manager_id')
        manager_pwd = request.data.get('manager_pwd')

        if not manager_id or not manager_pwd:
            return Response({"error": "manager_id and manager_pwd must be provided"}, status=status.HTTP_400_BAD_REQUEST)

        tokens = login_manager(manager_id, manager_pwd)
        if "error" in tokens:
            return Response(tokens, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(tokens, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = create_manager(serializer.validated_data)
        return Response(ManagerSerializer(user).data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def approve_company(self, request, pk=None):
        try:
            company = CompanyAccount.objects.get(pk=pk)
            company.activate = 1
            company.save()
            return Response({"status": "Company approved successfully"}, status=status.HTTP_200_OK)
        except CompanyAccount.DoesNotExist:
            return Response({"detail": "Company not found", "code": "company_not_found"}, status=status.HTTP_404_NOT_FOUND)
