# Generated by Django 3.2.18 on 2023-04-06 04:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0033_cartorderitem_product_obj'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='stock_qty',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
