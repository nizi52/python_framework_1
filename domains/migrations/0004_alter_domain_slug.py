from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("domains", "0003_populate_domain_slugs"),
    ]

    operations = [
        migrations.AlterField(
            model_name="domain",
            name="slug",
            field=models.SlugField(
                editable=False, max_length=280, unique=True, verbose_name="URL-идентификатор"
            ),
        ),
    ]
