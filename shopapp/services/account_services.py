from shopapp.models.account import Customer, ManagerAccount, CompanyAccount
from django.contrib.auth import authenticate
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
    from_email = 'your-email@example.com'
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

def create_customer(customer_data, is_verified=False):
    if not is_verified:
        raise ValueError('Email is not verified')
    
    customer = Customer.objects.create(
        cust_username=customer_data['cust_username'],
        cust_name=customer_data['cust_name'],
        cust_password=customer_data['cust_password'],
        cust_gender=customer_data.get('cust_gender', 'F'),
        cust_birthday=customer_data.get('cust_birthday'),
        cust_address=customer_data['cust_address'],
        cust_email=customer_data['cust_email'],
    )
    customer.save()
    return customer

def create_manager(manager_data):
    if ManagerAccount.objects.filter(manager_id=manager_data['manager_id']).exists():
        raise ValueError('Manager with this ID already exists.')
    
    manager = ManagerAccount.objects.create_user(
        manager_id=manager_data['manager_id'],
        password=manager_data['password'],
    )
    manager.save()
    return manager

def create_company(company_data):
    if CompanyAccount.objects.filter(company_id=company_data['company_id']).exists():
        raise ValueError('Company with this ID already exists.')
    
    company = CompanyAccount.objects.create(
        company_id=company_data['company_id'],
        company_pwd=company_data['company_pwd'],
        activate=0  # 기본값으로 비활성화된 상태로 생성
    )
    company.save()
    print(f"Created company: {company.company_id}, password: {company.company_pwd}, pk: {company.id}")
    return company

def login_user(cust_username, cust_password):
    try:
        user = Customer.objects.get(cust_username=cust_username)
    except Customer.DoesNotExist:
        return {"error": "Invalid credentials"}

    if user.cust_password != cust_password:
        return {"error": "Invalid credentials"}

    refresh = RefreshToken.for_user(user)
    refresh['username'] = user.cust_username
    refresh['user_type'] = 'customer'
    print(f"Generated token: {refresh}")

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def login_manager(manager_id, password):
    user = None

    if manager_id:
        try:
            user = ManagerAccount.objects.get(manager_id=manager_id)
            print(f"Found user by manager_id: {user.manager_id}")
        except ManagerAccount.DoesNotExist:
            print("No user found with this manager_id.")

    if user and user.check_password(password):
        print("Authentication successful")
    else:
        print("Authentication failed")
        return {"error": "Invalid credentials"}

    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def login_company(company_id, company_pwd):
    user = None

    if company_id:
        try:
            user = CompanyAccount.objects.get(company_id=company_id)
            print(f"Found user by company_id: {user.company_id}")
        except CompanyAccount.DoesNotExist:
            print("No user found with this company_id.")

    if user:
        if user.company_pwd == company_pwd:
            if user.activate == 1:
                print("Authentication successful")
            else:
                print("Company account is not activated")
                return {"error": "Company account is not activated"}
        else:
            print("Authentication failed")
            return {"error": "Invalid credentials"}

    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
