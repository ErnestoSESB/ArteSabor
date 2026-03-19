from django.db import migrations, models
import decimal

class Migration(migrations.Migration):

    dependencies = [
        ('ERP', '0002_alter_category_id_alter_productcategorylink_id_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='FinanceBox',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('cash_total', models.DecimalField(default=decimal.Decimal('0.00'), max_digits=12, decimal_places=2)),
                ('loan_total', models.DecimalField(default=decimal.Decimal('0.00'), max_digits=12, decimal_places=2)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='FinanceLog',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('action', models.CharField(max_length=32)),
                ('value', models.DecimalField(max_digits=12, decimal_places=2)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('description', models.CharField(max_length=255, blank=True)),
                ('box', models.ForeignKey(to='ERP.FinanceBox', on_delete=models.CASCADE, related_name='logs')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
