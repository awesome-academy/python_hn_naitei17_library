# Generated by Django 4.2.1 on 2023-05-24 08:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0014_alter_borrowing_status'),
    ]

    operations = [
        migrations.DeleteModel(
            name='BookInstance',
        ),
    ]
