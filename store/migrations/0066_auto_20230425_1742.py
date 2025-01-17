# Generated by Django 3.2.18 on 2023-04-25 16:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('store', '0065_auto_20230425_0305'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productfaq',
            name='active',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='productfaq',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
