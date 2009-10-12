from django.core.management.base import LabelCommand
from emailconfirmation.models import EmailAddress, EmailConfirmation


class Command(LabelCommand):
    help = "Verifies any supplied emails if they exist as unverified emails for a single user."
    args = "[email]"
    label = 'email'

    requires_model_validation = False
    # Can't import settings during this command, because they haven't
    # necessarily been created.
    can_import_settings = True

    def handle_label(self, email, **options):
        try:
            email = EmailAddress.objects.get(email=email)
        except EmailAddress.MultipleObjectsReturned:
            return 'More than one instance of %s exists and therefore it cannot be verified.' % email
        except EmailAddress.DoesNotExist:
            return 'No instance of %s exists and therefore it cannot be verified.' % email

        if email.verified:
            return 'The email %s is already verified for user %s.' % (email.email, email.user)

        try:
            ck = email.emailconfirmation_set.all()[0].confirmation_key
        except IndexError:
            return 'No email confirmation message exists for this email.'
        email = EmailConfirmation.objects.confirm_email(ck)
        return 'Confirmed %s for user %s' % (email.email, email.user)

