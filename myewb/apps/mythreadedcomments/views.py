from threadedcomments.views import *
from mythreadedcomments.forms import MyThreadedCommentForm

def comment(*args, **kwargs):
    """
    Thin wrapper around free_comment which adds login_required status and also assigns
    the ``model`` to be ``ThreadedComment``.
    """
    kwargs['model'] = ThreadedComment
    kwargs['form_class'] = MyThreadedCommentForm
    return free_comment(*args, **kwargs)
comment = login_required(comment)