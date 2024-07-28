from django.core.management.base import BaseCommand
from shopapp.models import Item
import random

class Command(BaseCommand):
    help = 'Updates likes count for existing items'

    def add_arguments(self, parser):
        parser.add_argument('--min', type=int, default=0, help='Minimum number of likes')
        parser.add_argument('--max', type=int, default=1000, help='Maximum number of likes')

    def handle(self, *args, **options):
        min_likes = options['min']
        max_likes = options['max']

        items = Item.objects.all()
        updated_count = 0

        for item in items:
            likes_count = random.randint(min_likes, max_likes)
            item.likes_count = likes_count
            item.save(update_fields=['likes_count'])
            updated_count += 1
            self.stdout.write(self.style.SUCCESS(f'Updated "{item.item_name}" with {likes_count} likes'))

        self.stdout.write(self.style.SUCCESS(f'Successfully updated {updated_count} items'))