# Generated by Django 2.2.5 on 2022-08-31 21:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kindergarden', '0004_time_tracker'),
    ]

    operations = [
        migrations.AlterField(
            model_name='day',
            name='date',
            field=models.DateField(db_index=True),
        ),
    ]
