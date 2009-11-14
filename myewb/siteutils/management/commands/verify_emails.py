from django.core.management.base import NoArgsCommand
from emailconfirmation.models import EmailAddress, EmailConfirmation


class Command(NoArgsCommand):
    help = "Verifies all unverified emails."

    requires_model_validation = False

    def handle_noargs(self, **options):
        msgs = []
        emails = EmailAddress.objects.filter(verified=False)
        for email in emails:
            try:
                ck = email.emailconfirmation_set.all()[0].confirmation_key
                email = EmailConfirmation.objects.confirm_email(ck)
                msgs.append('Confirmed %s for user %s' % (email.email, email.user))
            except IndexError:
                msgs.append('No email confirmation message exists for %s.' % email.email)
        msgs = msgs or ['No unverified emails found.',]
        return '\n'.join(msgs)

