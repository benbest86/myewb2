"""myEWB fix for attachments app
In some cases, maybe 1 in 10, attachments are saved with the wrong permissions
and can't be read by the webserver - leading to Forbidden errors when trying 
to download the file.

This listener chmod's all files after saving to ensure this doesn't happen.
Later, it can also be used to ensure there aren't any encoding/etc issues that 
prevent the file from being found.

This file is part of myEWB
Copyright 2010 Engineers Without Borders Canada

@author Francis Kung
"""

import settings, os
from attachments.models import Attachment
from django.db.models.signals import post_save
from stat import *

def attachment_fix(sender, instance, created, **kwargs):
    if created:
        #filepath = instance.attachment_file
        #file = os.path.join(settings.MEDIA_ROOT, filepath)
        file = instance.attachment_file.path
        
        if os.stat(file):
            os.chmod(file, S_IRUSR | S_IWUSR | S_IRGRP | S_IROTH)
        else:
            # probably an encoding problem in the filename...?
            pass 
        
post_save.connect(attachment_fix, sender=Attachment)
