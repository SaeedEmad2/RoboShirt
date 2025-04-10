# Generated by Django 5.1.7 on 2025-03-15 18:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('store', '0002_custmor_cart_custmor_product_custmor'),
    ]

    operations = [
        migrations.CreateModel(
            name='Design',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('design_description', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('custmor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='store.custmor')),
            ],
        ),
    ]
