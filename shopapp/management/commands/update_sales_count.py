from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from shopapp.models import Item, Order, OrderProduct, User, ItemOption
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Creates dummy order data for existing items'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=30, help='Number of days to generate data for')
        parser.add_argument('--max_orders', type=int, default=100, help='Maximum number of orders per day')

    def handle(self, *args, **options):
        days = options['days']
        max_orders = options['max_orders']

        # 고객 사용자 가져오기
        customers = User.objects.filter(is_company=False)
        if not customers.exists():
            self.stdout.write(self.style.ERROR('No customer users found. Please create some customer users first.'))
            return

        # 회사별 아이템 옵션 가져오기
        companies = User.objects.filter(is_company=True)
        company_item_options = {company: list(ItemOption.objects.filter(item_no__item_company=company)) for company in companies}

        if not any(company_item_options.values()):
            self.stdout.write(self.style.ERROR('No item options found. Please create some items and options first.'))
            return

        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)

        for company in companies:
            if not company_item_options[company]:
                continue

            company_start_date = start_date
            while company_start_date <= end_date:
                # 각 날짜에 대해 랜덤한 수의 주문 생성
                num_orders = random.randint(1, max_orders)
                for _ in range(num_orders):
                    customer = random.choice(customers)
                    order = Order.objects.create(
                        cust_no=customer,
                        order_create_date=timezone.make_aware(datetime.combine(company_start_date, datetime.min.time())),
                        order_total_price=0,
                        cust_address='Dummy Address'
                    )

                    # 각 주문에 대해 1-5개의 주문 상품 생성
                    num_products = random.randint(1, 5)
                    total_price = 0
                    for _ in range(num_products):
                        item_option = random.choice(company_item_options[company])
                        quantity = random.randint(1, 5)
                        price = item_option.item_no.item_price * quantity
                        total_price += price

                        OrderProduct.objects.create(
                            order_no=order,
                            order_amount=quantity,
                            opt_no=item_option
                        )

                        # 아이템의 sales_count 업데이트
                        item = item_option.item_no
                        item.sales_count += quantity
                        item.save()

                    # 주문 총액 업데이트
                    order.order_total_price = total_price
                    order.save()

                self.stdout.write(self.style.SUCCESS(f'Created {num_orders} orders for company {company.id} on {company_start_date}'))
                company_start_date += timedelta(days=1)

        self.stdout.write(self.style.SUCCESS(f'Successfully created dummy order data for all companies over {days} days'))