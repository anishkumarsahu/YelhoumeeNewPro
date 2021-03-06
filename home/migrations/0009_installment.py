# Generated by Django 3.2.13 on 2022-07-14 16:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('home', '0008_sale_deliveryphoto'),
    ]

    operations = [
        migrations.CreateModel(
            name='Installment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('installmentDate', models.DateField(blank=True, null=True)),
                ('amountPaid', models.FloatField(default=0.0)),
                ('finePaid', models.FloatField(default=0.0)),
                ('remark', models.CharField(blank=True, max_length=500, null=True)),
                ('isPaid', models.BooleanField()),
                ('isReassigned', models.BooleanField()),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('lastUpdatedOn', models.DateTimeField(auto_now=True)),
                ('isDeleted', models.BooleanField(default=False)),
                ('assignedTo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                                 related_name='AssignedToInstallment', to='home.staffuser')),
                ('collectedBy', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                                  related_name='CollectedBy', to='home.staffuser')),
                ('saleID',
                 models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='home.sale')),
            ],
            options={
                'verbose_name_plural': 'L) Installment Date List',
            },
        ),
    ]
