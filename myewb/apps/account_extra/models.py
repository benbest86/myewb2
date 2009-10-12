from django.db.models.signals import post_save
from emailconfirmation.models import EmailAddress

def clean_up_email_addresses(sender, instance, created, **kwargs):
    """
    Cleans up unverified emails with the same email and deletes any users who
    have no remaining emails.
    """
    if instance.verified:
        others = EmailAddress.objects.filter(email__iexact=instance.email, verified=False)
        for o in others:
            u = o.user
            o.delete()
            if u.emailaddress_set.count() == 0:
                u.delete()
post_save.connect(clean_up_email_addresses, sender=EmailAddress)
