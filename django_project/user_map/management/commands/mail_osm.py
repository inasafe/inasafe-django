# coding=utf-8
import csv

from django.core.management.base import BaseCommand
from django.core.mail import send_mass_mail
from django.template import loader


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
                users.append(row['email'])

        return users

    def handle(self, *args, **options):
        """How to use thiss:

        python manage.py mail_osm <the absolute path to csv file>
        """
        users = self.read_csv(args[0])
        email = loader.render_to_string(
            'user_map/mail/old_users_email.html')
        subject = 'The New Face of InaSAFE User Map'
        sender = 'InaSAFE - No Reply'

        messages = []
        for user in users:
            message = (subject, email, sender, [user])
            messages.append(message)
        messages = tuple(messages)
        # print messages
        send_mass_mail(messages)

        self.stdout.write('The email is sent successfully!')
