# Generated by Django 4.2.9 on 2025-04-25 17:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lung_disease', '0012_patientprofile_delete_uploadedimage'),
    ]

    operations = [
        migrations.AddField(
            model_name='patientprofile',
            name='needs_doctor_assistance',
            field=models.BooleanField(default=False),
        ),
    ]
