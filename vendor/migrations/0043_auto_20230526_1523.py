# Generated by Django 3.2.18 on 2023-05-26 14:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('store', '0095_auto_20230526_1522'),
        ('vendor', '0042_auto_20230520_2041'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='bid',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='store.productbidders'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='offer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='store.productoffers'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='store.cartorder'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='store.product'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notification_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='notification',
            name='vendor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notification_user', to='vendor.vendor'),
        ),
        migrations.AlterField(
            model_name='ordertracker',
            name='order_item',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cartorderitem_tracker', to='store.cartorderitem'),
        ),
    ]
