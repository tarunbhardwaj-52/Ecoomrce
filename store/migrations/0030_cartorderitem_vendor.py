# Generated by Django 3.2.18 on 2023-04-05 05:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0008_alter_vendor_user'),
        ('store', '0029_auto_20230404_2220'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartorderitem',
            name='vendor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='vendor.vendor'),
        ),
    ]
