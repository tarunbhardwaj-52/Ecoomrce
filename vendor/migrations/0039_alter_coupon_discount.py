# Generated by Django 3.2.18 on 2023-05-06 13:30

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0038_auto_20230506_0330'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='discount',
            field=models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator, django.core.validators.MaxValueValidator]),
        ),
    ]