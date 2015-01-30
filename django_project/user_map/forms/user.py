# coding=utf-8
"""Django forms for User related routines."""
from django.contrib.gis import forms
from django.contrib.auth.forms import PasswordResetForm
from leaflet.forms.widgets import LeafletWidget

from user_map.models import User, InasafeRole, OsmRole
from user_map.forms.custom_widget import CustomClearableFileInput


class RegistrationForm(forms.ModelForm):
    """Form for user model."""
    name = forms.CharField(
        required=True,
        label='Name',
        widget=forms.TextInput(
            attrs={'placeholder': 'John Doe'})
    )
    email = forms.EmailField(
        required=True,
        label='Email',
        widget=forms.EmailInput(
            attrs={
                'placeholder': 'john@doe.com'})
    )
    image = forms.ImageField(
        required=False,
        widget=CustomClearableFileInput()
    )
    password = forms.CharField(
        required=True,
        label='Password',
        widget=forms.PasswordInput()
    )
    password2 = forms.CharField(
        required=True,
        label='Password (again)',
        widget=forms.PasswordInput()
    )
    website = forms.URLField(
        required=False,
        label='Website',
        widget=forms.URLInput(
            attrs={'placeholder': 'http://john.doe.com'})
    )
    inasafe_roles = forms.ModelMultipleChoiceField(
        required=True,
        label='Your InaSAFE role(s)',
        queryset=InasafeRole.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )
    osm_roles = forms.ModelMultipleChoiceField(
        required=False,
        label='Your OSM role(s)',
        queryset=OsmRole.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )
    osm_username = forms.CharField(
        required=False,
        label='OSM Username',
        widget=forms.TextInput(
            attrs={'placeholder': 'johndoe'})
    )
    location = forms.PointField(
        label='Click your location on the map',
        widget=LeafletWidget())
    email_updates = forms.BooleanField(
        required=False,
        label='Receive project news and updates'
    )

    class Meta:
        """Association between models and this form."""
        model = User
        fields = ['name', 'email', 'image', 'password', 'password2', 'website',
                  'inasafe_roles', 'osm_roles', 'osm_username', 'location',
                  'email_updates']

    def clean(self):
        """Verifies that the values entered into the password fields match."""
        cleaned_data = super(RegistrationForm, self).clean()
        if 'password' in cleaned_data and 'password2' in cleaned_data:
            if cleaned_data['password'] != cleaned_data['password2']:
                raise forms.ValidationError(
                    "Passwords don't match. Please enter both fields again.")
        return cleaned_data

    def save(self, commit=True):
        """Save form.

        :param commit: Whether committed to db or not.
        :type commit: bool
        """
        user = super(RegistrationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    """Form for user to log in."""
    class Meta:
        """Meta of the form."""
        fields = ['email', 'password']

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'john@doe.com'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Your s3cr3T password'})
    )


class BasicInformationForm(forms.ModelForm):
    """Form for Basic Information model."""
    name = forms.CharField(
        required=True,
        label='Your name',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'John Doe'})
    )
    email = forms.EmailField(
        required=True,
        label='Your email',
        widget=forms.EmailInput(
            attrs={
                'readonly': 'readonly',
                'placeholder': 'john@doe.com'})
    )
    image = forms.ImageField(
        required=False,
        widget=CustomClearableFileInput()
    )
    website = forms.URLField(
        required=False,
        label='Your website',
        widget=forms.URLInput(
            attrs={
                'placeholder': 'http://john.doe.com'})
    )
    inasafe_roles = forms.ModelMultipleChoiceField(
        required=True,
        label='Your InaSAFE role(s)',
        queryset=InasafeRole.objects.filter(sort_number__gte=1),
        widget=forms.CheckboxSelectMultiple
    )
    osm_roles = forms.ModelMultipleChoiceField(
        required=False,
        label='Your OSM role(s)',
        queryset=OsmRole.objects.filter(sort_number__gte=1),
        widget=forms.CheckboxSelectMultiple)
    osm_username = forms.CharField(
        required=False,
        label='OSM Username',
        widget=forms.TextInput(
            attrs={'placeholder': 'johndoe'}
        )
    )
    email_updates = forms.BooleanField(
        required=False,
        label='Receive project news and updates')
    location = forms.PointField(
        label='Click your location on the map',
        widget=LeafletWidget())

    class Meta:
        """Association between models and this form."""
        model = User
        fields = ['name', 'email', 'image', 'website', 'inasafe_roles',
                  'osm_roles', 'osm_username', 'location', 'email_updates']

    def save(self, commit=True):
        """Save form.

        :param commit: Whether committed to db or not.
        :type commit: bool
        """
        user = super(BasicInformationForm, self).save(commit=False)
        if commit:
            user.save()
        return user


class CustomPasswordResetForm(PasswordResetForm):
    """Form for password reset containing email input."""
    email = forms.EmailField(
        required=True,
        label='Email',
        widget=forms.EmailInput(
            attrs={
                'placeholder': 'john@doe.com'})
    )

    class Meta:
        """Association between models and this form."""
        model = User
