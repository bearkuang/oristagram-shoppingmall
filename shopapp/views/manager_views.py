from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
from .permissions import IsManagerUser
from shopapp.models.item import Item
from shopapp.models.account import User
from shopapp.models.loginlog import LoginLog
from shopapp.services.account_services import create_manager, login_user
from shopapp.serializers import UserSerializer, ItemSerializer

class ManagerAccountViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_staff=True)
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsManagerUser]

    def get_permissions(self):
        if self.action in ['create', 'login', 'register']:
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated, IsManagerUser]
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

    # 기업 승인
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def approve_company(self, request, pk=None):
        try:
            company = User.objects.get(pk=pk, is_company=True)
            company.is_active = True
            company.save()
            return Response({"status": "Company approved successfully"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "Company not found", "code": "company_not_found"}, status=status.HTTP_404_NOT_FOUND)
    
    # 모든 승인 대기 중인 상품 목록
    @action(detail=False, methods=['get'])
    def pending_items(self, request):
        pending_items = Item.objects.filter(item_is_display='N')
        serializer = ItemSerializer(pending_items, many=True)
        return Response(serializer.data)

    # 기업별 승인 대기 중인 상품 목록
    @action(detail=False, methods=['get'])
    def pending_items_by_company(self, request):
        company_id = request.query_params.get('company_id')
        if not company_id:
            return Response({"error": "Company ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        pending_items = Item.objects.filter(item_company_id=company_id, item_is_display='N')
        serializer = ItemSerializer(pending_items, many=True)
        return Response(serializer.data)

    # 특정 상품 승인
    @action(detail=True, methods=['post'])
    def approve_item(self, request, pk=None):
        try:
            item = Item.objects.get(pk=pk)
        except Item.DoesNotExist:
            return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)
        
        item.item_is_display = 'Y'
        item.save()
        
        serializer = ItemSerializer(item)
        return Response(serializer.data)

    # 승인 대기 중인 상품이 있는 기업 목록
    @action(detail=False, methods=['get'])
    def companies_with_pending_items(self, request):
        companies = User.objects.filter(is_company=True, item__item_is_display='N').distinct()
        serializer = UserSerializer(companies, many=True)
        return Response(serializer.data)
    
    # 일별 트래픽
    @action(detail=False, methods=['get'])
    def daily_unique_logins(self, request):
        days = int(request.query_params.get('days', 30))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days-1)

        daily_logins = LoginLog.objects.filter(
            login_datetime__date__range=[start_date, end_date]
        ).annotate(
            login_date=TruncDate('login_datetime')
        ).values('login_date').annotate(
            unique_users=Count('user', distinct=True)
        ).order_by('login_date')

        result = {item['login_date'].strftime('%Y-%m-%d'): item['unique_users'] for item in daily_logins}

        # 로그인이 없는 날짜에 대해 0으로 채우기
        all_dates = [(start_date + timedelta(days=x)).strftime('%Y-%m-%d') for x in range(days)]
        for date in all_dates:
            if date not in result:
                result[date] = 0

        return Response(result)