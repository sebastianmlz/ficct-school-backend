# Generated by Django 5.2.1 on 2025-05-25 19:46

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academic', '0003_attendance'),
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Participation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('date', models.DateField()),
                ('level', models.CharField(choices=[('high', 'High'), ('medium', 'Medium'), ('low', 'Low'), ('none', 'None')], default='medium', max_length=20)),
                ('comments', models.TextField(blank=True, null=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participations', to='academic.course')),
                ('period', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participations', to='academic.period')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participations', to='authentication.student')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participations', to='academic.subject')),
            ],
            options={
                'ordering': ['-date'],
                'unique_together': {('student', 'course', 'subject', 'date', 'period')},
            },
        ),
    ]
