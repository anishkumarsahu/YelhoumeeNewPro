# Generated by Django 3.2.13 on 2022-06-30 13:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staffuser',
            name='isActive',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
