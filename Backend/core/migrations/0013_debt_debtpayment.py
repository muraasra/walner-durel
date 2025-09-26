from decimal import Decimal

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_journal_core_journa_date_op_a99831_idx_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Debt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reference', models.CharField(max_length=50, unique=True)),
                ('machine_description', models.TextField()),
                ('technician_name', models.CharField(max_length=255)),
                ('reason', models.CharField(blank=True, max_length=255)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('partially_paid', 'Partially Paid'), ('paid', 'Paid')], default='pending', max_length=20)),
                ('expected_return_date', models.DateField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='DebtPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('debt', models.ForeignKey(on_delete=models.CASCADE, related_name='payments', to='core.debt')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='debt',
            index=models.Index(fields=['status'], name='core_debt_status_idx'),
        ),
        migrations.AddIndex(
            model_name='debt',
            index=models.Index(fields=['technician_name'], name='core_debt_technician_idx'),
        ),
        migrations.AddIndex(
            model_name='debt',
            index=models.Index(fields=['created_at'], name='core_debt_created_idx'),
        ),
    ]