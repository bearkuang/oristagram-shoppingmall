from shopapp.models.account import Customer, ManagerAccount, CompanyAccount
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

def create_customer(customer_data):
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
    user = None

    if cust_username:
        try:
            user = Customer.objects.get(cust_username=cust_username)
            print(f"Found user by cust_username: {user.cust_username}")
        except Customer.DoesNotExist:
            print("No user found with this cust_username.")

    if user:
        print(f"Authenticating user: {user.cust_username} with password: {cust_password}")
        authenticated_user = authenticate(username=user.cust_username, password=cust_password)
        if authenticated_user:
            print("Authentication successful")
        else:
            print("Authentication failed")

    if user is None:
        return {"error": "Invalid credentials"}

    refresh = RefreshToken.for_user(user)
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
