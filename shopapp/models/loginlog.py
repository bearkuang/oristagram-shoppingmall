from django.db import models
from django.conf import settings

class LoginLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    login_datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['login_datetime']),
        ]