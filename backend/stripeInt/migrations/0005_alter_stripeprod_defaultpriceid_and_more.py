# Generated by Django 5.2.4 on 2025-07-08 22:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stripeInt', '0004_stripeprod_defaultpriceid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stripeprod',
            name='defaultPriceId',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='stripeprod',
            name='stripeId',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
