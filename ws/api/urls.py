from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from . import views
from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse_lazy
from django.contrib import admin
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    url(r'^$', views.home, name='home'),
    # url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^terms',views.terms,name='terms'),
    url(r'^privacy$',views.privacy,name='privacy'),
    url(r'^faq$',views.faq,name='faq'),
    url(r'^blogs$',views.blogs,name='blogs'),
    url(r'^about$',views.about,name='about'),
    url(r'^careers$',views.careers,name='careers'),
    url(r'^contact$',views.contact,name='contact'),
    url(r'^group$',views.group,name='group'),
    url(r'^cities/$',views.CitiesList.as_view(),name='cities-details'),
    url(r'^cities/(?P<pk>[0-9]+)/$',views.CitiesDetail.as_view(),name='cities-detail'),
    url(r'^locations/$',views.LocationsList.as_view(),name='locations'),
    url(r'^locations/(?P<pk>[0-9]+)/$',views.LocationsDetail.as_view(),name='locations-detail'),
    url(r'^vendors/$',views.VendorsList.as_view(),name='vendors-details'),
    url(r'^vendors/(?P<pk>[0-9]+)/$',views.VendorsDetail.as_view(),name='vendors-detail'),
    url(r'^vendorslocations/$',views.VendorsLocationsList.as_view(),name='vendorslocations-list'),
    url(r'^vendorslocations/(?P<pk>[0-9]+)/$',views.VendorsLocationsDetail.as_view(),name='vendorslocations-detail'),
    url(r'^bikes/$',views.BikesList.as_view(),name='bikes-details'),
    url(r'^bikes/(?P<pk>[0-9]+)/$',views.BikesDetail.as_view(),name='bikes-detail'),
    url(r'^make/$',views.MakeList.as_view(),name='make-details'),
    url(r'^make/(?P<pk>[0-9]+)/$',views.MakeDetail.as_view(),name='make-detail'),
    url(r'^fos/$',views.FosList.as_view(),name='fos-details'),
    url(r'^fos/(?P<pk>[0-9]+)/$',views.FosDetail.as_view(),name='fos-detail'),
    url(r'^vendorslocationsbikes/$',views.VendorsLocationsBikesList.as_view(),name='vendorslocationsbikes-list'),
    url(r'^vendorslocationsbikes/(?P<pk>[0-9]+)/$',views.VendorsLocationsBikesDetail.as_view(),name='vendorslocationsbikes-detail'),
    url(r'^vendorslocationsaccessories/$',views.VendorsLocationsAccessoriesList.as_view(),name='vendorslocationsbikesaccessories-list'),
    url(r'^vendorslocationsaccessories/(?P<pk>[0-9]+)/$',views.VendorsLocationsAccessoriesDetail.as_view(),name='vendorslocationsbikesaccessories-detail'),
    url(r'^vendorslocationsbikesdetails/$',views.VendorsLocationsBikesDetailsList.as_view(),name='vendorslocationsbikesdetails-list'),
    url(r'^vendorslocationsbikesdetails/(?P<pk>[0-9]+)/$',views.VendorsLocationsBikesDetailsDetail.as_view(),name='vendorslocationsbikesdetails-detail'),
    url(r'^vendorslocationsbikesservice/$',views.VendorsLocationsBikesServiceList.as_view(),name='vendorslocationsbikesservice-list'),
    url(r'^vendorslocationsbikesservice/(?P<pk>[0-9]+)/$',views.VendorsLocationsBikesServiceDetail.as_view(),name='vendorslocationsbikesservice-detail'),
    url(r'^vendorslocationsbikessold/$',views.VendorsLocationsBikesSoldList.as_view(),name='vendorslocationsbikessold-list'),
    url(r'^vendorslocationsbikes/sold$',views.AddVendorsLocationsBikesSold.as_view(),name='vendorslocationsbikessold'),
    url(r'^vendorslocationsbikessold/(?P<pk>[0-9]+)/$',views.VendorsLocationsBikesSoldDetail.as_view(),name='vendorslocationsbikessold-detail'),
    url(r'^vendorlocationadd/$',views.AddVendorLocation.as_view(),name='addvendorlocation'),
    url(r'^vendorbikemodeladd/(?P<pk>[0-9]+)/$',views.AddVendorLocationBikeModel.as_view(),name='addvendorbikemodel'),
    url(r'^vendorbikeaccessoriesadd/(?P<pk>[0-9]+)/$',views.AddVendorLocationAccessories.as_view(),name='addvendorbikeaccessories'),
    url(r'^vendorbikedetailsadd/(?P<pk>[0-9]+)/$',views.AddVendorLocationBikeDetails.as_view(),name='addvendorbikedetails'),
    url(r'^vendorbikeserviceadd/(?P<pk>[0-9]+)/$',views.AddVendorLocationBikeService.as_view(),name='addvendorbikeservice'),
    url(r'^vendorbikes$',views.VendorsBikes.as_view(),name='bikes'),
    url(r'^vendor/registerform/$',views.VendorRegister.as_view(),name="addvendor"),
    url(r'^vendor/register/$',views.VendorsList.as_view(),name='vendor-register'),
    url(r'^user/register/$',views.UsersList.as_view(),name='user-register'),
    url(r'^avaliablity/$',views.checkavaliablity,name='avaliablity'),
    url(r'^bookings/$',views.BookingsList.as_view(),name='bookings'),    
    url(r'^login$',(views.Login.as_view()),name='login_view'),
    url(r'^logout$', views.Logout.as_view(),name='logout_view'),
    # url(r'^vendor/(?P<pk>[0-9]+)/forgotpassword/$',views.VendorsDetail.as_view(),name='forgot-password'),
    # url(r'^log/$', TemplateView.as_view(template_name='vlogin.html')),
    url(r'^getAvailableBikes/$',views.AvailableBikes.as_view(),name='availableBikes'),
    url(r'^bookBikes/$',views.BookBikes.as_view(),name='bookBikes'),
    url(r'^makebooking/$',views.MakeBooking.as_view(),name='makebooking'),
    url(r'^makebooking/avaliablity/$',views.AvaliablityView.as_view(),name='avaliablity'),
    url(r'^book/$',views.FinishBooking.as_view(),name='finishbooking'),
    url(r'^payment/$',views.Payment.as_view(),name='payment'),
    url(r'^riderDetails/$',views.RiderDetails.as_view(),name='riderDetails'),
    ]
#Needed to parse data request to any format
urlpatterns = format_suffix_patterns(urlpatterns)

