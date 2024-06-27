from django.contrib.auth.backends import BaseBackend
from shopapp.models.account import Customer

class CustomerBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = Customer.objects.get(cust_username=username)
            if user.cust_password == password:  # 실제로는 해싱된 비밀번호를 확인해야 합니다
                return user
        except Customer.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Customer.objects.get(pk=user_id)
        except Customer.DoesNotExist:
            return None
