# Generated by Django 3.1.5 on 2021-07-29 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DCS1', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dairyproducts',
            name='id',
        ),
        migrations.AlterField(
            model_name='dairyproducts',
            name='barcode',
            field=models.CharField(max_length=256, primary_key=True, serialize=False),
        ),
    ]
