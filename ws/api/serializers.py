from api.models import Cities, Locations,  Vendors, VendorsLocations, Fos, Bikes, Make, VendorsLocationsBikes, \
VendorsLocationsAccessories, VendorsLocationsBikesDetails, VendorsLocationsBikesService, VendorsLocationsBikesSold, \
Users, UsersOtp, FacebookConnect, GoogleConnect, Availability,Customer, Bookings, BookingsDetails, Orders , Accessories, RiderDetails

# from django.contrib.auth.models import User
from django.contrib.auth.base_user import AbstractBaseUser
from rest_framework import serializers
import string, random, datetime
from rest_framework.validators import UniqueTogetherValidator
# for making bookings
from django.db.models import Q
from django.utils import timezone

# for caching database 
from django.core.cache import cache

def checkforeign(cls,key):
    if cls.objects.get(id=key):
        return True
    else:
        return False

class AccessoriesSerializers(serializers.ModelSerializer):
    class Meta:
        model              = Accessories
        fields             = '__all__'
class CitiesSerializers(serializers.ModelSerializer):
    class Meta:
        model              = Cities
        fields             = ("id","city_name","city_type","latitude","longitude")

class LocationsSerializers(serializers.ModelSerializer):
    city       = serializers.CharField(source='get_city',read_only=True)
    cities     = serializers.PrimaryKeyRelatedField(queryset=Cities.objects.all(),write_only=True)
    class Meta:
        model            =  Locations
        fields             = ("id","cities","city","location_name")

class CustomerSerializers(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True,required=False)
    class Meta:
        model           = Customer
        fields          = "__all__"
        read_only_fields      = ('is_admin','is_active','groups')
    def create(self,validated_data):
        customer       = Customer.objects.create_user(**validated_data)
        print(customer.mobile_number)
        return customer

    def validate(self,validated_data):
        if validated_data.get("password",None) != validated_data.get("confirm_password",None):
            raise serializers.ValidationError("password doesn't match")
        if len(validated_data["password"])<8:
            raise serializers.ValidationError("Password should be atleast 8 characters long")
        if validated_data["password"].isalpha():
            raise serializers.ValidationError("Include atleast numbers in password")
        if not validated_data["mobile_number"].isdigit():
            raise serializers.ValidationError("Invalid number")
        if len(validated_data["mobile_number"])!=10:
            raise serializers.ValidationError("Invalid number length of mobile number should be 10")
        return validated_data

class  VendorsSerializers(serializers.ModelSerializer):
    customer            = serializers.CharField(source='get_customer',read_only=True)
    customer_id         = serializers.PrimaryKeyRelatedField(source='customer',queryset=Customer.objects.all(),write_only=True)
    class Meta:
        model             = Vendors
        fields            ='__all__'
        read_only_fields  = ('added_on','modified_on')

    def create(self, validated_data):
        # For debugging
        # print(validated_data)
        vendor = Vendors(**validated_data)
        vendor.save()
        return vendor

    def update(self,instance,validated_data):
        instance.company                   = validated_data.get("company",instance.company)
        instance.company_register_address  = validated_data.get("company_register_address",instance.company_register_address)
        instance.company_corporate_address = validated_data.get("company_corporate_address",instance.company_corporate_address)
        instance.bank_name                 = validated_data.get("bank_name",instance.bank_name)
        instance.bank_account_number       = validated_data.get("bank_account_number" , instance.bank_account_number)
        instance.ifsc_code                 = validated_data.get("bank_ifsc_code", instance.bank_ifsc_code)
        password                           = validated_data.pop('password',None) 
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    

class FosSerializers(serializers.ModelSerializer):
    customer            = serializers.CharField(source='get_customer',read_only=True)
    customer_id         = serializers.PrimaryKeyRelatedField(source='customer',queryset=Customer.objects.all(),write_only=True)
    class Meta:
        model            = Fos
        read_only_fields =('added_on')

class VendorsLocationsSerializers(serializers.ModelSerializer):
    #locurl = serializers.URLField(source='get_absolute_url', read_only=True)
    bikes_count = serializers.SerializerMethodField('count_bikes',read_only=True)
    fos         = FosSerializers(read_only=True)
    fos_id      = serializers.PrimaryKeyRelatedField(queryset = Fos.objects.all(), source='fos',write_only=True)
    location    = serializers.CharField(source ='get_location',read_only=True)
    location_id = serializers.PrimaryKeyRelatedField(source='location',queryset=Locations.objects.all(),write_only=True)
    vendors     = serializers.CharField(source ='get_vendor',read_only=True)
    vendor_id   = serializers.PrimaryKeyRelatedField(source='vendors',queryset=Vendors.objects.all(),write_only=True)
    def count_bikes(self, loc):
        bikes_count = 0
        bikes = VendorsLocationsBikes.objects.filter(ven_loc = loc.id)
        for bike in bikes:
            bikes_count   += bike.bikes_quantity
        return bikes_count  
    class Meta:
        model            = VendorsLocations
        fields           = ("id","location","address","vendors","vendor_id","location_id","store_open_time","store_close_time","fos_id","bikes_count",'latitude','longitude',"fos")
        read_only_fields =('added_on','modified_on')
    
    def validate(self,validated_data):
        if validated_data.get("store_open_time") > validated_data.get("store_close_time"):
            raise serializers.ValidationError("store open time can't be early then store close time.")
        
        return validated_data




class BikesSerializers(serializers.ModelSerializer):
    make = serializers.CharField(source='get_make',read_only=True)
    make_id = serializers.PrimaryKeyRelatedField(source='make', queryset=Make.objects.all(),write_only=True)
    class Meta:
        model            = Bikes
        fields           ="__all__"
        # depth            = 1

class MakeSerializers(serializers.ModelSerializer):
    class Meta:
        model            = Make
        fields           ="__all__"
        read_only_fields =('')

class VendorsLocationsBikesSerializers(serializers.ModelSerializer):
    bikes         = serializers.CharField(source='get_bike', read_only=True)
    location       = serializers.CharField(source='get_loc',read_only=True)
    bikes_id      = serializers.PrimaryKeyRelatedField(queryset = Bikes.objects.all(), source='bikes',write_only=True)
    ven_loc       = serializers.PrimaryKeyRelatedField(queryset=VendorsLocations.objects.all(),write_only=True)
    class Meta:
        model            = VendorsLocationsBikes               
        fields           = ("id","bikes_quantity","ven_loc","location","bikes_deposit",'bikes_rent',"bikes",'bikes_id')
        read_only_fields = ('added_on','modified_on','bikes_quantity')
        validators=[UniqueTogetherValidator(queryset=VendorsLocationsBikes.objects.all(),fields=('ven_loc','bikes'))]


class VendorsLocationsAccessoriesSerializers(serializers.ModelSerializer):
    accessories_id  = serializers.PrimaryKeyRelatedField(queryset = Accessories.objects.all(),write_only=True)
    product         = serializers.CharField(source='get_product',read_only=True)
    class Meta:
        model       = VendorsLocationsAccessories
        fields      = ('id','location','accessories_id','product','rent','quantity')
        read_only_fields = ('id',)
        validators=[UniqueTogetherValidator(queryset=VendorsLocationsAccessories.objects.all(),fields=('accessories_id','location'))]

    def create(self,validated_data):
        accessorie = VendorsLocationsAccessories(**validated_data)
        accessorie.status ='active'
        accessorie.save()

class VendorsLocationsBikesDetailsSerializers(serializers.ModelSerializer):
    model              = serializers.CharField(source='get_loc_bikes_model',read_only=True)
    ven_loc_bikes      = serializers.PrimaryKeyRelatedField(queryset=VendorsLocationsBikes.objects.all(),write_only=True)
    class Meta:
        model          = VendorsLocationsBikesDetails
        fields         = ('id','ven_loc_bikes','model', 'status', 'reg_number', 'color', 'insurance_last_date_time' ,'years_of_manu','next_service_date_time')


    def create(self, validated_data):
        vendorlocbike = VendorsLocationsBikesDetails(**validated_data)
        vendorlocbike.save()
        ven_loc_bike  = VendorsLocationsBikes.objects.get(id=validated_data["ven_loc_bikes"].id)
        ven_loc_bike.bikes_quantity += 1
        ven_loc_bike.save()        
        return vendorlocbike


class VendorsLocationsBikesServiceSerializers(serializers.ModelSerializer):
    registration      = serializers.CharField(source = 'get_ven_loc_bikes',read_only=True)
    model             = serializers.CharField(source ='get_ven_loc_bikes_model',read_only=True)
    ven_loc_bikes     = serializers.PrimaryKeyRelatedField(queryset = VendorsLocationsBikesDetails.objects.all(),write_only=True)
 
    class Meta:
        model            = VendorsLocationsBikesService
        fields           = ('added_on','ven_loc_bikes','model','registration','reason','service_start_date_time','service_end_date_time')
        read_only        = ('added_on',)


class VendorsLocationsBikesSoldSerializers(serializers.ModelSerializer):
    bike          = serializers.CharField(source='get_ven_loc_bikes',read_only=True)
    ven_loc_bikes = serializers.PrimaryKeyRelatedField(queryset=VendorsLocationsBikesDetails.objects.all(),write_only=True)
    class Meta:
        model            = VendorsLocationsBikesSold
        fields           = ("ven_loc_bikes","reason","bike")
        #validators=[UniqueTogetherValidator(queryset=VendorsLocationsBikesSold.objects.all(),fields=('ven_loc_bikes'))]

        # depth            = 1
    def create(self, validated_data):
        vendorlocbike = VendorsLocationsBikesSold(**validated_data)
        vendorlocbike.save()
        bike = validated_data.get('ven_loc_bikes')
        print(bike)
        bike.status='sold'
        bike.save()
        ven_loc_bike  = bike.ven_loc_bikes       
        ven_loc_bike.bikes_quantity -= 1
        ven_loc_bike.save()        
        return vendorlocbike

    def validate(self,validated_data):
        ven_loc_bikes = validated_data.get('ven_loc_bikes')
        if ven_loc_bikes.status !='active':
            raise serializers.ValidationError("Bike already sold")

        print(validated_data)
        return validated_data
            

class UsersSerializers(serializers.ModelSerializer):
    customer            = serializers.CharField(source='get_customer',read_only=True)
    customer_id         = serializers.PrimaryKeyRelatedField(source='customer',queryset=Customer.objects.all(),write_only=True)
    class Meta:
        model            = Users
        #depth            = 1
        fields           = "__all__"

    def create(self,validated_data):
        user = Users(**validated_data)
        user.save()
        return user 

class UsersOtpSerializers(serializers.ModelSerializer):
    class Meta:
        model = UsersOtp
        fields           ="__all__"
        read_only_fields =('added_on')
        #depth            = 1

class FacebookConnectSerializers(serializers.ModelSerializer):
    class Meta:
        model = FacebookConnect
        fields           ="__all__"
        read_only_fields =('added_on')
        #depth            = 1

class GoogleConnectSerializers(serializers.ModelSerializer):
    class Meta:
        model = GoogleConnect
        fields           ="__all__"
        read_only_fields =('added_on')
        # depth            = 1


class BikesObjSerializers(serializers.Serializer):
    ven_loc_bikes_id    = serializers.IntegerField(required=False) 
    booking_quantity    = serializers.IntegerField(required=False)
    # deposit             = serializers.IntegerField(required=True)
    # def validate(self,validated_data):

class BookingSerializers(serializers.ModelSerializer):
    location   = serializers.CharField(source='get_location',read_only=True)
    bike       = serializers.CharField(source='get_bike',read_only=True)
    start_time = serializers.DateTimeField(source='get_start',read_only=True)
    end_time   = serializers.DateTimeField(source='get_end',read_only=True)
    quantity   = serializers.IntegerField(source='get_quantity',read_only=True)
    class Meta:
        model = Bookings
        fields = ('location','bike','start_time','end_time','quantity')

from django.core.exceptions import ObjectDoesNotExist

class BookingsDetailsSerializers(serializers.Serializer):
    
    bikes              = BikesObjSerializers(many=True,required=False)
    pickup_date        = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S",required=True)
    drop_off_date      = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S",required=True)
    discount_amount    = serializers.IntegerField()
    # Booking mode will come in next step
    # booking_mode       = serializers.ChoiceField(choices=[('cod','cod'),('paytm','paytm'),('payu','payu')])
    status             = serializers.ChoiceField(choices=[('initiated','initiated'),('paid','paid')])
    booking_source     = serializers.ChoiceField(choices=[('website','website',),( 'android','android'),('ios','ios'),('super','super'),('vendor','vendor'),])
    booking_identifier = serializers.CharField(max_length=32,read_only=True)
    actual_amount      = serializers.IntegerField(read_only=True)
    deposit_amount     = serializers.IntegerField(read_only=True)
    delivery_amount     = serializers.IntegerField(required=True)

    def create(self,validated_data):
        cache.clear()
        depositTotal    = 0
        rentTotal       = 0
        deliveryTotal   = 0
        unique_id       = BookingsDetailsSerializers.id_generator()
        pickup_date     = validated_data.pop('pickup_date')
        drop_off_date   = validated_data.pop('drop_off_date')
        
        # pickup_date     = datetime.datetime.strptime(pickup_date, "%Y-%m-%d-%H")
        # pickup_date     = timezone.make_aware(pickup_date, timezone.get_current_timezone()).isoformat()
        # drop_off_date   = datetime.datetime.strptime(drop_off_date, "%Y-%m-%d-%H")
        # drop_off_date   = timezone.make_aware(drop_off_date, timezone.get_current_timezone()).isoformat()
        
        hours           = ((drop_off_date - pickup_date).total_seconds())/3600
        bikes = validated_data.pop('bikes')
        if not bikes:
            raise serializers.ValidationError({"non_field_errors":"Empty bikes list not accepted!!!"})
        for bike in bikes:
            for i, (k,v) in enumerate(bike.items()):
                if v == 0:
                    raise serializers.ValidationError({"non_field_errors":"Vendor Id or quantity is not accepted!!!"})
                if str(k) == "ven_loc_bikes_id" :
                    ven_loc_bikes_id = v
                if str(k) == "booking_quantity" :
                    booking_quantity = v
            
            temp  = VendorsLocationsBikes.objects.get( id = ven_loc_bikes_id )
            rentph           = temp.bikes_rent
            depositOne       = temp.bikes_deposit
            ven_loc_id       = temp.ven_loc.id
            ven_loc_obj      = VendorsLocations.objects.get( id = ven_loc_id )
            rentTotal      += rentph * booking_quantity * hours
            depositTotal   += depositOne * booking_quantity
            # deliveryTotal  += delivery_amount
            Bookings.objects.create(unique_id=unique_id,ven_loc_id=ven_loc_obj,booking_quantity=booking_quantity,ven_loc_bikes_id=ven_loc_bikes_id)
        
        bookingsDetails = BookingsDetails(booking_identifier=unique_id,actual_amount=rentTotal,deposit_amount=depositTotal,pickup_date=pickup_date,drop_off_date=drop_off_date,**validated_data)
        bookingsDetails.save()
        order = Orders(booking_identifier=unique_id,booking_details=bookingsDetails,status='initiated')
        order.save()
        cache.clear()
        return bookingsDetails

    def validate(self,validated_data):
        if BookingsDetailsSerializers.isBookable(validated_data) is False :
            raise serializers.ValidationError("Booking cannot be proceeded. One or more than One Bikes Not availble for booking. Data sent to wheelstreet might be manipulated!!!")
        return validated_data

    def id_generator(size=32, chars= string.digits + string.ascii_letters):
        return ''.join(random.choice(chars) for _ in range(size))

    def isBookable(data) :
        cache.clear()
        # start           = datetime.datetime.strptime( data['pickup_date'],"%Y-%m-%d-%H")
        # start           = timezone.make_aware(start, timezone.get_current_timezone()).isoformat()
        # end             = datetime.datetime.strptime( data['drop_off_date'],"%Y-%m-%d-%H")
        # end             = timezone.make_aware(end, timezone.get_current_timezone()).isoformat()
        
        bikelist = []
        bikes = data['bikes']
        for bike in bikes:
            for i, (k,v) in enumerate(bike.items()):
                if str(k) == "ven_loc_bikes_id" :
                    bike_id  = v 
                if str(k) == "booking_quantity" :
                    quantity = v
            bikelist.append((bike_id,quantity))          # got all the ven_loc_bikes_id and their quantities he is asking for, to book
        
        start = data['pickup_date']
        end   = data['drop_off_date']

        #  to check if store is open or close 
        for bike in bikelist :
            try:
                store_open_time = VendorsLocationsBikes.objects.get(id=bike[0]).ven_loc.store_open_time.hour
                store_close_time = VendorsLocationsBikes.objects.get(id=bike[0]).ven_loc.store_close_time.hour
            except ObjectDoesNotExist:
                print("obj doesnt exist")
                raise serializers.ValidationError({"non_field_errors":"Vendor Id is not accepted!!!"})

            
            if start.hour > store_close_time or start.hour < store_open_time or end.hour > store_close_time or end.hour < store_open_time : 
                return False

        # Now checking if they are available for the start and end time durations
        for bike in bikelist :
            alreadyBookedQuantity = 0
            bookings = Bookings.objects.filter(ven_loc_bikes_id=bike[0])
            if bookings: # means not empty and there is a booking for this bike_id
                for singleBooking in bookings:
                    
                    temp = BookingsDetails.objects.filter(booking_identifier=singleBooking.unique_id)
                    if temp:
                        bookedDetails = BookingsDetails.objects.filter(booking_identifier=singleBooking.unique_id).filter( Q(pickup_date__gt=end) | Q(drop_off_date__lt=start) | Q(status="initiated") )
                        """ Not below is to be observed """
                        if not bookedDetails:      # means clashing of dates
                            booked = "Not Available"
                            alreadyBookedQuantity = alreadyBookedQuantity + singleBooking.booking_quantity
                    else:
                        print('fake entry found')
            if bike[1] > ( VendorsLocationsBikes.objects.get(id=bike[0]).bikes_quantity - alreadyBookedQuantity ) :
                print("bikes_quantity ",VendorsLocationsBikes.objects.get(id=bike[0]).bikes_quantity)
                print('booking failed')
                return False
        print('bike booked success')
        return True

class PriorCheckoutSerializers(serializers.Serializer):
    booking_identifier   = serializers.CharField(max_length=32,required=True)
    payment_status       = serializers.ChoiceField(choices=[('initiated','initiated'),('paid','paid')],required=True)
    payment_method       = serializers.ChoiceField(choices=[('cash','cash'),('card','card')],required=True)
    order_id             = serializers.CharField(max_length=32,required=False)

    def create(self,validated_data):
        cache.clear()
        booking_identifier       = validated_data['booking_identifier']
        payment_status           = validated_data['payment_status']
        payment_method           = validated_data['payment_method']
        status                   = payment_status + "_" + payment_method
        order                    = Orders.objects.get(booking_identifier=booking_identifier)
        order.status             = status
        order.save()
        booking                  = BookingsDetails.objects.get(booking_identifier=booking_identifier)
        booking.status           = payment_status
        booking.booking_mode     = payment_method
        booking.save()
        order_id                 = order.id
        validated_data['order_id'] = order_id
        return validated_data   



class AvailabilitySerializers(serializers.ModelSerializer):
    class Meta:
        model = Availability
        fields           ="__all__"
        read_only_fields =('added_on')
        # depth            = 1

class RiderDetailsSerializers(serializers.ModelSerializer):
    class Meta:
        model = RiderDetails
        fields = "__all__"
