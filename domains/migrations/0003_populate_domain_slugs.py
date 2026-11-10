from django.db import migrations
from django.utils.text import slugify
from unidecode import unidecode


def populate_domain_slugs(apps, schema_editor):
    Domain = apps.get_model("domains", "Domain")
    for domain in Domain.objects.order_by("pk"):
        # slugify() удаляет точки, поэтому сначала заменяем их дефисами: example.ru -> example-ru.
        base_slug = slugify(unidecode(domain.name.replace(".", "-"))) or "domain"
        domain.slug = f"{base_slug}-{domain.pk}"
        domain.save(update_fields=["slug"])


class Migration(migrations.Migration):

    dependencies = [
        ("domains", "0002_domain_slug"),
    ]

    operations = [
        migrations.RunPython(populate_domain_slugs, migrations.RunPython.noop),
    ]
