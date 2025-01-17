# Generated by Django 3.2.18 on 2023-04-14 02:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0046_cartorderitem_grand_total'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartorderitem',
            name='service_fee',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=12),
        ),
        migrations.AddField(
            model_name='cartorderitem',
            name='vat',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=12),
        ),
    ]
