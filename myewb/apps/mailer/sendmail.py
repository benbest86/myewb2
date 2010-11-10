from django.template import Context, loader
from django.utils.encoding import force_unicode
from mailer.models import Email
from lxml.html.clean import clean_html, autolink_html, Cleaner


def send_mail(subject=None, txtMessage=None, htmlMessage=None,
              fromemail=None, recipients=None, shortname=None,
              priority=None, context={}, use_template=True,
              lang='en', cc=None, bcc=None):

    # try to be backwards-compatible
    if htmlMessage and recipients == None:
        recipients = fromemail
        fromemail = htmlMessage
        htmlMessage = None

    if not htmlMessage:
        htmlMessage = txtMessage.replace("\n", "<br/>")
        htmlMessage = clean_html(htmlMessage)
        htmlMessage = autolink_html(htmlMessage)
        
    if not txtMessage:
        txtMessage = htmlMessage
        context['do_text_conversion'] = True
        # TODO: do a fancy strip tags thing
            
    subject = force_unicode(subject)
    txtMessage = force_unicode(txtMessage)
    htmlMessage = force_unicode(htmlMessage)

    if not context.get('do_text_conversion', None):
        context['do_text_conversion'] = False
    if use_template:
        context['body'] = htmlMessage
        htmlMessage = loader.get_template("email_template.html").render(Context(context))
        
        context['body'] = txtMessage
        txtMessage = loader.get_template("email_template.txt").render(Context(context))
    
    else:
        context['body'] = txtMessage
        txtMessage = loader.get_template("email_template_clean.txt").render(Context(context))
    
    recips = ",".join(recipients)
    cc_string = None
    bcc_string = None
    if cc:
        cc_string = ",".join(cc)
    if bcc:
        bcc_string = ",".join(bcc)
            
    if shortname:
        shortname = shortname.lower()
        Email.objects.create(recipients=recips,
                             shortName=shortname,
                             sender=fromemail,
                             subject=subject,
                             textMessage=txtMessage,
                             htmlMessage=htmlMessage,
                             lang=lang,
                             cc=cc_string,
                             bcc=bcc_string)
    else:
        Email.objects.create(recipients=recips,
                             shortName=shortname,
                             sender=fromemail,
                             subject=subject,
                             textMessage=txtMessage,
                             htmlMessage=htmlMessage,
                             lang=lang,
                             cc=cc_string,
                             bcc=bcc_string)
