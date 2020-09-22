from mailjet_rest import Client
import os
from django.shortcuts import render
from .forms import RegisterForm
from .forms import LoginForm
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.utils.encoding import force_bytes
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode
from django.utils.http import urlsafe_base64_encode
from django.contrib import messages
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout

from django.utils.translation import gettext as _

from . import tokens as t
from mailjet_rest import Client
import os
api_key = '39b93cd219afa7bbfda355795fcf7b94'
api_secret = 'f29eb65e1b46c83c577075c93612ba51'
mailjet = Client(auth=(api_key, api_secret), version='v3.1')



def login(request):
    #messages.add_message(request, messages.INFO, 'Hello world.')
    if request.method=="POST":
        form=LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            pwd = form.cleaned_data['password']

            try:
                user = User.objects.get(email=email)

                if not user.is_active:
                    messages.warning(request, 'Your account is not activated.')
                    return redirect('login')

                else:
                    print('user is active',user.username)

                if user is not None:
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    auth_login(request,user)
                    messages.info(request, 'Successfully logged in!')
                    return redirect('project_home')
                else:
                    messages.error(request, 'Entered password is wrong.')
                    return redirect('login')
            except:
                messages.error(request, 'User does not exists.')
                return redirect('login')



        else:
            print('not valid')
            form = LoginForm()
    else:
        form = LoginForm()
    return render(request, "form_base.html", {"form":form,"title":'Login',"button":'Login'})

# Create your views here.
def register(request):
    if request.method == "POST":
        form=RegisterForm(request.POST)


        if form.is_valid():
            print('form is valid')
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            subject = 'Activate Your TrustexUX Account'
            message = render_to_string('account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': t.account_activation_token.make_token(user),
                })

            print('base64 code uid:',urlsafe_base64_encode(force_bytes(user.pk)))
            print(t.account_activation_token.make_token(user))
            data = {
              'Messages': [
                {
                  "From": {
                    "Email": "pankajch@tlu.ee",
                    "Name": "TrustedUX Team "
                  },
                  "To": [
                    {
                      "Email": user.email,
                    }
                  ],
                  "Subject": "Activate your TrustedUX account.",
                  "TextPart": message,
                }
              ]
            }



            result = mailjet.send.create(data=data)
            if result.status_code == 200:

                print('user saved')
            print(result.status_code)
            messages.info(request, 'An email with instructions to activate your account has been sent.')
            return redirect('login')


        else:
            print('Form is not valid')

    else:
        form = RegisterForm()

    return render(request, "register.html", {"form":form})
# Create your views here.


def activate(request, uidb64, token):
    print(uidb64)
    print(force_text(urlsafe_base64_decode(uidb64)))
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        print(uid)
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
        print('user does not exists')

    if user is not None and t.account_activation_token.check_token(user, token):
        user.is_active = True

        user.save()
        messages.success(request, 'Your account is activated successfully!.You can login now.')
        return redirect('login')
    else:
        return render(request,'base_page.html',{"title":'Expired link',"content":"The confirmation link is not valid."})


def account_activation_sent(request):
    return render(request,'base_page.html',{"title":'Confirmation email sent',"content":'A email with confirmation link has been sent.'})

def logout(request):
    auth_logout(request)
    return redirect('login')

def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            print('form is valid with email')
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(email=data)
            if associated_users.exists():
                print('user exists')
                current_site = get_current_site(request)
                for user in associated_users:


                    subject = "TrustedUX Password Reset"
                    message = render_to_string('password_reset_email.html', {
                        'user': user,
                        'domain': current_site.domain,
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http'
                        })
                    try:
                        data = {
                          'Messages': [
                            {
                              "From": {
                                "Email": "pankajch@tlu.ee",
                                "Name": "TrustedUX Team "
                              },
                              "To": [
                                {
                                  "Email": user.email,
                                }
                              ],
                              "Subject": "TrustedUX Password Reset",
                              "TextPart": message,
                            }
                          ]
                        }
                        result = mailjet.send.create(data=data)
                    except:
                        return HttpResponse('Error')
                    return redirect ("/password_reset/done")
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="password_reset.html", context={"password_reset_form":password_reset_form})