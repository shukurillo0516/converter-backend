# Generated by Django 4.0.3 on 2022-09-10 06:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spreadsheet', '0003_row_alter_order_delivery_time_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='number',
            field=models.IntegerField(blank=True, null=True, verbose_name='№'),
        ),
        migrations.AlterField(
            model_name='order',
            name='row_number',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
