# Generated by Django 4.2.9 on 2025-04-27 17:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lung_disease', '0013_patientprofile_needs_doctor_assistance'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('message', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
