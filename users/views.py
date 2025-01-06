from django.shortcuts import render, redirect 
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm 
from django.contrib.auth import login, logout
from .forms import CustomUserCreationForm



# Create your views here.

# register new user along with the help test for username, password1 and password2
# def register_view(request):
#     if request.method == "POST": 
#         form = UserCreationForm(request.POST) 
#         if form.is_valid(): 
#             login(request, form.save())
#             return redirect("home")
#     else:
#         form = UserCreationForm()
#     return render(request, "users/register.html", { "form": form })

# register new user along with out the help test for username, password1 and password2
def register_view(request):
    if request.method == "POST": 
        form = CustomUserCreationForm(request.POST) 
        if form.is_valid(): 
            user = form.save()
            # login(request, user)  # this will allow auto login as newly created user
            return redirect("home")
    else:
        form = CustomUserCreationForm()
    return render(request, "users/register.html", { "form": form,  'disable_menu' : True})




def login_view(request): 
    if request.method == "POST": 
        form = AuthenticationForm(data=request.POST)
        if form.is_valid(): 
            user = form.get_user()
            login(request, user)
            # return redirect("home")

            # Get the user's group names
            group_names = [group.name for group in user.groups.all()] 
            # for grp in group_names:
            #     print(grp)
            # Store the group names in the session
            request.session['user_groups'] = group_names

            if 'next' in request.POST:
                return redirect(request.POST.get('next'))
            else:
                return redirect("home")
    else: 
        form = AuthenticationForm()
    return render(request, "users/login.html", { "form": form })

def logout_view(request):
    if request.method == "POST": 
        logout(request) 
        return redirect("home")
    

def helppage_view(request):
    return render(request, 'users/help.html')
    # return redirect("help")
