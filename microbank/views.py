from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from microbank.models import Client,Loan,ClientGroup
from django.core.urlresolvers import reverse

from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
# from microbank.decorators import my_login_required
from microbank.forms import SignUpForm,ApplyForLoanForm

def index(request):
    return render(request,"index.html")

def signup(request):
    id = 0
    id = request.user.id
    if id is not None:
        return redirect('/home/?msg=%s' % "Already logged in !" )

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
    client =  Client.objects.filter(user_id=request.user.id)
    args = {}
    args["loanApplied"] = 0
    args["loanTaken"] = 0
    args["loanAmount"] = 0
    args["loanInterest"] = 0
    args["deposit"]     = 0
    args["emi"]         = 0
    args["loanPayed"]   = 0
    args["duration"]    = 1
    args["msg"] = request.GET.get('msg', '')
    args["address"] = ""
    args["mobile"]      = 0
    # print(client)
    if client is not None:
        if len(client) > 0:
            args["loanApplied"] = 1
            args["deposit"]     = client[0].deposit
            args["address"]     = client[0].address
            args["mobile"]      = client[0].mobile

            if client[0].groupId_id is not None:
                group = ClientGroup.objects.filter(g_id=client[0].groupId_id)
            groupId = 0;
            if 'group' in locals():
                if len(group) > 0:
                    groupId = group[0].id
                else:
                    groupId = 0;
            if groupId != 0:
                loan = Loan.objects.filter(groupId_id=groupId)
            else:
                loan = Loan.objects.filter(clientId_id=client[0].id)
            if loan is not None:
                if len(loan) > 0:
                    args["loanTaken"] = 1
                    args["loanAmount"] = loan[0].amount
                    args["loanInterest"] = loan[0].interestRate
                    args["loanPayed"] = loan[0].loanPayed
                    args["duration"] = loan[0].duration

    else:
        args["loanApplied"] = 0

    args["emi"] = args["loanAmount"]*args["loanInterest"]
    args["emi"] /=100
    args["emi"] += args["loanAmount"]
    args["emi"] /= args["duration"]

    return render(request,'home.html',{
        "loanApplied" : args["loanApplied"],
        "loanTaken"   : args["loanTaken"],
        "loanAmount"  : args["loanAmount"],
        "loanInterest": args["loanInterest"],
        "deposit"     : args["deposit"],
        "emi"         : round(args["emi"]),
        "loanPayed"   : args["loanPayed"],
        "duration"    : args["duration"],
        "msg"         : args["msg"],
        "address"     : args["address"],
        "mobile"      : args["mobile"]
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
            client = Client.objects.create(user_id=int(id),address=address,mobile=mobile,singleOrGroup=int(singleOrGroup),deposit=0)
            client.save()
            return redirect('/home/?msg=%s' % "Loan Applied, Go to Bank to get it granted !" )

@login_required
def payemi(request):
    if request.method == 'GET':
        args={}
        id = request.user.id
        client = Client.objects.filter(user_id=id)
        if client is not None:
            if len(client) > 0:
                if client[0].groupId_id is not None:
                    group = ClientGroup.objects.filter(g_id=client[0].groupId_id)
                groupId = 0;
                if 'group' in locals():
                    if len(group) > 0:
                        groupId = group[0].id
                    else:
                        groupId = 0;
                if groupId != 0:
                    loan = Loan.objects.filter(groupId_id=groupId)
                else:
                    loan = Loan.objects.filter(clientId_id=client[0].id)
                if loan is not None:
                    if len(loan) > 0:
                        args["loanAmount"] = loan[0].amount
                        args["loanPayed"] = loan[0].loanPayed
                        args["duration"] = loan[0].duration
                        args["loanInterest"] = loan[0].interestRate
                        args["emi"] = args["loanAmount"]*args["loanInterest"]
                        args["emi"] /=100
                        args["emi"] += args["loanAmount"]
                        args["emi"] /= args["duration"]
                        loan.update(loanPayed=args["loanPayed"]+args["emi"])
            return redirect('/home/?msg=%s' % "EMI Paid, Congrats !" )
        else:
            return redirect('/home/?msg=%s' % "EMI couldnt be paid, retry !" )
    else:
        return redirect('/home/?msg=%s' % "EMI couldnt be paid, retry !" )










# ad
