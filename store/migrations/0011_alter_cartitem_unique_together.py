# Generated by Django 5.1.7 on 2025-04-07 17:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0010_remove_cart_products_remove_cart_user_alter_cart_id_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='cartitem',
            unique_together={('cart', 'product')},
        ),
    ]
