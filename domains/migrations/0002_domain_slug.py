from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("domains", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="domain",
            name="slug",
            field=models.SlugField(
                blank=True, editable=False, max_length=280, verbose_name="URL-идентификатор"
            ),
        ),
    ]
