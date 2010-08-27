from django.core.management.base import NoArgsCommand, CommandError

import mailchimp

class Command(NoArgsCommand):
    help = "Runs the MailChimp synchronization queue"

    requires_model_validation = False
    can_import_settings = True

    def handle_noargs(self, **options):
        mailchimp.sync.run()
