# Generated by Django 3.2.13 on 2022-07-14 11:21

from django.db import migrations
import stdimage.models


class Migration(migrations.Migration):
    dependencies = [
        ('home', '0007_sale'),
    ]

    operations = [
        migrations.AddField(
            model_name='sale',
            name='deliveryPhoto',
            field=stdimage.models.StdImageField(blank=True, force_min_size=False, upload_to='deliveryPhoto',
                                                variations={'large': (600, 400), 'medium': (300, 200),
                                                            'thumbnail': (50, 50, True)}),
        ),
    ]
