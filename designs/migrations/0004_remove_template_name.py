# Generated by Django 5.1.7 on 2025-04-14 13:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('designs', '0003_template'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='template',
            name='name',
        ),
    ]
