# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('agency', '0001_initial'),
        ('jurisdiction', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('foia', '0001_initial'),
        ('crowdfund', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlacklistDomain',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('domain', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_done', models.DateTimeField(null=True, blank=True)),
                ('resolved', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['date_created'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StatusChangeTask',
            fields=[
                ('task_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='task.Task')),
                ('old_status', models.CharField(max_length=255)),
                ('foia', models.ForeignKey(to='foia.FOIARequest')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=('task.task',),
        ),
        migrations.CreateModel(
            name='StaleAgencyTask',
            fields=[
                ('task_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='task.Task')),
                ('agency', models.ForeignKey(to='agency.Agency')),
            ],
            options={
            },
            bases=('task.task',),
        ),
        migrations.CreateModel(
            name='SnailMailTask',
            fields=[
                ('task_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='task.Task')),
                ('category', models.CharField(max_length=1, choices=[(b'a', b'Appeal'), (b'n', b'New'), (b'u', b'Update'), (b'f', b'Followup')])),
                ('communication', models.ForeignKey(to='foia.FOIACommunication')),
            ],
            options={
            },
            bases=('task.task',),
        ),
        migrations.CreateModel(
            name='ResponseTask',
            fields=[
                ('task_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='task.Task')),
                ('communication', models.ForeignKey(to='foia.FOIACommunication')),
            ],
            options={
            },
            bases=('task.task',),
        ),
        migrations.CreateModel(
            name='RejectedEmailTask',
            fields=[
                ('task_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='task.Task')),
                ('category', models.CharField(max_length=1, choices=[(b'b', b'Bounced'), (b'd', b'Dropped')])),
                ('email', models.EmailField(max_length=75, blank=True)),
                ('error', models.TextField(blank=True)),
                ('foia', models.ForeignKey(blank=True, to='foia.FOIARequest', null=True)),
            ],
            options={
            },
            bases=('task.task',),
        ),
        migrations.CreateModel(
            name='PaymentTask',
            fields=[
                ('task_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='task.Task')),
                ('amount', models.DecimalField(max_digits=8, decimal_places=2)),
                ('foia', models.ForeignKey(to='foia.FOIARequest')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=('task.task',),
        ),
        migrations.CreateModel(
            name='OrphanTask',
            fields=[
                ('task_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='task.Task')),
                ('reason', models.CharField(max_length=2, choices=[(b'bs', b'Bad Sender'), (b'ib', b'Incoming Blocked'), (b'ia', b'Invalid Address')])),
                ('address', models.CharField(max_length=255)),
                ('communication', models.ForeignKey(to='foia.FOIACommunication')),
            ],
            options={
            },
            bases=('task.task',),
        ),
        migrations.CreateModel(
            name='NewAgencyTask',
            fields=[
                ('task_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='task.Task')),
                ('agency', models.ForeignKey(to='agency.Agency')),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=('task.task',),
        ),
        migrations.CreateModel(
            name='MultiRequestTask',
            fields=[
                ('task_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='task.Task')),
                ('multirequest', models.ForeignKey(to='foia.FOIAMultiRequest')),
            ],
            options={
            },
            bases=('task.task',),
        ),
        migrations.CreateModel(
            name='GenericTask',
            fields=[
                ('task_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='task.Task')),
                ('subject', models.CharField(max_length=255)),
                ('body', models.TextField(blank=True)),
            ],
            options={
            },
            bases=('task.task',),
        ),
        migrations.CreateModel(
            name='FlaggedTask',
            fields=[
                ('task_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='task.Task')),
                ('text', models.TextField()),
                ('agency', models.ForeignKey(blank=True, to='agency.Agency', null=True)),
                ('foia', models.ForeignKey(blank=True, to='foia.FOIARequest', null=True)),
                ('jurisdiction', models.ForeignKey(blank=True, to='jurisdiction.Jurisdiction', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=('task.task',),
        ),
        migrations.CreateModel(
            name='FailedFaxTask',
            fields=[
                ('task_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='task.Task')),
                ('communication', models.ForeignKey(to='foia.FOIACommunication')),
            ],
            options={
            },
            bases=('task.task',),
        ),
        migrations.CreateModel(
            name='CrowdfundTask',
            fields=[
                ('task_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='task.Task')),
                ('crowdfund', models.ForeignKey(to='crowdfund.CrowdfundRequest')),
            ],
            options={
            },
            bases=('task.task',),
        ),
        migrations.AddField(
            model_name='task',
            name='assigned',
            field=models.ForeignKey(related_name='assigned_tasks', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='task',
            name='resolved_by',
            field=models.ForeignKey(related_name='resolved_tasks', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
    ]
