# coding=utf-8
import sqlite3

from django.core.management.base import BaseCommand
from django.core.mail import send_mass_mail
from django.template import loader


class Command(BaseCommand):
    help = 'Email all the users from the old User Map'

    def read_sqlite_db(self, db_path):
        """Get the old users' email from an sqlite db.

        :param db_path: The path to sqlite db.
        :type db_path: str
        """
        connection = sqlite3.connect(db_path)

        users = []
        with connection:
            cur = connection.cursor()
            cur.execute("SELECT * FROM user")
            rows = cur.fetchall()

            for row in rows:
                user = {
                    'name': row[2],
                    'email': row[3]
                }
                users.append(user)
        return users

    def handle(self, *args, **options):
        """How to use:

        python manage.py mail_old_users <the absolute path to the sqlite db>
        """
        users = self.read_sqlite_db(args[0])
        email = loader.render_to_string(
            'user_map/mail/old_users_email.html')
        subject = 'The New Face of InaSAFE User Map'
        sender = 'InaSAFE - No Reply'

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
