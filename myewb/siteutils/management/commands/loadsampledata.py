from django.core.management.base import NoArgsCommand
from django.core.management import ManagementUtility


class Command(NoArgsCommand):
    help = "Loads all fixtures named sample_data."

    requires_model_validation = False

    def handle_noargs(self, **options):
        utility = ManagementUtility(['./manage.py', 'loaddata', 'sample_data'])
        utility.execute()
        return 'Sample data loaded.'

