# Generated by Django 3.2.18 on 2023-03-31 01:24

from django.db import migrations
import django_ckeditor_5.fields


class Migration(migrations.Migration):

    dependencies = [
        ('addons', '0004_policy'),
    ]

    operations = [
        migrations.AlterField(
            model_name='policy',
            name='privacy_policy',
            field=django_ckeditor_5.fields.CKEditor5Field(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='policy',
            name='return_policy',
            field=django_ckeditor_5.fields.CKEditor5Field(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='policy',
            name='terms_and_conditions',
            field=django_ckeditor_5.fields.CKEditor5Field(blank=True, null=True),
        ),
    ]