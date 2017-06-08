from django.db import models
from django.utils import timezone
# For extending User to customize it
from django.contrib.auth.models import User ,update_last_login ,Group
from django.contrib.auth.models import ( AbstractBaseUser, BaseUserManager, PermissionsMixin )
from django.core.validators import RegexValidator
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse

#Token authentication
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.conf import settings
 
# This code is triggered whenever a new user has been created and saved to the database
# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def create_auth_token(sender, instance=None, created=False, **kwargs):
#     if created:
#         Token.objects.create(user=instance)


class Cities(models.Model):

	numeric     = RegexValidator(r'^[0-9.\-]*$','Only numeric characters are allowed.')
	alpha       = RegexValidator(r'^[a-zA-Z\- ]*$','Only alphabet characters are allowed.')

	id 		    = models.AutoField(db_column='Id',primary_key=True)
	city_name   = models.CharField(max_length=50, validators=[alpha])
	latitude         = models.CharField(max_length=30,validators=[numeric])
	longitude         = models.CharField(max_length=30,db_column='long',validators=[numeric])
	added_by    = models.ForeignKey('Customer',null=True)
	added_on    = models.DateTimeField(auto_now_add=True)
	city_type   = models.CharField(max_length=10,choices=(('premium','premium'),('tier1','tier1'),('tier2','tier2'),('tier3','tier3'),('tier4','tier4')))
	modified_by = models.ForeignKey('Customer',null=True,blank=True,related_name='cities_modified')
	modified_on = models.DateTimeField(auto_now=True)

	class Meta:
		db_table  = 'tbl_cities'
	def __str__(self):
		return self.city_name

class Locations(models.Model):
	alpha       = RegexValidator(r'^[a-zA-Z(), /\- ]*$','Only alphabet characters are allowed.')

	id          = models.AutoField(db_column='Id',primary_key=True)
	location_name   = models.CharField(max_length=255, validators=[alpha])
	cities      = models.ForeignKey('Cities')
	added_by    = models.ForeignKey('Customer',null=True)
	added_on	= models.DateTimeField(auto_now_add=True)
	modified_by = models.ForeignKey('Customer',null=True,blank=True,related_name='locations_modified')
	modified_on = models.DateTimeField(auto_now=True)

	class Meta:
		db_table='tbl_locations'
	def __str__(self):
		return self.location_name
	def get_full_name(self):
		return self.location_name
	def get_short_name(self):
		return self.location_name
	def get_city(self):
		return self.cities.city_name

class CustomerManager(BaseUserManager):

	def _create_user( self, mobile_number, password,customer_role, is_active, is_admin, **extra_fields):
		now=timezone.now()
		customer = self.model(mobile_number=mobile_number, customer_role=customer_role, is_admin=is_admin, is_active=is_active, last_login=now, added_on=now, modified_on=now)
		customer.set_password(password)
		customer.is_superuser =is_admin
		customer.save()
		if customer_role   == 'vendor':
			g = Group.objects.get(name='vendor_group') 
			customer.groups.add(g)
			print(customer.groups)
		elif customer_role == 'super' :
			g = Group.objects.get(name='super_group')
			customer.groups.add(g)
			print(customer.groups)
		elif customer_role =='user':
			g = Group.objects.get(name = 'user_group')
			print(g.permissions)
			customer.groups.add(g)
			print(customer.groups)
		else:
			g = Group.objects.get(name = 'fos_group')
			print(g.permissions)
			customer.groups.add(g)
			print(customer.groups)
		return customer
		
	def create_user(self, mobile_number,customer_role,password=None,**extra_fields):
		return self._create_user(mobile_number,password,customer_role,True,False,**extra_fields)
	
	def create_superuser(self, mobile_number,customer_role,password=None,**extra_fields):
		return self._create_user(mobile_number,password,'super',True,True,**extra_fields)
        	

class Customer(AbstractBaseUser,PermissionsMixin):
	phone_regex = RegexValidator(regex=r'^\d{10}$', message="mobile should be 10 digits only.")

	objects = CustomerManager()
	ADDED_SOURCE    = (('website', 'website'),('android', 'android'),('ios', 'ios'),('super', 'super'),('vendor', 'vendor'),)
	
	id				= models.AutoField(db_column='Id', primary_key=True)
	mobile_number 	= models.CharField(max_length=15,unique=True,validators=[phone_regex])
	added_source 	= models.CharField(max_length=10, choices=ADDED_SOURCE, default='website')
	added_on 		= models.DateTimeField(auto_now_add=True, blank=False)
	customer_role	= models.CharField(max_length=8,choices=(('user','user'),('vendor','vendor'),('super','super'),('fos','fos')),default='user')
	modified_on		= models.DateTimeField(auto_now=True)
	modified_by     = models.ForeignKey('Customer',null=True,blank=True,related_name='customer_modified')
	is_active 		= models.BooleanField(default=True)
	is_admin 		= models.BooleanField(default=False)

	REQUIRED_FIELDS = ['customer_role','added_source']
	USERNAME_FIELD = 'mobile_number'
	class Meta:
		managed  = True
		db_table = 'tbl_customer'

	def username(self):
		return self.mobile_number
	def get_full_name(self):
		return self.mobile_number

	def get_short_name(self):
		return self.mobile_number
	
	def __str__(self):
		return self.mobile_number

	def has_perm(self, perm, obj=None):
		"Does the user have a specific permission?"
		# Simplest possible answer: Yes, always
		return perm in self.get_all_permissions()

	def has_module_perms(self, app_label):
		"Does the user have permissions to view the app `app_label`?"
		# Simplest possible answer: Yes, always
		return True
		
	def is_staff(self):
		"Is the user a member of staff?"
		# Simplest possible answer: All admins are staff
		return self.is_admin
	def get_groups(self):
		groups = ''
		for i in self.groups():
			groups += i+', '  
		return groups


class Vendors(models.Model):
	id                        = models.AutoField(db_column='Id',primary_key=True)
	customer                  = models.OneToOneField('Customer')
	username                  = models.CharField(max_length=100)
	company                   = models.CharField(max_length=30)
	company_register_address  = models.CharField(max_length=255)
	company_corporate_address = models.CharField(max_length=255)
	bank_name   			  = models.CharField(max_length=50)
	bank_account_number       = models.CharField(max_length=50)
	bank_ifsc_code            = models.CharField(max_length=50)
	
	class Meta:
		db_table='tbl_vendors'

	def __str__(self):
		return u'%s' % (self.username)
	def get_full_name(self):
		return u'%s' % (self.company)
	def get_short_name(self):
		return u'%s' % (self.company)
	def get_customer(self):
		return self.customer.mobile_number

class VendorsLocations(models.Model):
	numeric     = RegexValidator(r'^[0-9.\-]*$','Only numeric characters are allowed.')
	id  		= models.AutoField(db_column='Id',primary_key=True)
	vendors     = models.ForeignKey('Vendors',db_column='vendors_id')
	location    = models.ForeignKey('Locations',db_column='location_id')
	latitude    = models.CharField(max_length=30,validators=[numeric])
	longitude   = models.CharField(max_length=30,db_column='long',validators=[numeric])
	address     = models.CharField(max_length=255)
	store_open_time  = models.TimeField()
	store_close_time = models.TimeField()
	fos         = models.ForeignKey('Fos',db_column='fos_id')
	status      = models.CharField(max_length=8,choices=(('active','active'),('inactive','inactive')))
	added_by    = models.ForeignKey('Customer',null=True)
	added_on	= models.DateTimeField(auto_now_add=True)
	modified_by = models.ForeignKey('Customer',null=True,blank=True,related_name='vendors_modified')
	modified_on = models.DateTimeField(auto_now=True)
	
	class Meta:
		db_table='tbl_ven_loc'


	def __str__(self):
		return u'%s' % (self.location )
	def get_absolute_url(self):
		return reverse('vendorslocations-detail', args=[str(self.id)])
	def get_location(self):
		return self.location.location_name
	def get_vendor(self):
		return self.vendors.company #User name can be used
	def get_fos(self):
		return self.fos.first_name +" " + self.fos.last_name

class FosCash(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # 
    supers_id = models.IntegerField()
    collected = models.IntegerField()
    collection_date = models.DateTimeField()
    collected_by = models.IntegerField()

    class Meta:
        db_table = 'tbl_fos_cash'

class Fos(models.Model):
	id            = models.AutoField(db_column='Id', primary_key=True)
	first_name    = models.CharField(max_length=255)
	last_name     = models.CharField(max_length=255)
	customer      = models.ForeignKey('Customer')
	email         = models.EmailField(max_length=255, blank=False, unique=True, validators=[validate_email])

	class Meta:
	    db_table = 'tbl_fos_employees'

	def __str__(self):
	    return u'%s  %s' % (self.first_name ,self.last_name) 


class Bikes(models.Model):
    id 			= models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    make 		= models.ForeignKey('Make',db_column='make_id')
    status 		= models.CharField(max_length=8,default='active',choices=(('active','active'),('inactive','inactive')))
    model_name 	= models.CharField(max_length=30)
    featured 	= models.IntegerField(default=0)
    ignition 	= models.CharField(max_length=4,default='self',choices=(('self','self'),('kick','kick')))
    gear 		= models.IntegerField(default=5)
    tagline 	= models.CharField(max_length=255)
    engine 		= models.SmallIntegerField(default=0)
    power 		= models.DecimalField(max_digits=5, decimal_places=2,default=0.00)
    torque 		= models.DecimalField(max_digits=5, decimal_places=2,default=0.00)
    mileage 	= models.IntegerField(default=0)
    kerb_weight = models.SmallIntegerField(default=0) 
    seat_height = models.SmallIntegerField(default=0) 
    description = models.TextField() 
    brake 		= models.CharField(max_length=5,default='drum',choices=(('front','front'),('drum','drum'),('rear','rear')))
    fuel 		= models.CharField(max_length=6,default='petrol',choices=(('petrol','petrol'),('diesel','diesel')))
    added_on 	= models.DateTimeField(auto_now_add=True)
    pic1 		= models.CharField(max_length=255,default='no image')

    class Meta:
    	db_table = 'tbl_bikes'

    def __str__( self ) :
    	return u'%s' % (self.model_name)
    def get_make(self):
    	return self.make.make


class Make(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    make = models.CharField(unique=True, max_length=30)
    class Meta:
    	db_table = 'tbl_make'
    def __str__( self ):
    	return u'%s' % (self.make)

class VendorsLocationsBikes(models.Model):
	id 		  	    = models.AutoField(primary_key=True,db_column='Id')
	ven_loc   	    = models.ForeignKey('VendorsLocations',db_column='ven_loc_id')
	bikes    	    = models.ForeignKey('Bikes',db_column='bikes_id')
	bikes_rent	    = models.IntegerField()
	bikes_deposit   = models.IntegerField()
	bikes_quantity  = models.IntegerField(default=0)
	added_by        = models.ForeignKey('Customer',null=True,related_name='added')
	added_on	    = models.DateTimeField(auto_now_add=True)
	modified_by     = models.ForeignKey('Customer',null=True,blank=True,related_name='venlocbikes_modified')
	modified_on     = models.DateTimeField(auto_now=True)

	class Meta:
		db_table  = 'tbl_ven_loc_bikes'

	def __str__(self):
		return u'%s' % (self.bikes)
	def get_absolute_url(self):
		return reverse('vendorslocationsbikes-detail', args=[str(self.id)])
	def get_bike(self):
		return self.bikes.model_name
	def get_loc(self):
		return self.ven_loc.address+", " +self.ven_loc.get_location()

class Accessories(models.Model):
	id               = models.AutoField(primary_key=True,db_column='id')
	product          = models.CharField(max_length=30)	
	def __str__(self):
		return u'%s' % (self.product)

class VendorsLocationsAccessories(models.Model):
	id               = models.AutoField(primary_key=True,db_column='Id')
	location         = models.ForeignKey('VendorsLocations',db_column='ven_loc')
	accessories_id   = models.ForeignKey('Accessories')
	rent             = models.IntegerField()
	quantity         = models.IntegerField()
	status 			 = models.CharField(max_length=8,choices = (('active','active'),('inactive','inactive')),default='active')
	added_by         = models.ForeignKey('Customer',null=True)
	added_on		 = models.DateTimeField(auto_now_add=True)
	modified_by      = models.ForeignKey('Customer',default ='',null=True,blank=True,related_name='venlocbikesaccessories_modified')
	modified_on 	 = models.DateTimeField(auto_now=True)

	class Meta:
		db_table   = 'tbl_ven_loc_bikes_accessories'
	def get_product(self):
		return self.accessories_id.product

class VendorsLocationsBikesDetails(models.Model):
	id          	 		 = models.AutoField(primary_key=True,db_column='Id')
	ven_loc_bikes 	 		 = models.ForeignKey('VendorsLocationsBikes',db_column='ven_loc_bikes_id')
	status                   = models.CharField(max_length=8,choices=(('active','active'),('inactive','inactive'),('sold','sold')),default='active')
	reg_number       		 = models.CharField(max_length=12,unique=True)
	color			 		 = models.CharField(max_length=50)
	insurance_last_date_time = models.DateField()
	years_of_manu            = models.DateField()
	next_service_date_time   = models.DateField()
	added_on				 = models.DateTimeField(auto_now_add=True)
	added_by                 = models.ForeignKey('Customer',null=True)
 
	class Meta:
		db_table   = 'tbl_ven_loc_bikes_details'

	def __str__( self ):
		return u'%s' % (self.reg_number)

	def get_loc_bikes_model(self):
		return self.ven_loc_bikes.get_bike()

class VendorsLocationsBikesService(models.Model):
	id 				   		= models.AutoField(primary_key=True,db_column='Id')
	ven_loc_bikes           = models.ForeignKey('VendorsLocationsBikesDetails',db_column='ven_loc_bikes_id)')
	reason					= models.TextField()
	service_start_date_time = models.DateTimeField()
	service_end_date_time	= models.DateTimeField()
	added_on				= models.DateTimeField(auto_now_add=True)
	added_by                = models.ForeignKey('Customer',null=True)
	class Meta:
		db_table	= 'tbl_ven_loc_bike_service'
	def get_ven_loc_bikes (self):
		return self.ven_loc_bikes.reg_number
	def get_ven_loc_bikes_model(self):
		return self.ven_loc_bikes.get_loc_bikes_model()


class VendorsLocationsBikesSold(models.Model):
	id          			= models.AutoField(primary_key=True,db_column='Id')
	ven_loc_bikes 	        = models.ForeignKey('VendorsLocationsBikesDetails',db_column='ven_loc_bikes_id')
	added_on				= models.DateTimeField(auto_now_add=True)
	added_by                = models.ForeignKey('Customer',null=True)
	reason					= models.TextField()
	class Meta:
		db_table   = 'tbl_ven_loc_bike_sold'

	def get_ven_loc_bikes_id(self):
		return self.ven_loc_bikes.ven_loc_bikes.id

	def get_ven_loc_bikes(self):
		return self.ven_loc_bikes.reg_number
		
class Users(models.Model):
	alpha       = RegexValidator(r'^[a-zA-Z\-]*$','Only alphabet characters are allowed.')

	id				= models.AutoField(db_column='Id', primary_key=True)
	customer        = models.OneToOneField('Customer')
	name 			= models.CharField(max_length=255, validators=[alpha])
	email           = models.EmailField(max_length=255, blank=False, unique=True, validators=[validate_email])
	
	class Meta:
		db_table = 'tbl_users'
		
	def __str__( self ):
		return u'%s' % (self.name)

class UsersOtp(models.Model):
	numeric     = RegexValidator(r'^[0-9.\-]*$','Only numeric characters are allowed.')

	id				= models.AutoField(db_column='Id', primary_key=True)
	users		    = models.ForeignKey('Users',models.DO_NOTHING)
	otp 			= models.CharField(max_length=6, validators=[numeric])
	otp_added_on	= models.DateTimeField(auto_now_add=True, blank=False)
	otp_verified	= models.SmallIntegerField()

	class Meta:
		db_table = 'tbl_users_otp'

class FacebookConnect(models.Model): 
	id				= models.AutoField(db_column='Id', primary_key=True)
	users_id		= models.ForeignKey('Users',models.DO_NOTHING)
	fb_id			= models.CharField(max_length=255)
	
	class Meta:
		db_table= 'tbl_facebook_connect'

class GoogleConnect(models.Model): 
	id				= models.AutoField(db_column='Id', primary_key=True)
	users_id		= models.ForeignKey('Users',models.DO_NOTHING)
	google_id		= models.CharField(max_length=255)
	
	class Meta:
		db_table    = 'tbl_google_connect'

class Bookings(models.Model):
	id 					= models.AutoField(db_column='Id', primary_key=True)
	unique_id 			= models.CharField(max_length=32)
	# unique_id 			= models.ForeignKey('BookingsDetails',to_field='booking_identifier',unique=False)
	ven_loc_bikes 		= models.ForeignKey('VendorsLocationsBikes', db_column='ven_loc_bikes_id')
	ven_loc_id 			= models.ForeignKey('VendorsLocations', db_column='ven_loc_id') 
	booking_quantity 	= models.IntegerField()
	class Meta:
		db_table   = 'tbl_bookings'
	def get_location(self):
		return self.ven_loc_id.get_location()
	def get_bike(self):
		return self.ven_loc_bikes.get_bike()
	def get_start(self):
		booking = BookingsDetails.objects.get(booking_identifier = self.unique_id)
		return booking.get_pickup()
	def get_end(self):
		booking = BookingsDetails.objects.get(booking_identifier = self.unique_id)
		return booking.drop_off_date
	def get_quantity(self):
		return self.booking_quantity

class BookingsDetails(models.Model):
	BOOKING_SOURCE = (('website','website',),( 'android','android'),('ios','ios'),('super','super'),('vendor','vendor'),)
	id 					= models.AutoField(db_column='Id', primary_key=True)
	# booking_identifier  = models.ForeignKey('Bookings', db_column='booking_unique_id',to_field='unique_id')
	booking_identifier  = models.CharField(max_length=32,unique=True)
	pickup_date 		= models.DateTimeField()
	drop_off_date 		= models.DateTimeField()
	actual_amount 		= models.IntegerField()
	delivery_amount 	= models.DecimalField(max_digits = 5, decimal_places=2)
	deposit_amount		= models.IntegerField()
	discount_amount 	= models.IntegerField()
	booking_mode	    = models.CharField(max_length=9, default='initiated',choices=(('cash','cash'),('card','card'),('initiated','initiated')))
	status 				= models.CharField(max_length=10, choices=(('initiated','initiated'),('paid','paid')))
	added_on 			= models.DateTimeField(auto_now_add=True, blank=False)
	added_by            = models.ForeignKey('Customer',null=True)
	booking_source     	= models.CharField(max_length=10, choices=BOOKING_SOURCE, default='website')

	class Meta:
		db_table = 'tbl_bookings_details'
	def get_pickup(self):
		return self.pickup_date
class Orders(models.Model):
	id 					= models.AutoField(db_column='Id', primary_key=True)
	booking_identifier  = models.CharField(max_length=32,unique=True)
	booking_details     = models.ForeignKey('BookingsDetails',null=True,db_column='booking_details_id',to_field='id')
	status 				= models.CharField(max_length=9, choices=(('initiated','initiated'),('paid_card','paid_card'),('paid_cash','paid_cash')))
	class Meta:
		db_table = 'tbl_orders'

class Availability(models.Model):

	STATUS              = (('booked','booked'),('on_service','on_service'),)
	
	ADDED_SOURCE        = (('website','website',),( 'android','android'),('ios','ios'),('super','super'),('vendor','vendor'),)
	id 					= models.AutoField(primary_key=True,db_column='Id')
	ven_loc_bikes	    = models.ForeignKey('VendorsLocationsBikes',models.DO_NOTHING,max_length=255)
	bookings_identifier = models.ForeignKey('BookingsDetails',models.DO_NOTHING,max_length=255)
	not_available_at 	= models.DateTimeField(blank=True)
	status				= models.CharField(max_length=10, choices=ADDED_SOURCE, default='') 
	booking_quantity	= models.IntegerField()

	class Meta:
		db_table='tbl_availability'

class RiderDetails(models.Model):
	riderName 			= models.CharField(max_length=30) 
	riderMobile			= models.BigIntegerField()
	riderExtraHelmet	= models.CharField(max_length=5, choices= (('True','True'),('False','False'),) )
	booking_identifier  = models.CharField(max_length=32,unique=True)
	class Meta:
		db_table = 'tbl_rider_details'
