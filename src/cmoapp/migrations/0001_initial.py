# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-13 17:00
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('login', models.CharField(max_length=100)),
                ('password', models.CharField(max_length=1024)),
                ('type', models.CharField(choices=[('Analyst', 'Analyst'), ('Operator', 'Operator'), ('Chief', 'Chief')], max_length=20)),
            ],
            options={
                'ordering': ['login'],
            },
        ),
        migrations.CreateModel(
            name='ActionPlan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plan_number', models.IntegerField(editable=False, validators=[django.core.validators.MinValueValidator(1)])),
                ('description', models.TextField(blank=True, null=True)),
                ('outgoing_time', models.DateTimeField(editable=False, null=True)),
                ('status', models.CharField(choices=[('Planning', 'Planning'), ('CORequest', 'Requesting CO'), ('PMORequest', 'Requesting PMO'), ('Rejected', 'Rejected'), ('PMOApproved', 'Approved')], max_length=20)),
                ('resolution_time', models.DurationField()),
                ('projected_casualties', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('type', models.CharField(choices=[('Combat', 'Combat'), ('Clean-up', 'Clean Up'), ('Resolved', 'Resolved')], max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('author', models.CharField(choices=[('PMO', "Prime Minister's Office"), ('CO', 'Chief Officer')], max_length=20)),
                ('timeCreated', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('actionPlan', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='cmoapp.ActionPlan')),
            ],
        ),
        migrations.CreateModel(
            name='Crisis',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('crisis_title', models.CharField(max_length=50, null=True)),
                ('status', models.CharField(choices=[('Clean-up', 'Clean Up'), ('Ongoing', 'Ongoing'), ('Resolved', 'Resolved')], max_length=20)),
                ('analyst', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='cmoapp.Account')),
            ],
        ),
        migrations.CreateModel(
            name='CrisisReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('datetime', models.DateTimeField()),
                ('latitude', models.DecimalField(decimal_places=8, max_digits=12)),
                ('longitude', models.DecimalField(decimal_places=8, max_digits=12)),
                ('radius', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)], verbose_name='Radius(Metres)')),
                ('crisis', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cmoapp.Crisis')),
            ],
        ),
        migrations.CreateModel(
            name='CrisisType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='EFUpdate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField()),
                ('affectedRadius', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Affected Radius')),
                ('totalInjured', models.IntegerField(verbose_name='Total Injured')),
                ('totalDeaths', models.IntegerField(verbose_name='Total Deaths')),
                ('duration', models.DurationField(null=True)),
                ('description', models.TextField()),
                ('type', models.CharField(choices=[('Request', 'Request'), ('Notification', 'Notification')], max_length=40)),
                ('actionPlan', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='cmoapp.ActionPlan')),
                ('crisis', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cmoapp.Crisis')),
            ],
        ),
        migrations.CreateModel(
            name='Force',
            fields=[
                ('name', models.CharField(max_length=200, primary_key=True, serialize=False)),
                ('currentUtilisation', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ForceDeployment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recommended', models.DecimalField(decimal_places=2, max_digits=5)),
                ('max', models.DecimalField(decimal_places=2, max_digits=5)),
                ('actionPlan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cmoapp.ActionPlan')),
                ('name', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='cmoapp.Force')),
            ],
        ),
        migrations.CreateModel(
            name='ForceUtilization',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('utilization', models.DecimalField(decimal_places=2, max_digits=5)),
                ('name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cmoapp.Force')),
                ('update', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cmoapp.EFUpdate')),
            ],
        ),
        migrations.CreateModel(
            name='Notifications',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField()),
                ('text', models.TextField()),
                ('new', models.BooleanField(default=True)),
                ('time_added', models.DateTimeField(auto_now_add=True)),
                ('_for', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cmoapp.Account')),
            ],
        ),
        migrations.AddField(
            model_name='crisisreport',
            name='crisisType',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='cmoapp.CrisisType'),
        ),
        migrations.AddField(
            model_name='actionplan',
            name='crisis',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cmoapp.Crisis'),
        ),
    ]
