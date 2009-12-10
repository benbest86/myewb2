from django.core.management.base import NoArgsCommand
from django.core.management import ManagementUtility


class Command(NoArgsCommand):
    help = "Creates the database, then loads sample_data fixtures."

    requires_model_validation = False

    def handle_noargs(self, **options):
        utilityOne = ManagementUtility(['./manage.py', 'syncdb'])
        utilityOne.execute()
        
        utilityTwo = ManagementUtility(['./manage.py', 'loaddata', 'sample_data'])
        utilityTwo.execute()
        return 'Sample data loaded.'
