from django.core.management.base import BaseCommand
from django.db import transaction

from app_fsMD.models import Category, Product, ProductImage, BlogPost, Feedback
from app_fsMD.utils.images import convert_imagefield_to_webp


class Command(BaseCommand):
    help = "Convert existing uploaded images to .webp and update ImageField paths."

    def handle(self, *args, **options):
        updated = 0

        def save_instance(obj, field_name, quality, max_px):
            nonlocal updated
            before = getattr(obj, field_name).name if getattr(obj, field_name) else ""
            obj._skip_webp = True
            convert_imagefield_to_webp(obj, field_name, quality=quality, max_px=max_px)
            after = getattr(obj, field_name).name if getattr(obj, field_name) else ""
            if before and after and before != after:
                obj.save(update_fields=[field_name])
                updated += 1
            obj._skip_webp = False

        with transaction.atomic():
            for c in Category.objects.all().iterator():
                if c.image:
                    save_instance(c, "image", 82, 2400)

            for p in Product.objects.all().iterator():
                if p.main_image:
                    save_instance(p, "main_image", 82, 2400)

            for pi in ProductImage.objects.all().iterator():
                if pi.image:
                    save_instance(pi, "image", 82, 2400)

            for b in BlogPost.objects.all().iterator():
                if b.main_image:
                    save_instance(b, "main_image", 82, 2400)

            for f in Feedback.objects.all().iterator():
                if f.image:
                    save_instance(f, "image", 82, 1600)

        self.stdout.write(self.style.SUCCESS(f"Done. Updated {updated} images to WEBP."))
