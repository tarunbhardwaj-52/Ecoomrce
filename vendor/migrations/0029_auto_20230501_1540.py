# Generated by Django 3.2.18 on 2023-05-01 14:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0028_vendor_show_mobile_number_in_store'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='notification',
            options={'ordering': ['-date']},
        ),
        migrations.AlterModelOptions(
            name='payouttracker',
            options={'ordering': ['-date']},
        ),
    ]
