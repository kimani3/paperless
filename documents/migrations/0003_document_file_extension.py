# Generated by Django 5.0.6 on 2024-10-01 13:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0002_alter_document_folder'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='file_extension',
            field=models.CharField(default=' ', max_length=255),
            preserve_default=False,
        ),
    ]