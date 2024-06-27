from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from shopapp.views.customer_views import CustomerViewSet
from shopapp.views.manager_views import ManagerAccountViewSet
from shopapp.views.company_views import CompanyAccountViewSet

router = DefaultRouter()
router.register(r'customers', CustomerViewSet)
router.register(r'managers', ManagerAccountViewSet)
router.register(r'companies', CompanyAccountViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', CustomerViewSet.as_view({'post': 'register'}), name='register'),
    path('auth/login/', CustomerViewSet.as_view({'post': 'login'}), name='login'),
    path('auth/manager-register/', ManagerAccountViewSet.as_view({'post': 'register'}), name='manager-register'),
    path('auth/manager-login/', ManagerAccountViewSet.as_view({'post': 'login'}), name='manager-login'),
    path('managers/<int:pk>/approve_company/', ManagerAccountViewSet.as_view({'post': 'approve_company'}), name='approve-company'),
    path('auth/company-register/', CompanyAccountViewSet.as_view({'post': 'register'}), name='company-register'),
    path('auth/company-login/', CompanyAccountViewSet.as_view({'post': 'login'}), name='company-login'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
