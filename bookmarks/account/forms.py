# CREATE USERLOGIN FORM
from django import forms
from django.contrib.auth import get_user_model
from .models import Profile
from django.contrib.auth.models import User
# custom login form
# class LoginForm(forms.Form):
#     username = forms.CharField()
#     password = forms.CharField(widget=forms.PasswordInput)
    
class UserRegistrationForm(forms.ModelForm): 
    """
    THIS IS THE MAIN FUNCTION TO ACCEPT AND VALIDATE USER REGISTRATION FORM, validate it using clean_password2 and clean_email functions
    """
    password = forms.CharField(
        label='password',
        widget=forms.PasswordInput
    ) #accept password (we changed the behaviour of the text field using widget = fomr.PasswordInput)
    password2 = forms.CharField(
        label='Repeat password',
        widget=forms.PasswordInput
    )
    class Meta:
        model = get_user_model() # we use built in django get_user_model() to call only the relevant informations
        fields = ['username', 'first_name', 'email'] 
    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError("password don't match")
        return cd['password2']
    def clean_email(self):
        data = self.cleaned_data['email']
        if User.objects.filter(email=data).exists():
            raise forms.ValidationError('Email already in use.')
        return data
    
# profile manager
class UserEditForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email']
    def clean_email(self):
        """
        Validate the 'email' field for uniqueness.
        Retrieves the email value from self.cleaned_data and checks whether any other
        User record (excluding the form's own model instance) already uses that email.
        If a duplicate exists, raises forms.ValidationError; otherwise returns the
        validated email string.
        Note: self.instance is the model instance bound to this form (set by Django's
        ModelForm machinery). When editing an existing user it refers to that User
        object (so self.instance.id excludes the current user from the uniqueness
        check). When creating a new user, self.instance will typically be an unsaved
        instance with a None primary key.
        """
        data = self.cleaned_data['email']
        qs = User.objects.exclude(id = self.instance.id).filter(email=data)
        
        if qs.exists():
            raise forms.ValidationError('Email already in use.')
        return data
    
class ProfileEditForm(forms.ModelForm):
    """
    Form for editing a Profile instance.

    This ModelForm exposes only the 'date_of_birth' and 'photo' fields from the Profile model. It leverages Django's ModelForm machinery to:
    - automatically generate form fields and validation from the model,
    - bind data (and files) via ProfileEditForm(request.POST, request.FILES, instance=profile),
    - validate with is_valid() and persist changes with save() (use save(commit=False) to adjust before saving).

    Usage notes:
    - The HTML form must use enctype="multipart/form-data" to upload the 'photo'.
    - Validation is handled by the form fields and any model-level clean() methods.
    - Only the listed fields are editable; other Profile attributes are not exposed by this form.
    """
    class Meta:
        model = Profile
        fields = ['date_of_birth', 'photo']