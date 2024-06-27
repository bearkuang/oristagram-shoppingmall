# init_db.py
import os
import django
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

if __name__ == "__main__":
    # 모든 데이터를 초기화합니다 (테이블은 유지됨)
    call_command('flush', '--no-input')
    # 마이그레이션을 수행하여 데이터베이스를 최신 상태로 유지
    call_command('migrate')
