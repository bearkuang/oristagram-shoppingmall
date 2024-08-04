from django.core.management.base import BaseCommand
from django.utils import timezone
from shopapp.models import Item, Review, User
import random
import datetime

class Command(BaseCommand):
    help = 'Generates dummy review data for items'

    def handle(self, *args, **kwargs):
        items = Item.objects.all()
        users = User.objects.filter(is_company=False)

        review_contents = [
            "정말 만족스러운 구매였어요!",
            "생각보다 품질이 좋아서 놀랐어요.",
            "배송이 빨라서 좋았습니다.",
            "가격 대비 괜찮은 상품이에요.",
            "디자인이 예뻐요. 다음에 또 구매할게요.",
            "사이즈가 딱 맞아요. 추천합니다!",
            "색상이 사진과 똑같아요. 만족스럽습니다.",
            "친구들에게도 추천했어요.",
            "사용해보니 편리하네요.",
            "포장도 꼼꼼히 해주셔서 감사합니다."
        ]

        def random_date(start, end):
            return start + datetime.timedelta(
                seconds=random.randint(0, int((end - start).total_seconds())),
            )

        start_date = timezone.now() - datetime.timedelta(days=365)
        end_date = timezone.now()

        for item in items:
            # 각 아이템마다 3~10개의 리뷰 생성
            for _ in range(random.randint(3, 10)):
                user = random.choice(users)
                
                Review.objects.create(
                    item=item,
                    orderproduct_no=None,  # OrderProduct 객체 대신 None 사용
                    review_star=random.randint(3, 5),  # 3~5점 사이의 별점
                    review_contents=random.choice(review_contents),
                    review_create_date=random_date(start_date, end_date)
                )

        self.stdout.write(self.style.SUCCESS('Successfully generated dummy reviews'))