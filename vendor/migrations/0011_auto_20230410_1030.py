# Generated by Django 3.2.18 on 2023-04-10 17:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0010_vendor_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendor',
            name='stripe_access_token',
            field=models.CharField(blank=True, max_length=10000, null=True),
        ),
        migrations.AddField(
            model_name='vendor',
            name='stripe_refresh_token',
            field=models.CharField(blank=True, max_length=10000, null=True),
        ),
        migrations.AddField(
            model_name='vendor',
            name='stripe_user_id',
            field=models.CharField(blank=True, max_length=10000, null=True),
        ),
    ]