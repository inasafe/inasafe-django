# coding=utf-8
import csv

from django.core.management.base import BaseCommand
from django.core.mail import send_mass_mail
from django.template import loader

from user_map.app_settings import DEFAULT_FROM_MAIL


class Command(BaseCommand):
    help = 'Email all the OSM trainers from csv file'

    def read_csv(self, csv_path):
        """Get the osm user email from the csv file.

        :param csv_path: The path to csv file.
        :type csv_path: str
        """
        users = []
        with open(csv_path) as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                user = {
                    'name': row['nama'],
                    'email': row['email']
                }
                users.append(user)

        return users

    def handle(self, *args, **options):
        """How to use this:

        python manage.py mail_osm <the absolute path to csv file>
        """
        users = self.read_csv(args[0])

        subject = 'The New Face of InaSAFE User Map'
        sender = 'InaSAFE - No Reply <%s>' % DEFAULT_FROM_MAIL

        messages = []
        for user in users:
            context = {
                'name': user['name']
            }
            email = loader.render_to_string(
                'user_map/mail/old_users_email.html', context)
            message = (subject, email, sender, [user['email']])
            messages.append(message)
        messages = tuple(messages)
        send_mass_mail(messages)

        self.stdout.write('The email is sent successfully!')
