# Generated by Django 3.2.18 on 2023-05-01 01:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0027_auto_20230424_2227'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendor',
            name='show_mobile_number_in_store',
            field=models.BooleanField(default=True),
        ),
    ]
