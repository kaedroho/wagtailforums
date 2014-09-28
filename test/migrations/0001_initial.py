# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import wagtailforums.models


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0002_initial_data'),
    ]

    operations = [
        migrations.CreateModel(
            name='ForumIndex',
            fields=[
                ('page_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
            ],
            options={
                'abstract': False,
            },
            bases=(wagtailforums.models.ForumPageMixin, 'wagtailcore.page'),
        ),
        migrations.CreateModel(
            name='ForumReply',
            fields=[
                ('page_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('message', models.TextField()),
                ('post_number', models.PositiveIntegerField(null=True, editable=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(wagtailforums.models.ForumPageMixin, 'wagtailcore.page'),
        ),
        migrations.CreateModel(
            name='ForumTopic',
            fields=[
                ('page_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('message', models.TextField()),
                ('post_number', models.PositiveIntegerField(null=True, editable=False)),
                ('custom_field', models.TextField()),
            ],
            options={
                'abstract': False,
            },
            bases=(wagtailforums.models.ForumPageMixin, 'wagtailcore.page'),
        ),
    ]
