# Generated by Django 2.0.3 on 2018-04-02 06:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TestModel', '0002_auto_20180402_1115'),
    ]

    operations = [
        migrations.RenameField(
            model_name='assignversion',
            old_name='publishplan_id',
            new_name='publish_plan_id',
        ),
        migrations.AddField(
            model_name='staff',
            name='type',
            field=models.IntegerField(default=10),
        ),
    ]
