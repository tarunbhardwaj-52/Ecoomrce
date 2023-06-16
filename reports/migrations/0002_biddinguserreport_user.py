# Generated by Django 3.2.18 on 2023-04-21 16:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('reports', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='biddinguserreport',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bidding_reporting_user', to=settings.AUTH_USER_MODEL),
        ),
    ]