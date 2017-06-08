from django.shortcuts import render ,redirect
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated , AllowAny, IsAdminUser

from api.models import Cities, Locations,  Vendors, VendorsLocations, Fos, Bikes, Make, VendorsLocationsBikes, \
VendorsLocationsAccessories, VendorsLocationsBikesDetails, VendorsLocationsBikesService, VendorsLocationsBikesSold,\
Users, UsersOtp, FacebookConnect, GoogleConnect, Bookings , BookingsDetails, Availability,Bikes,Make , Customer

from api.serializers import CitiesSerializers, LocationsSerializers, VendorsSerializers, FosSerializers, VendorsLocationsSerializers, \
BikesSerializers, MakeSerializers, VendorsLocationsBikesSerializers, VendorsLocationsAccessoriesSerializers, \
VendorsLocationsBikesDetailsSerializers, VendorsLocationsBikesServiceSerializers, VendorsLocationsBikesSoldSerializers,BikesSerializers,MakeSerializers, \
UsersSerializers , CustomerSerializers, BookingsDetailsSerializers ,VendorsLocationsAccessoriesSerializers, PriorCheckoutSerializers, BookingSerializers, RiderDetailsSerializers

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login , logout
from django.utils.decorators import method_decorator
from django.shortcuts import render_to_response ,redirect
from django.template.context import RequestContext
from django.http import JsonResponse
from rest_framework.renderers import TemplateHTMLRenderer
# from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from rest_framework.reverse import reverse
from api.forms import VendorsLocationsBikesForm , VendorsLocationsBikesDetailsForm, VendorsLocationsAccessoriesForm, VendorsLocationsBikesServiceForm, \
VendorsLocationsForm, VendorForm , CustomerForm, VendorsLocationsBikesSoldForm , BookingForm , MakeBookingForm
from rest_framework.authentication import SessionAuthentication ,BasicAuthentication

from rest_framework.authtoken.models import Token

from oauth2_provider.views.generic import ProtectedResourceView
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from django.db.models import F, FloatField, Sum
from math import acos,sin,pi,cos 
import datetime
from django.utils import timezone
from django.db.models import Q
import re
from oauth2_provider.views.generic import ProtectedResourceView
from django.http import HttpResponse
from base64 import b64encode
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json
from oauth2_provider import models
# for caching database 
from django.core.cache import cache

from rest_framework.decorators import api_view, permission_classes

def checkavaliablity(request):
    data_type = request.POST.get("type")
    data      = request.POST.get("data")
    print(data_type+":"+data)
    if data_type == 'mobile':
        customer = Customer.objects.filter(mobile_number=data).exists()
        if customer:
            print("mobile unavaliable")
            return JsonResponse({"avaliable":"false"})
        else:
            print("mobile avaliable")
            return JsonResponse({"avaliable":"true"})
    if data_type == 'username':
        vendor = Vendors.objects.filter(username=data).exists()
        if vendor:
            print("username unavaliable")
            return JsonResponse({"avaliable":"false"})
        else:
            print("username avaliable")
            return JsonResponse({"avaliable":"true"})


def checkadmin(user):
    print(user)
    print("is admin"+str(user.is_admin))
    if user.is_admin or user.is_admin:
        return True
    return False
def checkvendor(user):
    if (user.is_authenticated() and user.is_active and (user.customer_role =='vendor')) or user.is_superuser:
        return True
    return False
def checkfos(user):
    if (user.is_authenticated() and user.is_active and user.customer_role=='fos') or user.is_superuser:
        return True
    return False

def checkmobile(mobile):
    mobile_pattern = re.compile(r'^\d{10}$')
    if not mobile.isnumeric():
        return "mobile number should be digits only."
    if not mobile_pattern.match(mobile):
        return "mobile should be 10 digits only."
    return "OK"


# from django.http import HttpResponse

class DisableCSRF(object):
    def process_request(self, request):
            setattr(request, '_dont_enforce_csrf_checks', True)

class LogoutMiddleware(object):
    def process_request(self,request):
        if(request.META.get('PATH_INFO') =='/api/logout'):
            #Revoke token to be inserted
            if request.META.get('HTTP_AUTHORIZATION'):
                access_token = request.META.get('HTTP_AUTHORIZATION')[len('Bearer '):]
                try:
                    token        = models.AccessToken.objects.get(token = access_token)
                except:
                    token=None
                if token:
                    application_id = token.application.id
                    client_id      = models.Application.objects.get(id = application_id).client_id
                    print("client_id : "+str(client_id))
                    client_secret  = models.Application.objects.get(id = application_id).client_secret
                    print("client_secret : "+str(client_secret))
                    self.revoke(client_id,client_secret,"revoke_token",access_token)

    def revoke(self,client_id,client_secret,grant_type,access_token):
        if(grant_type=='revoke_token'):
            data          = urlencode(dict(token=access_token,grant_type=grant_type,client_id=client_id,client_secret=client_secret)).encode('ascii')
            
        else:
            return Response({"success":False,"message":"grant_type not permitted"},status=status.HTTP_400_BAD_REQUEST)

        url           ='http://127.0.0.1:8000/o/revoke_token/'
        headers       = {'Authorization':b"Basic "+b64encode((client_id+':'+client_secret).encode('utf-8'))}

        try:
            response      = urlopen(Request(url,data,headers))
        except Exception as e:
            print(e.read())


class ApiEndpoint(ProtectedResourceView):
    def get(self, request, *args, **kwargs):
        print(request.user)
        return HttpResponse('Hello, OAuth2!')


def secret_page(request, *args, **kwargs):
    return render_to_response('geolocation.html',{})

def home(request):
   context = RequestContext(request,{'request': request, 'user': request.user})
   return render_to_response('home.html',context_instance=context)


class Authentication(APIView):
    permission_classes = (AllowAny,)
    def post(self,request):
        mobile_number = request.data.get('mobile_number')
        if checkmobile(mobile_number) !='OK':
            return Response({"status":False,"message":checkmobile(mobile_number)},status=status.HTTP_400_BAD_REQUEST)
        password      = request.data.get('password')
        client_id     = request.data.get('client_id')
        client_secret = request.data.get('client_secret')
        grant_type    = request.data.get('grant_type')
        refresh_token = request.data.get('refresh_token',None)

        if(grant_type=='password'):
            data          = urlencode(dict(username=mobile_number,password=password,grant_type=grant_type)).encode('ascii')
        elif grant_type=='refresh_token':
            data          = urlencode(dict(refresh_token=refresh_token,grant_type=grant_type)).encode('ascii')
        else :
            return Response({"success":False,"message":"invalid grant_type or client"},status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user credentials are correct or not 
        user = authenticate(mobile_number = mobile_number, password = password )
        print(user)
        if user is None:
            return Response({"success":False,"message":"user credentials not correct"},status=status.HTTP_401_UNAUTHORIZED)
        url           ='http://imbs-wheelstreet.herokuapp.com/o/token/'
        headers       = {'Authorization':b"Basic "+b64encode((client_id+':'+client_secret).encode('utf-8'))}
        try:
            response      = urlopen(Request(url,data,headers))
        except Exception as e:
            ResponseData = json.loads(e.read().decode("utf8", 'ignore'))
            return Response({"success":False,"message":"invalid grant_tupe or client"},status=status.HTTP_400_BAD_REQUEST)
        data          = json.loads(response.read().decode())
        return Response({"success":True,"access_token":data['access_token'],"refresh_token":data['refresh_token'],"token_type":data['token_type']})


class Login(APIView):
    permission_classes = (AllowAny,)
    def post(self,request,format=None):
        mobile   = request.data.get('mobile_number')   
        password = request.data.get('password')
        # print(mobile +" " + password)
        if mobile:
            if checkmobile(mobile) !='OK':
                return Response({"status":False,"message":checkmobile(mobile)},status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(mobile_number =mobile, password=password)
        print("user is "+str(request.user))
        if user is not None:
            if user.is_active:
                login(request, user)
                #token = Token.objects.get_or_create(user = user.id)

                if request.accepted_renderer.format != 'json':
                    return redirect(reverse('vendorslocations-list', kwargs={}))
                else:
                    return Response({"status":True,"message":"Login successful","user":{"id":user.id,"customer_role":user.customer_role}})

            else:
                if request.accepted_renderer.format != 'json':
                    return Response({"status":False,"message":"Account Suspended. Contact for reactivation." },template_name = 'home.html') 
                else:
                    return Response({"status":False,"message":"Account Suspended. Contact for reactivation." },status=status.HTTP_400_BAD_REQUEST)
        else:
            if request.accepted_renderer.format != 'json':
                return Response({"status":False,"message":"Login credentials not matched."},template_name = 'home.html')
            else:
                return Response({"status":False,"message":"Login credentials not matched."},status=status.HTTP_400_BAD_REQUEST)


class Logout(APIView):
    permission_classes=(AllowAny,)
    def post(self,request,format=None):
        print(request.user)
        if not request.user.is_authenticated():
            return Response({"success":False,"message":"User not logged in"},status=status.HTTP_400_BAD_REQUEST)
        print(request.META.get('HTTP_AUTHORIZATION',''))
        logout(request)
        if request.accepted_renderer.format !='json':
            return Response({"success":True ,"message":"Successfully logout."},template_name = 'home.html')
        else:
            return Response({"success":True ,"message":"Successfully logout."},status=status.HTTP_200_OK)


class CitiesList(APIView):
    def get(self,request,format=None):
        if not checkvendor(request.user):
            return Response({'success':False,'message':'Permission not granted'},status=status.HTTP_403_FORBIDDEN)
        cities     = Cities.objects.all()
        serializer = CitiesSerializers(cities,many=True)
        return Response({"success":True,'cities':serializer.data},status=status.HTTP_200_OK)

    def post(self,request,format=None):
        if not checkadmin(request.user):
            return Response({'success':False,'message':'Permission not granted'},status=status.HTTP_403_FORBIDDEN)
        request_data = request.data.copy()
        serializer = CitiesSerializers(data=request_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(added_by=request.user)
            return Response({"success":True,'cities':serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"success":False,"message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class CitiesDetail(APIView):
    
    def get_object(self,pk):
        try:
            return Cities.objects.get(pk=pk)
        except Cities.DoesNotExist:
            return None
           
    def get(self,request,pk,format=None):
        city=self.get_object(pk)
        if city:
            serializer = CitiesSerializers(city)
            return Response({'cities':serializer.data,"success":True},status=status.HTTP_200_OK)
        return Response({"success":False,"message":"cities not found."},status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk, format=None):
        if not checkadmin(request.user):
            return Response({'success':False,'message':'Permission not granted'},status=status.HTTP_403_FORBIDDEN)
        cities=self.get_object(pk)
        serializer = CitiesSerializers(cities, data=request.data,partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save(modified_by=request.user.id)
            return Response({"success":True,"message":serializer.data},status=status.HTTP_200_OK)
        return Response({"success":False,"message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    permission_classes = (IsAdminUser,)
    def delete(self, request, pk, format=None):
     	cities=self.get_object(pk)
     	cities.delete()
     	return Response(status=status.HTTP_204_NO_CONTENT)


class LocationsList(APIView):

    def get(self,request,format=None):
        if not checkvendor(request.user):
            return Response({'success':False,'message':'Permission not granted'},status=status.HTTP_403_FORBIDDEN)
        locations     = Locations.objects.all()
        serializer = LocationsSerializers(locations,many=True)
        return Response({"success":True,'locations':serializer.data},status=status.HTTP_200_OK)

    def post(self,request,format=None):
        if not checkadmin(request.user):
            return Response({'success':False,'message':'Permission not granted'},status=status.HTTP_403_FORBIDDEN)
        request_data = request.data.copy()
        serializer = LocationsSerializers(data=request_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(added_by=request.user.id)
            return Response({"success":True,"message":"location created successfully","location":serializer.data},status=status.HTTP_201_CREATED)
        return Response({"success":False,"message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class LocationsDetail(APIView):
    
    def get_object(self,pk):
        try:
            return Locations.objects.get(pk=pk)
        except Locations.DoesNotExist:
            return None

    def get(self,request,pk,format=None):
        location=self.get_object(pk)
        if location:
            serializer = LocationsSerializers(location)
            return Response({'locations':serializer.data,"success":True},status=status.HTTP_200_OK)
        return Response({"success":False,"message":"locations not found."},status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, format=None):
        if not checkadmin(request.user):
            return Response({'success':False,'message':'Permission not granted'},status=status.HTTP_403_FORBIDDEN)
        request.data['modified_by'] = request.user.id
        locations=self.get_object(pk)
        serializer = LocationsSerializers(locations, data=request.data,partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save(modified_by=request.user)
            return Response({"success":True,"message":"location updated successfully","location":serializer.data},status=status.HTTP_200_OK)
        return Response({"success":False,"message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        if not checkadmin(request.user):
            return Response({'success':False,'message':'Permission not granted'},status=status.HTTP_403_FORBIDDEN)
        locations=self.get_object(pk)
        locations.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class VendorRegister(APIView):
    permission_classes = (AllowAny,)
    def get(self,request,format=None):
        customer_form = CustomerForm()
        vendor_form   = VendorForm()
        return Response({"customer_form":customer_form,"vendor_form":vendor_form},template_name="vregister.html")

# def ForgotPassword(request,format=None):
#     if(request.method=='POST'):
#         mobile = request.data.get('mobile_number')
#         user = Customer.objects.get(mobile_number=mobile)
#         if user is not None:



class VendorsList(APIView):
    def get(self,request,format=None):
        if not checkadmin(request.user):
            if request.accepted_renderer.format != 'json':
                return redirect(reverse('addvendor', kwargs={}))
            return Response({'success':False,'message':'Permission not granted'},status = status.HTTP_403_FORBIDDEN)
        vendors     = Vendors.objects.all()
        serializer = VendorsSerializers(vendors,many=True)
        return Response({"success":True,'vendors':serializer.data},status=status.HTTP_200_OK)
        

    permission_classes = (AllowAny,)
    def post(self,request,format=None):
        request_data = request.data.copy()
        request_data['customer_role']='vendor'
        serializer = CustomerSerializers(data=request_data)
        # LANGUAGES = ()ine to bypass customer feild validation using fake key otherwise VendorsSerializer will definately throw error
        # I used the fake_key value such that it is not present in the Users database but present in Customer database
        fake_customer_id ="1"
        request_data['customer_id'] = fake_customer_id
        venserializer = VendorsSerializers(data=request_data)
        print("is problem here 1")
        if not serializer.is_valid(raise_exception=True):
            print("Customer error")
            if request.accepted_renderer.format != 'json':
                return JsonResponse({"success":False,"message": serializer.errors})
                return redirect(reverse('addvendor', kwargs={}))
            else:  
                return Response({"success":False,"message": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        print("is problem here 2")
        if not venserializer.is_valid(raise_exception=True):
            print("Vendors error")
            if request.accepted_renderer.format != 'json':
                return JsonResponse({"success":False,"message": venserializer.errors})
                return redirect(reverse('addvendor', kwargs={}))
            else:
                return Response({"success":False,"message":venserializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        serializer.validated_data.pop('confirm_password')
        serializer.save()
        # overriding previous fake coustomer id field
        request_data['customer_id'] = serializer.data['id']
        print("is problem here 3")
        venserializer = VendorsSerializers(data=request_data)
        if venserializer.is_valid():
            venserializer.save()
            if request.accepted_renderer.format != 'json':
                return redirect(reverse('home', kwargs={}))
            else:
                return Response({'vendor':venserializer.data,"success":True,"message":"Vendor created successfully."},status=status.HTTP_201_CREATED)
        if request.accepted_renderer.format != 'json':
            return JsonResponse({"success":False,"message": serializer.errors})
            return redirect(reverse('addvendor', kwargs={}))            
        
        return Response({"success":False,"message": serializer.errors},status=status.HTTP_400_BAD_REQUEST)


class VendorsDetail(APIView):
    
    def get_object(self,pk):
        try:
            return Vendors.objects.get(pk=pk)
        except Vendors.DoesNotExist:
            return None

    def get(self,request,pk,format=None):
        vendor=self.get_object(pk)
        if vendor:
            serializer = VendorsSerializers(vendor)
            return Response({'vendors':serializer.data,"success":True},status=status.HTTP_200_OK)
        return Response({"success":False,"message":"vendor not found."},status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, format=None):
        if not checkvendor(request.user):
            return Response({'success':False,'message':'Permission not granted'},status=status.HTTP_403_FORBIDDEN)
        vendors=self.get_object(pk)
        serializer = VendorsSerializers(vendors, data=request.data,partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"success":True,"vendor":serializer.data},status=status.HTTP_200_OK)
        return Response({"success":False,"message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        if not checkadmin(request.user):
            return Response({'success':False,'message':'Permission not granted'},status=status.HTTP_403_FORBIDDEN)
        vendors=self.get_object(pk)
        vendors.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class AddVendorsLocationsBikesSold(APIView):
    def get(self,request,format=None):
        bikeid = request.GET.get('bikeid')
        form   = VendorsLocationsBikesSoldForm(id=bikeid)
        return Response({'form':form},template_name='vaddbikesold.html')

class AddVendorLocation(APIView):
    def get(self,request,format=None):
        if request.user.customer_role == "vendor":
            vendor_id  = Vendors.objects.get(customer = request.user.id)
        location_id = request.GET.get('location',None)
        if location_id is not None:
            locationobj = VendorsLocations.objects.filter(vendors=vendor_id).get(id = location_id)
            form   = VendorsLocationsForm(id=vendor_id,instance= locationobj)
            return Response({'form':form,"edit":"True"},template_name ='vaddlocation.html')
        else:
            form = VendorsLocationsForm(id=vendor_id , instance=None)
            return Response({'form':form},template_name ='vaddlocation.html')


class AddVendorLocationBikeModel(APIView):
    def get(self,request,pk,format=None):
        bikeid = request.GET.get('bikeid',None)
        if bikeid is not None:
            bikeobj  =VendorsLocationsBikes.objects.get(id=bikeid)
            form     = VendorsLocationsBikesForm(id=pk, instance =bikeobj)
            return Response({"form":form,"ven_loc":pk,"bikeid":bikeid,"edit":"True"},template_name ='vaddbikemodel.html')
        else:
            form     = VendorsLocationsBikesForm(id=pk)
            return Response({"form":form,"ven_loc":pk,"edit":"False"},template_name ='vaddbikemodel.html')


class AddVendorLocationAccessories(APIView):
    def get(self,request,pk,format=None):
        print("location"+str(pk))
        accessorie_id = request.GET.get('accessorieid',None)
        if accessorie_id :
            accessorie = VendorsLocationsAccessories.objects.get(id = accessorie_id)
            print(accessorie.accessories_id)
            print(accessorie)
            form = VendorsLocationsAccessoriesForm(id=pk,instance = accessorie)
            return Response({"form":form,"location":pk,"edit":"True",'accessorieid':accessorie_id},template_name ='vaddbikeaccessories.html')
        else:
            form     = VendorsLocationsAccessoriesForm(id=pk)
            return Response({"form":form,"location":pk},template_name ='vaddbikeaccessories.html')


class AddVendorLocationBikeDetails(APIView):
    def get(self,request,pk,format=None):
        detailid = request.GET.get('detailid',None)
        print(detailid)
        form     = VendorsLocationsBikesDetailsForm(id=pk)
        if detailid is not None:
            detailobj = VendorsLocationsBikesDetails.objects.get(id=detailid)
            form = VendorsLocationsBikesDetailsForm(id=pk, instance=detailobj)
            return Response({"form":form,"ven_loc_bikes":pk,"edit":"True","detailid":detailid},template_name ='vaddbikedetails.html')
        else:
            form = VendorsLocationsBikesDetailsForm(id=pk)
            return Response({"form":form,"ven_loc_bikes":pk},template_name ='vaddbikedetails.html')


class AddVendorLocationBikeService(APIView):
    def get(self,request,pk,format=None):
        form     = VendorsLocationsBikesServiceForm(id=pk)       
        return Response({"form":form,"ven_loc_bikes":pk},template_name ='vaddbikeservice.html')

class VendorsBikes(APIView):
    def get(self,request,format=None):
        if not checkvendor(request.user):
            return Response({'success':False,'message':'Permission not granted'},status=status.HTTP_403_FORBIDDEN)
        vendors_id                = Vendors.objects.get(customer=request.user.id)
        vendorslocations           = VendorsLocations.objects.filter(vendors = vendors_id)
        vendorlocation            = [i.id for i in vendorslocations]
        vendorslocationsbikes     = VendorsLocationsBikes.objects.filter(ven_loc__in = vendorlocation).values('bikes').distinct()
        vendorslocaitonsbikesmodel = VendorsLocationsBikesSerializers(vendorslocationsbikes,many=True)
        bikes = []
        for i in vendorslocationsbikes:
            vendorslocationsbike = VendorsLocationsBikes.objects.filter(ven_loc__in = vendorlocation).filter(bikes = i['bikes']).order_by('-bikes_quantity')
            print(vendorslocationsbike)
            serializer = VendorsLocationsBikesSerializers(vendorslocationsbike,many=True)
            bikes.append({"model":serializer.data[0]['bikes'],"bikes":serializer.data}) 
        return Response({"success":True,'vendors_bikes':bikes},template_name='vbikeslist.html',status=status.HTTP_200_OK)

def getclean(data):
    print("previous keys:",end='')
    print(list(data.keys()))
    print(type(list(data.keys())))
    print("data : ",end= ' ')
    print(data[list(data.keys())[0]])
    cleaned_data = {}
    for key,value in data.items():
        cleaned_data.update({key:value})
        print(str(key)+":"+str(value))
    print(len(data.keys()))
    print("new data is ", end='   ')
    return cleaned_data


class VendorsLocationsList(APIView):
    def get(self,request,format=None):
        if not request.user.is_authenticated():
            return Response({"success":False,"message":"User not logged in"},status=status.HTTP_401_UNAUTHORIZED)    
        if request.user.customer_role == "vendor":
            vendor_id            = Vendors.objects.get(customer = request.user.id)
            vendorslocations     = VendorsLocations.objects.filter(vendors = vendor_id)
        else:
            vendorslocations     = VendorsLocations.objects.all()
        serializer = VendorsLocationsSerializers(vendorslocations,many=True)
        print(request.user)
        print(serializer.data)
        if request.accepted_renderer.format != 'json':
            return Response({'vendors_locations':serializer.data},template_name ='vhome.html')
        return Response({"success":True,'vendors_locations':serializer.data},status=status.HTTP_200_OK)

    def post(self,request,format=None):
        if not checkvendor(request.user):
            return Response({'success':False,'message':'Permission not granted'},status=status.HTTP_403_FORBIDDEN)
        # location_data = getclean(request.data.copy())
        location_data = request.data.copy()
        # print(location_data)
        customer_id = request.user.id
        location_data['vendor_id']=Vendors.objects.get(customer= customer_id).id
        if 'edit' in location_data.keys():
            vendor_location = VendorsLocations.objects.get(id=location_data.get('location_id'))
            serializer = VendorsLocationsSerializers( data= location_data ,instance=vendor_location)
        else:
            serializer = VendorsLocationsSerializers( data= location_data )

        if serializer.is_valid(raise_exception=True ):
            serializer.save(added_by=request.user,status='inactive')
            print(serializer.validated_data)
            if request.accepted_renderer.format != 'json':
                return redirect(reverse('vendorslocations-list', kwargs={}))
            else:
                return Response(serializer.data ,status=status.HTTP_201_CREATED)
        print(serializer.validated_data)
        return Response({"success":False,"message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class VendorsLocationsDetail(APIView):
    # @login_required
    def get_object(self,request,pk):
        try:
            if (request.user.customer_role=="vendor"):
                vendor_id  = Vendors.objects.get(customer = request.user.id )
                return VendorsLocations.objects.filter(vendors = vendor_id).get(pk=pk)
            else:
                return VendorsLocations.objects.get(pk=pk)    
        except VendorsLocations.DoesNotExist:
            return None

    def get(self,request,pk,format=None):
        if not checkvendor(request.user):
            return Response({'success':False,'message':'Permission not granted'},status=status.HTTP_403_FORBIDDEN)
        vendorslocationaccessories = VendorsLocationsAccessories.objects.filter(location=pk)
        print(str(vendorslocationaccessories))
        aserializer = VendorsLocationsAccessoriesSerializers(vendorslocationaccessories,many=True)
        vendors_location   =   self.get_object(request,pk)
        if not vendors_location:
            return Response({'success':False,"message":"Location not found"},status=status.HTTP_400_BAD_REQUEST)
        ven_loc_serializer =   VendorsLocationsSerializers( vendors_location)
        bikes_at_location = VendorsLocationsBikes.objects.filter(ven_loc = vendors_location.id)
        bike_serializer   = VendorsLocationsBikesSerializers(bikes_at_location,many=True)
        if request.accepted_renderer.format != 'json':
            return Response({"success":True,'location':ven_loc_serializer.data,"bikes":bike_serializer.data ,"accessories":aserializer.data },template_name ='vlocation.html')
        return Response({'success':True,'location':ven_loc_serializer.data,"bikes":bike_serializer.data,"accessories":aserializer.data },status=status.HTTP_200_OK)

        # return Response({'vendors':serializer.data,"success":True},status=status.HTTP_200_OK)
        # return Response({"success":False,"message":"vendors not found."},status=status.HTTP_400_BAD_REQUEST)

        
    def post(self, request, pk, format=None):
        if not checkvendor(request.user):
            return Response({'success':False,'message':'Permission not granted'},status=status.HTTP_403_FORBIDDEN)
        request_data   = request.data.copy()
        vendorslocations=self.get_object(request,pk)
        request_data['vendors'] = vendorslocations.vendors.id
        serializer = VendorsLocationsSerializers(vendorslocations, data=request_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(modified_by=request.user)
            if request.accepted_renderer.format != 'json':
                return redirect(reverse('vendorslocations-list', kwargs={}))
            else:
                return Response(serializer.data ,status=status.HTTP_201_CREATED)
        return Response({"message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        if not checkadmin(request.user):
            return Response({'success':False,'message':'Permission not granted'},status=status.HTTP_403_FORBIDDEN)
        vendorslocations=self.get_object(request,pk)
        serializer = VendorsLocationsSerializers(vendorslocations, data={"status":'inactive'})
        if serializer.is_valid(raise_exception=True):
            serializer.save(modified_by=request.user)
            print(serializer.data)
            if request.accepted_renderer.format != 'json':
                return redirect(reverse('vendorslocations-list', kwargs={}))
            else:
                return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class FosList(APIView):
    def get(self,request,format=None):
        if not checkvendor(request.user):
            return Response({'success':False,'message':'Permission not granted'},status=status.stauts.HTTP_403_FORBIDDEN)
        fos      = Fos.objects.all()
        serializer = FosSerializers(fos,many=True)
        return Response({"success":True,"fos":serializer.data},status=status.HTTP_200_OK)
    
    def post(self,request,format=None):
        if not checkadmin(request.user):
            return Response({'success':False,'message':'Permission not granted'},status=status.HTTP_403_FORBIDDEN)
        request_data = request.data.copy()
        request_data['customer_role']='fos'
        serializer = CustomerSerializers(data=request_data)
        # Line to bypass customer feild validation using fake key otherwise VendorsSerializer will definately throw error
        # I used the fake_key value such that it is not present in the Users database but present in Customer database
        fake_customer_id ="1"
        request_data['customer_id'] = fake_customer_id
        fosserializer = FosSerializers(data=request_data)
        if not serializer.is_valid(raise_exception=True):
            print("Customer error")     
            return Response({"success":False,"message": serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        if not fosserializer.is_valid(raise_exception=True):
            print("Fos error")
            return Response({"success":False,"message":fosserializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        serializer.validated_data.pop('confirm_password')
        serializer.save()
        # overriding previous fake coustomer id field
        request_data['customer_id'] = serializer.data['id']
        print(request_data)
        fosserializer = FosSerializers(data=request_data)
        if fosserializer.is_valid(raise_exception=True):
            fosserializer.save()
            if request.accepted_renderer.format != 'json':
                return redirect(reverse('vendorslocations-list', kwargs={"status":"201"}))
            else:
                return Response({'fos':fosserializer.data,"success":True,"message":"Fos created successfully."},status=status.HTTP_201_CREATED)
        return Response({"success":False,"message": fosserializer.errors},status=status.HTTP_400_BAD_REQUEST)


class FosDetail(APIView):

    def get_object(self,pk):
        try:
            return Fos.objects.get(pk=pk)
        except Fos.DoesNotExist:
            return None

    def get(self,request,pk,format=None):
        fos = self.get_object(pk)
        if not fos:
            return Response({"success":False},status=status.HTTP_404_NOT_FOUND)    
        serializer = FosSerializers(fos)
        return Response({"success":True,"fos":serializer.data},status=status.HTTP_200_OK)

    def put(self, request, pk, format=None):
        fos = self.get_object(pk)
        serializer = FosSerializers(fos, data=request.data,partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"success":True,"message":"fos updated successfully","fos":serializer.data},status = status.HTTP_200_OK)
        return Response({"success":True,"message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        if not checkadmin(request.user):
            return Response({'success':False,'message':'Permission not granted'},status=status.HTTP_403_FORBIDDEN)
        fos = self.get_object(pk)
        fos.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class BikesList(APIView):
    permission_classes = (AllowAny,)
    def get(self,request,format=None):
        bikes     = Bikes.objects.all()
        serializer = BikesSerializers(bikes,many=True)
        return Response({"success":True,"bikes":serializer.data},status=status.HTTP_200_OK)

    def post(self,request,format=None):
        if not checkadmin(request.user):
            return Response({'success':False,'message':'Permission not granted'},status=status.HTTP_403_FORBIDDEN)
        serializer = BikesSerializers(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(added_by=request.user)
            return Response({"success":True,"bikes":serializer.data,"message":"bikes created successfully"}, status=status.HTTP_201_CREATED)
        return Response({"success":False,"message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class BikesDetail(APIView):
    
    def get_object(self,pk):
        try:
            return Bikes.objects.get(pk=pk)
        except Bikes.DoesNotExist:
            raise Http404

    def get(self,request,pk,format=None):
        bikes=self.get_object(pk)
        serializer = BikesSerializers(bikes)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        if not checkadmin(request.user):
            return Response({'success':False,'message':'Permission not granted'},status=status.HTTP_403_FORBIDDEN)
        bikes=self.get_object(pk)
        serializer = BikesSerializers(bikes, data=request.data,partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save(modified_by=request.user)
            return Response(serializer.data)
        return Response({"message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        if not checkadmin(request.user):
            return Response({'success':False,'message':'Permission not granted'},status=status.HTTP_403_FORBIDDEN)
        bikes=self.get_object(pk)
        bikes.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MakeList(APIView):

    def get(self,request,format=None):
        make     = Make.objects.all()
        serializer = MakeSerializers(make,many=True)
        return Response(serializer.data)

    def post(self,request,format=None):
        if not checkadmin(request.user):
            return Response({'success':False,'message':'Permission not granted'},status=status.HTTP_403_FORBIDDEN)
        serializer = MakeSerializers(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class MakeDetail(APIView):
    
    def get_object(self,pk):
        try:
            return Make.objects.get(pk=pk)
        except Make.DoesNotExist:
            raise Http404

    def get(self,request,pk,format=None):
        make=self.get_object(pk)
        serializer = MakeSerializers(make)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        if not checkadmin(request.user):
            return Response({'success':False,'message':'Permission not granted'},status=status.HTTP_403_FORBIDDEN)
        make=self.get_object(pk)
        serializer = MakeSerializers(make, data=request.data,partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response({"message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        if not checkadmin(request.user):
            return Response({'success':False,'message':'Permission not granted'},status=status.HTTP_403_FORBIDDEN)
        make=self.get_object(pk)
        make.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class VendorsLocationsBikesList(APIView):

    def get(self,request,format=None):
        location_id = request.data.get('location',None) # location will be given in json request
        if location_id is not None:
            vendorslocationsbikes     = VendorsLocationsBikes.objects.filter(ven_loc = location_id)
        else:
            vendors_id                = Vendors.objects.get(customer=request.user.id)
            vendorslocations           = VendorsLocations.objects.filter(vendors = vendors_id)
            vendorlocation            = [i.id for i in vendorslocations]
            vendorslocationsbikes     = VendorsLocationsBikes.objects.filter(ven_loc__in = vendorlocation)
        serializer = VendorsLocationsBikesSerializers(vendorslocationsbikes,many=True)
        print(serializer.data)
        return Response({"success":True,'vendors_locations_bikes':serializer.data},status=status.HTTP_200_OK)


    def post(self,request,format=None):
        if not checkvendor(request.user):
            return Response({'success':False,'message':'Permission not granted'},status=status.HTTP_403_FORBIDDEN)
        bike_data = request.data.copy()
        print(bike_data)
        bike_data["modified_by"] = request.user.id
        if bike_data.get('edit')=='True':
            bikeinstance = VendorsLocationsBikes.objects.get(id=bike_data['bikeid'])
            serializer = VendorsLocationsBikesSerializers(bikeinstance,data=bike_data)
        else:
            serializer = VendorsLocationsBikesSerializers(data=bike_data)
        if serializer.is_valid(raise_exception=True):
            print(serializer.validated_data)    
            serializer.save(added_by=request.user)
            print('success')
            if request.accepted_renderer.format != 'json':
                return redirect(reverse('vendorslocations-detail', kwargs={'pk':bike_data['ven_loc'] }))
            else:
                return Response(serializer.data ,status=status.HTTP_201_CREATED)
        return Response({"message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


"""Implement POST Function in bikes Details part post funciton is missing and editing forms are also to be incoprated in the present forms Buttons to be provided to either edit or to change the present location of the vendors"""

# After sold form redirect and sold button disable also can chage the color scheme seen redirection errors handling
class VendorsLocationsBikesDetail(APIView):
    
    # @login_required
    def get_object(self,request,pk):
        vendorslocationbikes =  VendorsLocationsBikesDetails.objects.filter(ven_loc_bikes = pk).order_by('status')
        if vendorslocationbikes:
            return vendorslocationbikes
        return None

    # @login_required

    def get(self,request,pk,format=None):   
        if not checkvendor(request.user):
            return Response({'success':False,'message':'Permission not granted'},status=status.HTTP_403_FORBIDDEN)
        vendorslocationsbikes=self.get_object(request,pk)
        print(vendorslocationsbikes)
        serializer = VendorsLocationsBikesDetailsSerializers(vendorslocationsbikes , many=True )
        print(serializer.data)
        if request.accepted_renderer.format != 'json':
            return Response({"success":True,"bikes":serializer.data, "ven_loc_bikes":pk },template_name='vbikes.html')
        else:
            return Response({"success":True,"vendors_locations_bikes":serializer.data, "ven_loc_bikes":pk },status=status.HTTP_200_OK)
        

    def put(self, request, pk, format=None):
        if not checkvendor(request.user):
            return Response({'success':False,'message':'Permission not granted'},status=status.HTTP_403_FORBIDDEN)
        request.data['modified_by'] = request.user.id 
        vendorslocationsbikes=self.get_object(request,pk)
        serializer = VendorsLocationsBikesSerializers(vendorslocationsbikes, data=request.data,partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save(modified_by=request.user)
            return Response(serializer.data)
        return Response({"message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        if not checkvendor(request.user):
            return Response({'success':False,'message':'Permission not granted'},status=status.HTTP_403_FORBIDDEN)
        vendorslocationsbikes=self.get_object(request,pk)   
        if vendorslocationsbikes:
            vendorslocationsbikes.status ='inactive'
            venlocbikes = vendorslocationsbikes.ven_loc_bikes
            venlocbikes.bikes_quantity -= 1
            venlocbikes.save()
            vendorslocationsbikes.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    # def delete(self, request, pk, format=None):
    #     vendorslocationsbikes=self.get_object(request,pk)
    #     venlocbikes = Vendorslocationsbikes.ven_loc_bike
    #     vendorslocationsbikes.delete()
    #     ven_loc_bike  = VendorsLocationsBikes.objects.get( ven_loc_bikes=venlocbikes )
    #     ven_loc.bikes_quantity -= 1
    #     return Response(status=status.HTTP_204_NO_CONTENT)


class VendorsLocationsAccessoriesList(APIView):
    def get(self,request,format=None):
        if not checkvendor(request.user):
            return Response({'success':False,'message':'Permission not granted'},status=status.HTTP_403_FORBIDDEN)
        vendorslocationsbikesaccessories     = VendorsLocationsBikesAccessories.objects.all()
        serializer = VendorsLocationsAccessoriesSerializers(vendorslocationsbikesaccessories,many=True)
        if request.accepted_renderer.format!='json':
            return Response({"success":True,"accessories":serializer.data},status = status.HTTP_200_OK,template_name='')
        return Response({"success":True,"accessories":serializer.data},status = status.HTTP_200_OK)

    def post(self,request,format=None):
        if not checkvendor(request.user):
            return Response({'success':False,'message':'Permission not granted'},status=status.HTTP_403_FORBIDDEN)
        print("accessories" + str(request.data))
        if request.data.get('edit')=='True':
            print('accessoried id '+str(request.data.get('accessorieid')))
            accessorie = VendorsLocationsAccessories.objects.get(id=request.data.get('accessorieid'))
            serializer = VendorsLocationsAccessoriesSerializers(instance= accessorie,data=request.data)
        else:
            serializer = VendorsLocationsAccessoriesSerializers(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(added_by=request.user)
            return redirect(reverse('vendorslocations-detail', kwargs={'pk':request.data.get('location') }))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class VendorsLocationsAccessoriesDetail(APIView):

    #@login_required
    def get_object(self,request,pk):
        try:
            #customer_id = request.user.id
            #vendors_id  =  Vendors.objects.get(customer= customer_id)
            return VendorsLocationsBikesAccessories.objects.filter(ven_loc = pk)
        except VendorsLocationsBikesAccessories.DoesNotExist:
            return None

    def get(self,request,pk,format=None):
        vendorslocationsbikesaccessories=self.get_object(request,pk)
        if not vendorslocationsbikesaccessories:
            return Response({"success":False,"message":"accessories not found."},status=status.HTTP_400_BAD_REQUEST)
        serializer = VendorsLocationsAccessoriesSerializers(vendorslocationsbikesaccessories,many=True)
        if request.accepted_renderer.format!='json':
            return Response({"success":True,"accessories":serializer.data},template_name='')
        else:
            return Response({"success":True,"accessories":serializer.data},status=status.HTTP_200_OK)

    
    def put(self, request, pk, format=None):
        request.data['modified_by'] = request.user.id
        vendorslocationsbikesaccessories=self.get_object(pk)
        serializer = VendorsLocationsAccessoriesSerializers(vendorslocationsbikesaccessories, data=request.data,partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save(modified_by=request.user)
            return Response(serializer.data)
        return Response({"message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        if not checkvendor(request.user):
            return Response({'success':False,'message':'Permission not granted'},status=status.HTTP_403_FORBIDDEN)
        vendorslocationsbikesaccessories=self.get_object(pk)
        vendorslocationsbikesaccessories.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class VendorsLocationsBikesDetailsList(APIView):

    def get(self,request,format=None):
        if not checkvendor(request.user):
            return Response({'success':False,'message':'Permission not granted'},status=status.HTTP_403_FORBIDDEN)
        vendor_id = Vendors.objects.get(customer = request.user.id)
        vendors_locations = VendorsLocations.objects.filter(vendors = vendor_id)
        data   =  VendorsLocationsSerializers(vendors_locations,many=True)
        vendors_locations_list = [i.id for i in vendors_locations]
        vendors_locations_bikes = VendorsLocationsBikes.objects.filter(ven_loc__in = vendors_locations_list)
        bikedata = VendorsLocationsBikesSerializers(vendors_locations_bikes, many=True)
        # for i in data:
        #     i.update({"bikemodel":""}) #To be done

        venderslocationsbikes_list = [i.id for i in vendors_locations_bikes]
        venderslocationsbikesdetails    = VendorsLocationsBikesDetails.objects.prefetch_related('ven_loc_bikes__bikes').filter(ven_loc_bikes__in = venderslocationsbikes_list)
        serializer = VendorsLocationsBikesDetailsSerializers(venderslocationsbikesdetails,many=True)
        if request.accepted_renderer.format!='json':
            return Response({"success":True,"bikes_details_list":serializer.data},status = status.HTTP_200_OK ,template_name='')
        return Response({"success":True,"bikes_details_list":serializer.data},status = status.HTTP_200_OK)

    def post(self,request,format=None):
        if not checkvendor(request.user):
            return Response({'success':False,'message':'Permission not granted'},status=status.HTTP_403_FORBIDDEN)
        bike_details_data = request.data.copy()
        if bike_details_data.get('edit') =='True':
            bikeinstance=VendorsLocationsBikesDetails.objects.get(id=bike_details_data['detailid'])
            serializer = VendorsLocationsBikesDetailsSerializers(bikeinstance,data=bike_details_data)
        else:
            serializer = VendorsLocationsBikesDetailsSerializers(data=bike_details_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(added_by=request.user)
            print(bike_details_data)
            if request.accepted_renderer.format != 'json':
                return redirect(reverse('vendorslocationsbikes-detail', kwargs={'pk':bike_details_data['ven_loc_bikes'] }))
            else:
                return Response(serializer.data ,status=status.HTTP_201_CREATED)
        return Response({"message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class VendorsLocationsBikesDetailsDetail(APIView):

    # @login_required    
    def get_object(self,request,pk):
        try:
            #customer_id = request.user.id
            #vendors_id  =  Vendors.objects.get(customer= customer_id)
            return VendorsLocationsBikesDetails.objects.get(id=pk)
        except VendorsLocationsBikesDetails.DoesNotExist:
            return None

   #@login_required
    def get(self,request,pk,format=None):
        vendorslocationsbikesdetails=self.get_object(request,pk)
        if not vendorslocationsbikesdetails:
            return Response({'success':False,"message":"No such bike found"},status=status.HTTP_400_BAD_REQUEST)
        serializer = VendorsLocationsBikesDetailsSerializers(vendorslocationsbikesdetails)
        vendorslocationsbikesservice = VendorsLocationsBikesService.objects.filter(ven_loc_bikes=pk)
        service_serializer = VendorsLocationsBikesServiceSerializers(vendorslocationsbikesservice,many=True)
        print(service_serializer.data)
        if request.accepted_renderer.format !='json':
            return Response({"services":service_serializer.data,"bike":serializer.data},template_name='vbikesdetails.html')
        else:
            return Response({"success":True,"services":service_serializer.data,"bike":serializer.data},status=status.HTTP_200_OK)
        
    
    def put(self, request, pk, format=None):
        vendorslocationsbikesdetails=self.get_object(pk)
        if vendorslocationsbikesdetails:
            serializer = VendorsLocationsBikesDetailsSerializers(vendorslocationsbikesdetails, data=request.data,partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save(modified_by=request.user)
            return Response(serializer.data)
        return Response({"message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        if not checkadmin(request.user):
            return Response({'success':False,'message':'Permission not granted'},status=status.HTTP_403_FORBIDDEN)
        vendorslocationsbikesdetails=self.get_object(pk)
        vendorslocationsbikesdetails.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class VendorsLocationsBikesServiceList(APIView):
    def get(self,request,format=None):
        if not checkvendor(request.user):
            return Response({'success':False,'message':'Permission not granted'},status=status.HTTP_403_FORBIDDEN)
        vendorslocationsbikesservice     = VendorsLocationsBikesService.objects.all()
        serializer = VendorsLocationsBikesServiceSerializers(vendorslocationsbikesservice,many=True)
        if request.accepted_renderer.format!='json':
            return Response({"success":True,"services":serializer.data},status=status.HTTP_200_OK,template_name='')
        return Response({"success":True,"services":serializer.data},status=status.HTTP_200_OK)

    def post(self,request,format=None):
        if not checkvendor(request.user):
            return Response({'success':False,'message':'Permission not granted'},status=status.HTTP_403_FORBIDDEN)
        bike_service_data  = request.data.copy() 
        print(bike_service_data)
        serializer = VendorsLocationsBikesServiceSerializers(data=bike_service_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(added_by=request.user)
            if request.accepted_renderer.format != 'json':
                return redirect(reverse('vendorslocationsbikesdetails-detail', kwargs={'pk':bike_service_data['ven_loc_bikes']}))
            else:
                return Response({"success":True,"service":serializer.data} ,status=status.HTTP_201_CREATED)
        print(serializer.validated_data)
        return Response({"success":False,"message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class VendorsLocationsBikesServiceDetail(APIView):
    
    def get_object(self,request,pk):
        try:
            return VendorsLocationsBikesService.objects.get(ven_loc_bikes = pk)
        except VendorsLocationsBikesService.DoesNotExist:
            return None

    def get(self,request,pk,format=None):
        vendorslocationsbikesservice=self.get_object(request,pk)
        if not vendorslocationsbikesservice:
            return Response({"success":False,"message":"No services for this bike found "},status=status.HTTP_400_BAD_REQUEST)
        serializer = VendorsLocationsBikesServiceSerializers(vendorslocationsbikesservice)
        if request.accepted_renderer.format!='json':
            return Response({"success":True,"services":serializer.data},status=status.HTTP_200_OK,template_name='')
        return Response({"success":True,"services":serializer.data},status=status.HTTP_200_OK)

    def put(self, request, pk, format=None):
        if not checkvendor(request.user):
            return Response({'success':False,'message':'Permission not granted'},status=status.HTTP_403_FORBIDDEN)
        vendorslocationsbikesservice=self.get_object(pk)
        serializer = VendorsLocationsBikesServiceSerializers(vendorslocationsbikesservice, data=request.data,partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save(modified_by=request.user)
            return Response(serializer.data)
        return Response({"message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        if not checkadmin(request.user):
            return Response({'success':False,'message':'Permission not granted'},status=status.HTTP_403_FORBIDDEN)
        vendorslocationsbikesservice=self.get_object(pk)
        vendorslocationsbikesservice.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class VendorsLocationsBikesSoldList(APIView):

    def get(self,request,format=None):
        if not checkvendor(request.user):
            return Response({'success':False,'message':'Permission not granted'},status=status.HTTP_403_FORBIDDEN)
        venlocationbikessoldlist = VendorsLocationsBikesSold.objects.all() 
        serializer = VendorsLocationsBikesSoldSerializers(venlocationbikessoldlist,many=True)
        if request.accepted_renderer.format !='json':
            return Response({"success":True,"data":serializer.data},status=status.HTTP_200_OK,template_name='')
        else:
            return Response({"success":True,"data":serializer.data},status=status.HTTP_200_OK)

    def post(self,request,format=None):
        if not checkvendor(request.user):
            return Response({'success':False,'message':'Permission not granted'},status=status.HTTP_403_FORBIDDEN)
        request_data  = request.data.copy()
        serializer = VendorsLocationsBikesSoldSerializers(data=request.data)
        print(request_data) 
        serializer = VendorsLocationsBikesSoldSerializers(data=request_data) 

        if serializer.is_valid(raise_exception=True):
            serializer.save(added_by=request.user)
            print(serializer.data)
            if request.accepted_renderer.format != 'json':
                bike_model_id = VendorsLocationsBikesDetails.objects.get(id=request.data.get('ven_loc_bikes')).ven_loc_bikes.id
                print("bike_model id"+str(bike_model_id))
                return redirect(reverse('vendorslocationsbikes-detail', kwargs={'pk':bike_model_id }))
            else:
                return Response({"success":True,"sold_detail":serializer.data}, status=status.HTTP_201_CREATED)
            
        return Response({"success":False,"message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class VendorsLocationsBikesSoldDetail(APIView):
    
    def get_object(self,request,pk):
        try:
            return VendorsLocationsBikesSold.objects.filter(ven_loc_bikes = pk)
        except VendorsLocationsBikesSold.DoesNotExist:
            return None

    def get(self,request,pk,format=None):
        if not checkvendor(request.user):
            return Response({'success':False,'message':'Permission not granted'},status=status.HTTP_403_FORBIDDEN)
        vendorslocationsbikessold=self.get_object(request,pk)
        if vendorslocationsbikessold:
            serializer = VendorsLocationsBikesSoldSerializers(vendorslocationsbikessold,many=True)
            return Response({"success":True,"data":serializer.data},status=status.HTTP_200_OK)
        else:
            return Response({"success":False},status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk, format=None):
        if not checkvendor(request.user):
            return Response({'success':False,'message':'Permission not granted'},status=status.HTTP_403_FORBIDDEN)
        vendorslocationsbikessold=self.get_object(request,pk)
        serializer = VendorsLocationsBikesSoldSerializers(vendorslocationsbikessold, data=request.data,partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save(modified_by=request.user)
            return Response(serializer.data)
        return Response({"message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        if not checkadmin(request.user):
            return Response({'success':False,'message':'Permission not granted'},status=status.HTTP_403_FORBIDDEN)
        vendorslocationsbikessold=self.get_object(request,pk)
        vendorslocationsbikessold.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# class CustomersList(APIView):

#     permission_classes = (IsAuthenticated,)
#     def post(self,request,format=None):     
#         request.data['customer_role']='vendor'
#         serializer = CustomerSerializers(data=request.data)

#         # Line to bypass customer feild validation using fake key otherwise VendorsSerializer will definately throw error
#         # I used the fake_key value such that it is not present in the Users database but present in Customer database
#         fake_customer_id ="1"
#         request.data['customer'] = fake_customer_id
#         venserializer = VendorsSerializers(data=request.data)

#         if not serializer.is_valid():     
#             return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
#         if not venserializer.is_valid():
#             return Response(ven_loc_serializerr.errors, status=status.HTTP_400_BAD_REQUEST)
#         serializer.save()
#         # overriding previous fake coustomer id field
#         request.data['customer'] = serializer.data['id']
#         venserializer = VendorsSerializers(data=request.data)
#         if venserializer.is_valid():
#             venserializer.save()
#             return Response(venserializer.data, status=status.HTTP_201_CREATED)
        

class UsersList(APIView):

    permission_classes = (IsAuthenticated,)
    def get(self,request,format=None):
        users     = Users.objects.all()
        serializer = UsersSerializers(users,many=True)
        return Response(serializer.data)

    permission_classes = (AllowAny,)
    def post(self,request,format=None):
        if request.user.is_authenticated():
            return Response({"message": "Permission not granted"}, status=status.HTTP_400_BAD_REQUEST)
        request.data['customer_role']='user'

        serializer = CustomerSerializers(data=request.data)
        # Line to bypass customer feild validation using fake key otherwise UsersSerializer will definately throw error
        # I used the fake_key value such that it is not present in the Users database but present in Customer database
        fake_customer_id ="1"
        request.data['customer_id'] = fake_customer_id
        userserializer = UsersSerializers(data=request.data)
        if not serializer.is_valid():     
            return Response({"status":False,"message":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
        if not userserializer.is_valid():
            return Response({"success":False,"message":userserializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        # For debugging purpose
        # print(serializer.data)
        # overriding previous fake coustomer id field
        request.data['customer_id'] = serializer.data['id']
        userserializer = UsersSerializers(data=request.data)
        # No need to check is_valid again as above id will be newly created user
        if  userserializer.is_valid():
            userserializer.save()
            return Response({"success":True,"user":userserializer.data}, status=status.HTTP_201_CREATED)

 # for url bookinngs
class BookingsList(APIView):
    def get(self,request,format=None):
        if not checkvendor(request.user):
            return Response({'success':False,'message':'Permission not granted'},status=status.stauts.HTTP_403_FORBIDDEN)
        vendor_id = Vendors.objects.get(customer=request.user.id)
        vendors_locations = VendorsLocations.objects.filter(vendors = vendor_id )
        if request.GET.get('start'):
            start  = datetime.datetime.strptime(request.GET.get('start'),"%Y-%m-%d %H:%M:%S")
            start  = timezone.make_aware(start, timezone.get_current_timezone()).isoformat()
        else:
            start = None
        if request.GET.get('end'):
            end    = datetime.datetime.strptime(request.GET.get('end'),"%Y-%m-%d %H:%M:%S")
            end    = timezone.make_aware(end, timezone.get_current_timezone()).isoformat()
        else:
            end = None
        if start and end:
            bookings_identifiers = [i.booking_identifier for i in BookingsDetails.objects.filter(pickup_date__gte= start ).filter(drop_off_date__lte=end).filter(status="paid")]
        elif start:
            bookings_identifiers = [i.booking_identifier for i in BookingsDetails.objects.filter(pickup_date__gte=start ).filter(status="paid")]
        elif end:
            bookings_identifiers = [i.booking_identifier for i in BookingsDetails.objects.filter(drop_off_date__lte=end).filter(status="paid")]
        else:
            bookings_identifiers = [i.booking_identifier for i in BookingsDetails.objects.all().filter(status="paid")]

        bookings = Bookings.objects.filter(ven_loc_id__in = vendors_locations).filter(unique_id__in = bookings_identifiers)
        serializer = BookingSerializers( bookings , many=True)
        if request.accepted_renderer.format != 'json':
            form = BookingForm()
            return Response({'success':True,'bookings':serializer.data,'form':form,"start":request.GET.get('start'),"end":request.GET.get('end')},template_name='vbookings.html')
        else:
            return Response({'success':True,'bookings':serializer.data,"start":request.GET.get('start'),"end":request.GET.get('end')},status = status.HTTP_200_OK)

class MakeBooking(APIView):
    def get(self,request,format=None):
        if not checkvendor(request.user):
            return Response({'success':False,'message':'Permission not granted'},status=status.stauts.HTTP_403_FORBIDDEN)
        vendor_id = Vendors.objects.get(customer=request.user.id)
        if request.accepted_renderer.format != 'json':
            form = MakeBookingForm(ven_id=vendor_id)
            return Response({'success':True,'form':form},template_name='vmakebooking.html')

import http.client, urllib.parse
# >>> params = urllib.parse.urlencode({'@number': 12524, '@type': 'issue', '@action': 'show'})
# >>> headers = {"Content-type": "application/x-www-form-urlencoded",
# ...            "Accept": "text/plain"}
# >>> conn = http.client.HTTPConnection("bugs.python.org")
# >>> conn.request("POST", "", params, headers)
# >>> response = conn.getresponse()
# >>> print(response.status, response.reason)
# 302 Found
# >>> data = response.read()
# >>> data

class FinishBooking(APIView):
    def post(self,request,format=None):
        print(request.data)
        data = {"bikes":[]}
        for i in range(len(request.data.getlist('ven_loc_bikes_id'))):
            if int(request.data.getlist('booking_quantity')[i]) > 0:
                data['bikes'].append({"booking_quantity":request.data.getlist('booking_quantity')[i],"ven_loc_bikes_id":request.data.getlist('ven_loc_bikes_id')[i]})
        pickup_date    = datetime.datetime.strptime(request.data.get('pickup_date'),"%Y-%m-%d %H:%M:%S")
        pickup_date    = timezone.make_aware(pickup_date, timezone.get_current_timezone()).isoformat()
        drop_off_date  = datetime.datetime.strptime(request.data.get('drop_off_date'),"%Y-%m-%d %H:%M:%S")
        drop_off_date  = timezone.make_aware(drop_off_date, timezone.get_current_timezone()).isoformat()
        data.update({'pickup_date':pickup_date})
        data.update({'drop_off_date':drop_off_date})
        data.update({"discount_amount": 0,"status": "initiated","booking_source": "website","delivery_amount": 0})
        params        = json.dumps(data)
        print(params)
        headers = {"Content-type": "application/json"}
        url='imbs-wheelstreet.herokuapp.com'
        conn = http.client.HTTPSConnection(url)
        conn.request("POST", "/api/bookBikes/", params, headers)
        response = conn.getresponse()
        response = response.read()
        print("response "+response.decode('ascii'))
        response_data = json.loads(response.decode())
        print("json " +str(response_data))
        if response_data["success"]=="True":
            print("success")
            for bike in list(response_data["bookings"].getlist("bikes")):
                bikeobj = VendorsLocationsBikes.objects.get(id = int(bike["ven_loc_bikes_id"]))
                bike_serializer = VendorsLocationsBikesSerializers(bikeobj)
                bike.update({"ven_loc_bikes_id":bike_serializer.data})
        print(response_data)
        return Response({"data":response_data},template_name='vpayment.html')

# '{"bookings":{"bikes":[{"booking_quantity":"2","ven_loc_bikes_id":"6"}],
# "bookingDetails":{"pickup_date":"2016-07-20T12:00:00","drop_off_date":"2016-07-21T14:00:00","discount_amount":0,
# "status":"initiated","booking_source":"website","booking_identifier":"5GiYpQ5IYDQ8G2dNw4eElxdvKb3yPEAw","actual_amount":10400,"deposit_amount":2000,"delivery_amount":0}}}



class Payment(APIView):
    def post(self,request,format=None):
        print(request.data)
        data={"booking_identifier":request.data.get("booking_identifier"),"payment_method":request.data.get("payment_method"),"payment_status":request.data.get("payment_status")}
        params        = json.dumps(data)
        print(params)
        headers = {"Content-type": "application/json"}
        url='imbs-wheelstreet.herokuapp.com'
        conn = http.client.HTTPSConnection(url)
        conn.request("PATCH", "/api/bookBikes/", params, headers)
        response = conn.getresponse()
        response = response.read()
        print("response "+response.decode('ascii'))
        response_data = json.loads(response.decode())
        print("json " +str(response_data))
        print(response_data)
        return redirect("home")

class AvaliablityView(APIView):
    def get(self,request,format=None):
        if not checkvendor(request.user):
            return Response({'success':False,'message':'Permission not granted'},status=status.stauts.HTTP_403_FORBIDDEN)
        vendor_id = Vendors.objects.get(customer=request.user.id)
        if request.GET.get('location'):
            vendors_locations = VendorsLocations.objects.filter (id=request.GET.get('location'))
        else:
            vendors_locations = VendorsLocations.objects.filter(vendors = vendor_id )
        if request.GET.get('start'):
            start  = datetime.datetime.strptime(request.GET.get('start'),"%Y-%m-%d %H:%M:%S")- datetime.timedelta(hours= 1)
            start  = timezone.make_aware(start).isoformat()
        else:
            start = None
        if request.GET.get('end'):
            end    = datetime.datetime.strptime(request.GET.get('end'),"%Y-%m-%d %H:%M:%S")+datetime.timedelta(hours= 1)
            end    = timezone.make_aware(end).isoformat()
        else:
            end = None
        if start and end:
            bookings_identifiers = [i.booking_identifier for i in BookingsDetails.objects.filter((Q(pickup_date__lte=start) & Q(drop_off_date__gte=start))|(Q(pickup_date__lte=end) & Q(drop_off_date__gte=start))).filter(status="paid")]
        elif start:
            bookings_identifiers = [i.booking_identifier for i in BookingsDetails.objects.filter(pickup_date__gte=start ).filter(status="paid")]
        elif end:
            bookings_identifiers = [i.booking_identifier for i in BookingsDetails.objects.filter(drop_off_date__lte=end).filter(status="paid")]
        else:
            bookings_identifiers = [] # when start date end date not given it will show all bikes in his fleet

        bookings  = Bookings.objects.filter(ven_loc_id__in = vendors_locations).filter(unique_id__in = bookings_identifiers)
        all_bikes = VendorsLocationsBikes.objects.filter(ven_loc__in = vendors_locations)
        for bike in all_bikes:
            bike.bikes_quantity = bike.bikes_quantity - bookings.filter(ven_loc_bikes = bike.id).aggregate(quantity= Sum(F('booking_quantity')))['quantity'] if not \
            not bookings.filter(ven_loc_bikes = bike.id).aggregate(quantity= Sum(F('booking_quantity')))['quantity'] else bike.bikes_quantity
        serializer = VendorsLocationsBikesSerializers( all_bikes, many=True)
        if request.GET.get('start'):
            start  = datetime.datetime.strptime(request.GET.get('start'),"%Y-%m-%d %H:%M:%S")+ datetime.timedelta(hours= 1)
            start  = timezone.make_aware(start).isoformat()
        else:
            start = None
        if request.GET.get('end'):
            end    = datetime.datetime.strptime(request.GET.get('end'),"%Y-%m-%d %H:%M:%S")-datetime.timedelta(hours= 1)
            end    = timezone.make_aware(end).isoformat()
        if request.accepted_renderer.format != 'json':
            form = MakeBookingForm(ven_id=vendor_id)
            return Response({'success':True,'avaliable':serializer.data,'form':form,"start":request.GET.get('start'),"end":request.GET.get('end')},template_name='vavaliablity.html')
        else:
            return Response({'success':True,'avaliable':serializer.data,"start":request.GET.get('start'),"end":request.GET.get('end')},status = status.HTTP_200_OK)



class AvailableBikes(APIView):
    permission_classes=(AllowAny,)
    def get(self,request,format=None):
        if not request.GET.get('start')  or not request.GET.get('end')  or not request.GET.get('lat') or not request.GET.get('lng'):
            return Response({"success":False,'message':"Request Parameters cannot be empty"},status=status.HTTP_400_BAD_REQUEST)
        pattern = re.compile("^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-2][0-9]:[0-6][0-9]:[0-6][0-9]$")
        if pattern.match(request.GET.get('start')) is None or pattern.match(request.GET.get('end')) is None:
            return Response({"success":False,'message':"Date Format not accepted"},status=status.HTTP_400_BAD_REQUEST)

        start           = datetime.datetime.strptime(request.GET.get('start'),"%Y-%m-%dT%H:%M:%S")
        start           = timezone.make_aware(start, timezone.get_current_timezone()).isoformat()
        end             = datetime.datetime.strptime(request.GET.get('end'),"%Y-%m-%dT%H:%M:%S")
        end             = timezone.make_aware(end, timezone.get_current_timezone()).isoformat()
        user_lat        = float(request.GET.get('lat'))
        user_lng        = float(request.GET.get('lng'))
        if start >= end:
            return Response({"success":False,'message':"End Date is before or equal to Pickup date! "},status=status.HTTP_400_BAD_REQUEST)
        vendors         = VendorsLocations.objects.all()
        vendorsList = []
        maxBikes = []
        bikesForYou = []
        for vendor in vendors:
            lat = float(vendor.latitude)
            lng = float(vendor.longitude)
            distance = (((acos(sin(( user_lat * pi /180)) * sin(( lat * pi /180))+cos(( user_lat *pi /180)) * cos(( lat * pi /180)) * cos((( user_lng - lng)*pi/180))))*180/pi )*60*1.1515*1.609344)
            if( distance < 30 ):
                vendorsList.append(vendor.id)
                ven_loc_bikes_objs = VendorsLocationsBikes.objects.filter(ven_loc_id=vendor)
                for bikeObj in ven_loc_bikes_objs:
                    maxBikes.append(bikeObj)

        for ven_loc_bikes in maxBikes:
            bookings = Bookings.objects.filter(ven_loc_bikes_id=ven_loc_bikes.id)
            if bookings:
                for singleBooking in bookings:
                    temp = BookingsDetails.objects.filter(booking_identifier=singleBooking.unique_id)                    
                    if temp:
                        bookedDetails = BookingsDetails.objects.filter(booking_identifier=singleBooking.unique_id).filter( Q(pickup_date__gt=end) | Q(drop_off_date__lt=start) | Q(status="initiated") )
                        # bookedDetails = BookingsDetails.objects.filter(booking_identifier=singleBooking.unique_id).filter( Q(pickup_date__gt=end) | Q(drop_off_date__lt=start)).exclude(status="initiated")
                        '''
                        if not a:
                            print "List is empty"
                        
                        Not below is to be observed with bookedDetails
                        '''
                        if bookedDetails:       # means this booking didnt clash so its here in bookedDetails and is available
                            booked = None       # Available
                            if ven_loc_bikes not in bikesForYou:
                                bikesForYou.append(ven_loc_bikes) 
                        else:   
                            booked = "Not Available"
                            if ven_loc_bikes in bikesForYou:
                                index = maxBikes.index(ven_loc_bikes)
                                maxBikes[index].bikes_quantity = maxBikes[index].bikes_quantity-singleBooking.booking_quantity
                            else :
                                bikesForYou.append(ven_loc_bikes)
                                index = maxBikes.index(ven_loc_bikes)
                                maxBikes[index].bikes_quantity = maxBikes[index].bikes_quantity-singleBooking.booking_quantity
                    else:
                        if ven_loc_bikes not in bikesForYou:
                                bikesForYou.append(ven_loc_bikes) 
                        print("Fake Entry Found")
            else:
                booked = None            
                bikesForYou.append(ven_loc_bikes)
    
        ''' 
        Logic to combine more than one bike model from different locations
        '''
        modelWiseBikes = []
        for value in bikesForYou:  
            model_name = str(value.bikes)
            done = 0    
            for bike in modelWiseBikes:
                for k,v in bike.items():
                    if k == 'bike_name':
                        if v == model_name:
                            bike['location'].append(VendorsLocationsBikesSerializers(value).data)
                            done = 1
                        break
            if done == 0:
                newbike = {}
                newbike['bike_name'] = model_name
                temp = VendorsLocationsBikes.objects.get(id=value.id).bikes
                newbike['bike_image'] = "https://d2ogitr3jia7eu.cloudfront.net/assets/media/bike/mobile/" + model_name.lower().replace(" ","_") + ".jpg"
                newbike['bike_image_small'] = "https://d2ogitr3jia7eu.cloudfront.net/assets/media/bike/small/" + model_name.lower().replace(" ","_") + ".jpg"
                newbike['bike_id'] = temp.id
                newbike['make_id'] = temp.make.id
                newbike['make_name'] = temp.make.make
                newbike['location'] = []
                VendorsLocationsBikesSerializers(value)
                newbike['location'].append(VendorsLocationsBikesSerializers(value).data)
                modelWiseBikes.append(newbike)
        # print(modelWiseBikes)
        print(request.user)
        return Response({"success":True,"message":"bikes on location","bikes": modelWiseBikes },status=status.HTTP_200_OK)

class BookBikes(APIView):
    permission_classes = (AllowAny,)
    def post(self,request,format=None):
        bookingserializer = BookingsDetailsSerializers(data=request.data, many=False)
        if  bookingserializer.is_valid(raise_exception=True):
            bookingserializer.save()
            return Response({"success":True,"message":"Prior to Checkout","bookings":{"bookingDetails":bookingserializer.data,"bikes":request.data['bikes']}}, status=status.HTTP_201_CREATED)
        else :
            # for key, value in bookingserializer.errors.items():
            #     error = key + ": " + value[0]
            #     break
            return Response({"success":False,'message':"Booking cannot be proceeded !",'error':error},status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    permission_classes = (AllowAny,)
    def patch(self,request,format=None):
        priorCheckout = PriorCheckoutSerializers(data=request.data,many=False)
        if  priorCheckout.is_valid(raise_exception=True):
            priorCheckout.save()
            return Response({"success":True,"message":"Booking Successfully Completed","booking":priorCheckout.data})
        else:
            error = ""
            for key, value in priorCheckout.errors.items():
                error = key + ": " + value[0]
            return Response({"success":False,'message':'Booking cannot be Completed',"errors":error},status=status.HTTP_400_BAD_REQUEST)  

class RiderDetails(APIView):
    permission_classes=(AllowAny,)
    def post(self,request,format=None):
        riderserializer = RiderDetailsSerializers(data=request.data)
        if  riderserializer.is_valid(raise_exception=True):
            riderserializer.save()
            return Response({"success":True,"message":"Rider Details Updated","riderDetails":riderserializer.data}, status=status.HTTP_201_CREATED)
        else :
            return Response({"success":False,'message':'Rider Details CANNOT be added',"errors":riderserializer.errors},status=status.HTTP_400_BAD_REQUEST)

def about(request):
    return render(request,'about.html',{})

def careers(request):
    return render(request,'careers.html',{})

def contact(request):
    return render(request,'contact.html',{})

def group(request):
    return render(request, 'group.html',{})

def privacy(request):
    return render(request,'privacy.html',{})

def faq(request):
    return render(request,'faq.html',{})

def terms(request):
    return render(request,'terms.html',{})

def blogs(request):
    return render(request, 'blog.html',{})
