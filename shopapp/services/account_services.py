from shopapp.models.account import User
from rest_framework_simplejwt.tokens import RefreshToken
import random
from django.core.mail import send_mail
from django.core.cache import cache

def generate_verification_code():
    return str(random.randint(100000, 999999))

def send_verification_email(email):
    code = generate_verification_code()
    subject = '이메일 인증 코드'
    message = f'귀하의 인증 코드는 {code} 입니다. 이 코드는 10분간 유효합니다.'
    from_email = 'ori178205@gmail.com'
    recipient_list = [email]
    
    send_mail(subject, message, from_email, recipient_list)
    
    # 캐시에 인증 코드 저장 (10분 동안 유효)
    cache_key = f'verification_code_{email}'
    cache.set(cache_key, code, 600)
    
    # 디버그 로그 추가
    print(f"Stored code in cache: {code}")
    print(f"Retrieved code from cache: {cache.get(cache_key)}")

    return code

def verify_email_code(email, code):
    cache_code = cache.get(f'verification_code_{email}')
    return cache_code == code

def create_user(user_data, is_verified=False):
    if not is_verified:
        raise ValueError('Email is not verified')
    
    if User.objects.filter(username=user_data['username']).exists():
        raise ValueError('User with this ID already exists.')
    
    user = User.objects.create_user(
        username=user_data['username'],
        password=user_data['password'],
        is_company=user_data.get('is_company', False)
    )
    user.save()
    return user

def login_user(username, password):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return {"error": "Invalid credentials"}

    if not user.check_password(password):
        return {"error": "Invalid credentials"}

    refresh = RefreshToken.for_user(user)
    refresh['username'] = user.username
    refresh['user_type'] = 'company' if user.is_company else 'customer'
    print(f"Generated token: {refresh}")

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def create_customer(customer_data, is_verified=False):
    if not is_verified:
        raise ValueError('Email is not verified')

    customer = User.objects.create(
        username=customer_data['username'],
        name=customer_data['name'],
        password=customer_data['password'],
        gender=customer_data.get('gender'),
        birthday=customer_data.get('birthday'),
        address=customer_data['address'],
        email=customer_data['email'],
        is_company=False,  # 고객 계정이므로 is_company는 False로 설정
    )
    customer.set_password(customer_data['password'])
    customer.save()
    return customer

def create_manager(manager_data):
    if User.objects.filter(username=manager_data['username']).exists():
        raise ValueError('Manager with this ID already exists.')

    manager = User.objects.create(
        username=manager_data['username'],
        is_staff=True,
        is_superuser=True,
        is_company=False,
    )
    manager.set_password(manager_data['password'])
    manager.save()
    return manager

def create_company(company_data):
    if User.objects.filter(username=company_data['username']).exists():
        raise ValueError('Company with this ID already exists.')

    company = User.objects.create(
        username=company_data['username'],
        email=company_data['email'],
        is_company=True,
        is_active=False,  # 기본값으로 비활성화된 상태로 생성
    )
    company.set_password(company_data['password'])
    company.save()
    return company

def login_manager(manager_id, password):
    try:
        user = User.objects.get(username=manager_id, is_staff=True)
    except User.DoesNotExist:
        return {"error": "Invalid credentials"}

    if not user.check_password(password):
        return {"error": "Invalid credentials"}

    refresh = RefreshToken.for_user(user)
    refresh['username'] = user.username
    refresh['user_type'] = 'manager'
    print(f"Generated token: {refresh}")

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def login_company(username, password):
    try:
        user = User.objects.get(username=username, is_company=True)
    except User.DoesNotExist:
        return {"error": "Invalid credentials"}

    if not user.check_password(password):
        return {"error": "Invalid credentials"}

    if not user.is_active:
        return {"error": "Company account is not activated"}

    refresh = RefreshToken.for_user(user)
    refresh['username'] = user.username
    refresh['user_type'] = 'company'
    print(f"Generated token: {refresh}")

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
