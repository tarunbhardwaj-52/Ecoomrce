# Generated by Django 3.2.18 on 2023-04-24 23:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('addons', '0024_homepagesetup'),
    ]

    operations = [
        migrations.AddField(
            model_name='homepagesetup',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
