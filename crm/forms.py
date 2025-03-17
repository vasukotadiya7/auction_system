
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from django import forms
from .models import Category, CustomUser,Profile,Product,ShippingDetails
from django.forms.widgets import PasswordInput,TextInput
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Bid


# Validate that the given date is in the future (starting from tomorrow).
    
# def validate_future_date(value):
    
#     if value <= datetime.now().date() + timedelta(days=1):
#         raise ValidationError(
#             _('Date must start from tomorrow.'),
#             params={'value': value},
#         )



# Create a user/register

class CreateUserForm(UserCreationForm):

    birthday = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}), required=False, help_text='Format: YYYY-MM-DD')
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False, help_text='Enter your address here.')

    class Meta:

        model = CustomUser
        fields = ['first_name','last_name','username', 'email','password1','password2','birthday','address']
    
    # def __init__(self, *args, **kwargs):
    #     super(CreateUserForm, self).__init__(*args, **kwargs)
    #     self.fields['birthday'].widget.attrs['type'] = 'date'
    #     self.fields['address'].widget.attrs['rows'] = 3
    #     self.fields['address'].widget.attrs['placeholder'] = 'Enter your address here.'
    #     self.fields['birthday'].help_text = 'Format: YYYY-MM-DD'
# Authenticate the user
        
class LoginForm(AuthenticationForm):

    username = forms.CharField(widget=TextInput())
    password = forms.CharField(widget=PasswordInput())
    

class UserUpdateForm(forms.ModelForm):
    email= forms.EmailField()

    class Meta:

        model = User
        fields = ['first_name','last_name','username', 'email']

class ProfileUpdateForm(forms.ModelForm):

    birthday = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}), required=False, help_text='Format: DD-MM-YYYY')
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 1}), required=False, help_text='Enter your address here.')
    phone = forms.CharField(widget=forms.TextInput(attrs={'type': 'number'}), min_length=10)
    aadhar_card = forms.CharField(widget=forms.TextInput(attrs={'type': 'number'}), min_length=12)
    

    class Meta:
        model=Profile
        fields = ['image','phone','birthday','address','aadhar_card']


class ProductForm(forms.ModelForm):

    # date = forms.DateField(validators=[validate_future_date])
    
    class Meta:
        model = Product
        fields = ['user', 'Category', 'product_name', 'image', 'min_price', 'price_interval', 'date', 'start_time', 'end_time', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, user, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields['Category'].queryset = Category.objects.all()  # Update queryset for category field
        self.fields['user'].widget = forms.HiddenInput()
        self.fields['user'].required = False  # Make user field not required

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        # Validate start time and end time
        if start_time and end_time:
            start_datetime = datetime.combine(datetime.now().date(), start_time)
            end_datetime = datetime.combine(datetime.now().date(), end_time)

            if start_datetime >= end_datetime:
                raise ValidationError(_("End time must be greater than start time."))

            # Validate the time difference between start time and end time
            time_diff = end_datetime - start_datetime
            if time_diff.seconds not in (3600, 7200):  # Check if the difference is not exactly 1 or 2 hours
                raise ValidationError(_("The difference between start time and end time must be either 1 or 2 hours."))

        return cleaned_data

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['amount']


class ShippingDetailsForm(forms.ModelForm):

    address = forms.CharField(widget=forms.TextInput(attrs={'rows': 1}), required=True, help_text='Enter your address here.')
    city = forms.CharField(widget=forms.TextInput(attrs={'rows': 1}), required=True, help_text='Enter your city here.')
    state = forms.CharField(widget=forms.TextInput(attrs={'rows': 1}), required=True, help_text='Enter your state here.')
    country = forms.CharField(widget=forms.TextInput(attrs={'rows': 1}), required=True, help_text='Enter your country here.')
    pincode = forms.CharField(widget=forms.NumberInput(attrs={'min': 100000}), required=True, help_text='Enter your pincode here.')

    class Meta:
        model = ShippingDetails
        fields = ['address', 'city', 'state', 'country', 'pincode']



