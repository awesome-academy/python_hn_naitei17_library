# Generated by Django 4.2.1 on 2023-05-24 04:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0012_alter_borrowing_options'),
    ]

    operations = [
        migrations.RenameField(
            model_name='borrowing',
            old_name='refuse_reason',
            new_name='decline_reason',
        ),
    ]
