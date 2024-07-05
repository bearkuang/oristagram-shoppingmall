from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from shopapp.models.account import User
from shopapp.services.account_services import create_customer, login_user, send_verification_email, verify_email_code
from shopapp.serializers import UserSerializer
from django.core.cache import cache

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_company=False)
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'login', 'register', 'request_verification', 'verify_email']:
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()
    
    # 이메일 인증번호 전송
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def request_verification(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            send_verification_email(email)
            return Response({'message': 'Verification code sent successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 인증번호 확인
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def verify_email(self, request):
        email = request.data.get('email')
        code = request.data.get('code')
        
        if not email or not code:
            return Response({"error": "Email and code are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if verify_email_code(email, code):
            return Response({'message': 'Email verified successfully'})
        else:
            return Response({'error': 'Invalid or expired verification code'}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        print(request.data)  # 요청 데이터 로깅
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not serializer.is_valid():
            print(serializer.errors)  # 유효성 검사 오류 로깅
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # 로그인
    @action(detail=False, methods=['post'])
    def login(self, request):
        cust_username = request.data.get('username')
        cust_password = request.data.get('password')

        if not cust_username or not cust_password:
            return Response({"error": "cust_username and cust_password must be provided"}, status=status.HTTP_400_BAD_REQUEST)

        tokens = login_user(cust_username, cust_password, is_company=False)
        if "error" in tokens:
            return Response(tokens, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(tokens, status=status.HTTP_200_OK)

    # 중복확인
    @action(detail=False, methods=['post'])
    def check_duplicate(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        errors = {}

        if username and User.objects.filter(username=username).exists():
            errors['cust_username'] = '이미 존재하는 아이디 입니다.'

        if email and User.objects.filter(email=email).exists():
            errors['cust_email'] = '이미 가입된 이메일입니다. 다른 이메일을 입력해주세요.'

        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'message': 'Valid username and email'}, status=status.HTTP_200_OK)
    
    # 회원 가입
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        username = serializer.validated_data['username']
        
        errors = {}

        # 아이디와 이메일 중복 검사를 한 번에 수행
        if User.objects.filter(username=username).exists():
            errors['cust_username'] = "이미 가입된 아이디입니다."
        
        if User.objects.filter(email=email).exists():
            errors['cust_email'] = "이미 가입된 이메일입니다."
        
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        # 이메일 인증 코드 확인
        verification_code = request.data.get('verification_code')
        if not verify_email_code(email, verification_code):
            return Response({"error": "Invalid or expired verification code"}, status=status.HTTP_400_BAD_REQUEST)

        user = create_customer(serializer.validated_data, is_verified=True)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)