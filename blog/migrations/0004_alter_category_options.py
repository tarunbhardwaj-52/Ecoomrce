# Generated by Django 3.2.18 on 2023-04-25 16:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_remove_post_active'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['-id'], 'verbose_name': 'Category', 'verbose_name_plural': 'Categories'},
        ),
    ]
