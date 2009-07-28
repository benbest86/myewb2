from django import forms
from django.utils.translation import ugettext_lazy as _

from networks.models import Network, NetworkMember

# @@@ we should have auto slugs, even if suggested and overrideable

class NetworkForm(forms.ModelForm):
    
    slug = forms.SlugField(max_length=20,
        help_text = _("a short version of the name consisting only of letters, numbers, underscores and hyphens."),
        error_message = _("This value must contain only letters, numbers, underscores and hyphens."))
            
    def clean_slug(self):
        
        if Network.objects.filter(slug__iexact=self.cleaned_data["slug"]).count() > 0:
            if self.instance and self.cleaned_data["slug"] == self.instance.slug:
                pass # same instance
            else:
                raise forms.ValidationError(_("A network already exists with that slug."))
        return self.cleaned_data["slug"].lower()
    
    def clean_name(self):

        if Network.objects.filter(name__iexact=self.cleaned_data["name"]).count() > 0:
            if self.instance and self.cleaned_data["name"] == self.instance.name:
                pass # same instance
            else:
                raise forms.ValidationError(_("A network already exists with that name."))
        return self.cleaned_data["name"]
    
    class Meta:
        model = Network
        fields = ('name', 'slug', 'network_type', 'description')


# @@@ is this the right approach, to have two forms where creation and update fields differ?

# class NetworkUpdateForm(forms.ModelForm):
#     
#     def clean_name(self):
#         if Network.objects.filter(name__iexact=self.cleaned_data["name"]).count() > 0:
#             if self.cleaned_data["name"] == self.instance.name:
#                 pass # same instance
#             else:
#                 raise forms.ValidationError(_("A network already exists with that name."))
#         return self.cleaned_data["name"]
#     
#     class Meta:
#         model = Network
#         fields = ('name', 'description')
        
class NetworkMemberForm(forms.ModelForm):

    class Meta:
        model = NetworkMember
        fields = ('user', 'is_admin', 'admin_title')
