# -*- coding: utf-8 -*-
{
    'name': 'Event Sequence',
    'version': '1.0',
    'website': 'https://www.odoo.com/page/events',
    'category': 'Marketing',
    'summary': 'Trainings, Conferences, Meetings, Exhibitions, Registrations',
    'description': """
Organization and management of Events.
======================================

The event module allows you to efficiently organize events and all related tasks: planning, registration tracking,
attendances, etc.

Key Features
------------
* Manage your Events and Registrations
* Use emails to automatically confirm and send acknowledgments for any event registration
""",
    'depends': ['event'],
    'data': [
        'views/event_views.xml',
        'data/event_sequence.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}
