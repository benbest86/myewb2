from django.contrib.auth.models import User
from emailconfirmation.models import EmailAddress

def get_email_user(email):
    email_user = None
    users_with_the_email = User.objects.filter(email=email)
    if users_with_the_email.count() > 0:
        email_user = users_with_the_email[0]
    else:
        users_with_the_email = EmailAddress.objects.get_users_for(email)
        if len(users_with_the_email) > 0:
            email_user = users_with_the_email[0]
            
    return email_user