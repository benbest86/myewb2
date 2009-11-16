from django.core.management.base import NoArgsCommand
from optparse import make_option
import sys
import os

class Command(NoArgsCommand):
    help = 'Runs the test suite for all applications in the apps folder.'

    requires_model_validation = False

    def handle_noargs(self, **options):
        # most of this stolen from django.core.commands.test
        from django.conf import settings

        verbosity = int(options.get('verbosity', 1))
        interactive = options.get('interactive', True)
    
        test_path = settings.TEST_RUNNER.split('.')
        # filter contents of apps directory for non-files (directories)
        # test each app name against settings.INSTALLED_APPS
        apps = [app for app in os.listdir('apps') if os.path.isfile(app) == 0 and app in settings.INSTALLED_APPS]
        valid_apps = []
        # testings requires apps to have a models.py file, so check here
        for app in apps:
            try:
                __import__('%s.models' % app)
                valid_apps.append(app)
            except:
                pass
        # Allow for Python 2.5 relative paths
        if len(test_path) > 1:
            test_module_name = '.'.join(test_path[:-1])
        else:
            test_module_name = '.'
        test_module = __import__(test_module_name, {}, {}, test_path[-1])
        test_runner = getattr(test_module, test_path[-1])

        print 'Testing apps: %s' % ', '.join(valid_apps)
        failures = test_runner(valid_apps, verbosity=verbosity, interactive=interactive)
        if failures:
            sys.exit(failures)
