"""
Django command to wait for the database to be available
"""

import time
from psycopg2 import OperationalError as Psycopg2Error
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Django command to wait for database
    """

    def handle(self, *args, **options):
        """
        Command entrypoint
        """

        self.stdout.write("Checking database availability\n")
        db_up = False
        seconds_cnt = 0
        while not db_up:
            try:
                self.check(databases=['default'])
                db_up = True
                self.stdout.write(
                    self.style.WARNING(
                        "Available within {} seconds".format(seconds_cnt)))
                self.stdout.write(self.style.SUCCESS("Database available!"))
            except(Psycopg2Error, OperationalError):
                seconds_cnt += 1
                CURSOR_UP_ONE = '\x1b[1A'
                ERASE_LINE = '\x1b[1M'
                self.stdout.write(CURSOR_UP_ONE + ERASE_LINE + CURSOR_UP_ONE)
                self.stdout.write(
                    self.style.WARNING(
                        "Database unavailable waiting... {} seconds"
                        .format(seconds_cnt)))
                time.sleep(1)
