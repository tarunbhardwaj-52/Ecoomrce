# Generated by Django 3.2.18 on 2023-04-14 22:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0047_auto_20230413_1900'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartorder',
            name='custom_order',
            field=models.BooleanField(default=False),
        ),
    ]
