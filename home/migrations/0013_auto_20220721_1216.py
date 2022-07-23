# Generated by Django 3.2.13 on 2022-07-21 12:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('home', '0012_installment_paymentreceivedon'),
    ]

    operations = [
        migrations.RenameField(
            model_name='installment',
            old_name='amountPaid',
            new_name='dueAmount',
        ),
        migrations.RenameField(
            model_name='installment',
            old_name='finePaid',
            new_name='paidAmount',
        ),
        migrations.RemoveField(
            model_name='installment',
            name='isPaid',
        ),
        migrations.RemoveField(
            model_name='installment',
            name='isReassigned',
        ),
        migrations.AddField(
            model_name='installment',
            name='NextDueDate',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='installment',
            name='latitude',
            field=models.CharField(default='0.0', max_length=200),
        ),
        migrations.AddField(
            model_name='installment',
            name='longitude',
            field=models.CharField(default='0.0', max_length=200),
        ),
        migrations.AddField(
            model_name='sale',
            name='projectName',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.CreateModel(
            name='InstallmentRemark',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('remark', models.CharField(blank=True, max_length=500, null=True)),
                ('latitude', models.CharField(default='0.0', max_length=200)),
                ('longitude', models.CharField(default='0.0', max_length=200)),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('lastUpdatedOn', models.DateTimeField(auto_now=True)),
                ('isDeleted', models.BooleanField(default=False)),
                ('addedBy', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                              to='home.staffuser')),
                ('installmentID', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                                    to='home.installment')),
            ],
            options={
                'verbose_name_plural': 'M) Installment Remark',
            },
        ),
    ]