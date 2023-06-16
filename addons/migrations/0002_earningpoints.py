# Generated by Django 3.2.7 on 2023-03-28 05:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('addons', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EarningPoints',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('signup_point', models.IntegerField(default=10)),
                ('enable_signup_point', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name_plural': 'Earning Points',
            },
        ),
    ]
