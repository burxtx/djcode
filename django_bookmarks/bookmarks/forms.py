from django import newforms as forms

class RegistrationForm(forms.Form):
    username = forms.CharField(label='Username', max_length=20)
    email = forms.EmailField(label='Email')
    password1 = forms.CharField(
        label = 'Password',
        widget=forms.PasswordInput()
    )
    password2 = forms.CharField(
        label = 'Password (Again)',
        widget=forms.PasswordInput()
    )
