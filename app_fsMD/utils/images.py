import os
from io import BytesIO

from PIL import Image, ImageOps
from django.core.files.base import ContentFile


def convert_imagefield_to_webp(instance, field_name: str, *, quality: int = 82, max_px: int = 2400) -> None:
    field = getattr(instance, field_name, None)
    if not field or not getattr(field, "name", ""):
        return

    clean_name = (field.name or "").replace("\\", "/")
    field.name = clean_name

    name_lower = clean_name.lower()
    if name_lower.endswith(".webp"):
        return
    if name_lower.endswith("products/no_image_available.png"):
        return

    try:
        try:
            field.open("rb")
        except FileNotFoundError:
            return

        with Image.open(field) as im:
            im = ImageOps.exif_transpose(im)

            if max_px and max(im.size) > max_px:
                im.thumbnail((max_px, max_px), Image.Resampling.LANCZOS)

            if im.mode not in ("RGB", "RGBA"):
                im = im.convert("RGBA" if "A" in im.mode else "RGB")
            if im.mode != "RGBA":
                im = im.convert("RGB")

            out = BytesIO()
            im.save(out, format="WEBP", quality=quality, method=6)
            out.seek(0)

        directory = os.path.dirname(clean_name).replace("\\", "/")
        base = os.path.splitext(os.path.basename(clean_name))[0]
        base = base[:60] if base else f"{instance._meta.model_name}-{getattr(instance, 'pk', 'x')}"
        new_name = f"{directory}/{base}.webp" if directory else f"{base}.webp"

        max_len = getattr(field.field, "max_length", 255) or 255
        if len(new_name) > max_len:
            short_base = f"{instance._meta.model_name}-{getattr(instance, 'pk', 'x')}-{field_name}"
            short_base = short_base[:60]
            new_name = f"{directory}/{short_base}.webp" if directory else f"{short_base}.webp"

        old_name = clean_name
        storage = field.storage

        field.close()
        field.save(new_name, ContentFile(out.read()), save=False)

        if old_name != field.name and storage.exists(old_name):
            try:
                storage.delete(old_name)
            except PermissionError:
                pass

    finally:
        try:
            field.close()
        except Exception:
            pass
