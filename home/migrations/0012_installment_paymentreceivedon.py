# Generated by Django 3.2.13 on 2022-07-15 14:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('home', '0011_sale_isclosed'),
    ]

    operations = [
        migrations.AddField(
            model_name='installment',
            name='paymentReceivedOn',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]