# Generated by Django 3.2.13 on 2022-07-21 12:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('home', '0016_auto_20220721_1227'),
    ]

    operations = [
        migrations.AddField(
            model_name='sale',
            name='saleNo',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
