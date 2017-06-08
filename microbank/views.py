from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from microbank.models import Client

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
# from microbank.decorators import my_login_required
from microbank.forms import SignUpForm,ApplyForLoanForm

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            last_name = request.POST.get('last_name','')
            first_name = request.POST.get('first_name','')
            email = request.POST.get('email','')
            raw_password = form.cleaned_data.get('password1')
            username = form.cleaned_data.get('username')
            user = User.objects.create_user(username=username,email=email,password=raw_password,first_name=first_name,last_name=last_name)
            user.save()
            # args={}
            # data = {"username":username,"first_name":first_name,"last_name":last_name,"email":email}
            # args["data"] = data;
            user = authenticate(username=username, password=raw_password,email=email)
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def loginredirect(request):
    return redirect('login')

@login_required
def home(request):
    # user_id  = request.user.id
    # args={}
    # data = {"username":username,"first_name":first_name,"last_name":last_name,"email":email}
    # args[data] = data;
    client =  Client.objects.filter(user_id=request.user.id)
    args = {}
    args["loanTaken"] = 0
    if client is not None:
        args["loanTaken"] = 1 #client[0].loanTaken
    else:
        args["loanTaken"] = 0
    print(args["loanTaken"])
    return render(request,'home.html',{
        "loanTaken" : args["loanTaken"],
    })

@login_required
def applyforloan(request):
    if request.method == 'GET':
        id = request.user.id
        user = Client.objects.filter(user_id=id)
        if not user:
            form = ApplyForLoanForm()
            return render(request, 'applyforloan.html', {'form': form})
        else:
            args = {}
            args["error"] = "Already applied"
            return redirect('home')
    elif request.method == 'POST':
        print("post here")
        id = request.user.id
        form = ApplyForLoanForm(request.POST)
        if form.is_valid():
            address = request.POST.get('address','')
            mobile = request.POST.get('mobile','')
            singleOrGroup = request.POST.get('singleOrGroup','')
            client = Client.objects.create(user_id=int(id),address=address,mobile=mobile,loanTaken=0,singleOrGroup=int(singleOrGroup))
            client.save()
            return redirect('home')















# ad
