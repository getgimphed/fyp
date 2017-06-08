from django.contrib import admin
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.db.models import F
from api.models import Cities, Locations,  Vendors, VendorsLocations, Bikes, Make, VendorsLocationsBikes, \
VendorsLocationsAccessories, VendorsLocationsBikesDetails, VendorsLocationsBikesService, VendorsLocationsBikesSold, \
Users, UsersOtp, FacebookConnect, GoogleConnect, Availability,Fos,FosCash,Customer,Accessories, Bookings, BookingsDetails

class  VendorsLocationsBikesInline(admin.TabularInline):
	model = VendorsLocationsBikes

class  VendorsLocationsBikesDetailsInline(admin.TabularInline):
	model = VendorsLocationsBikesDetails

class  VendorsLocationsAccessoriesInline(admin.TabularInline):
	model = VendorsLocationsAccessories

class VendorsLocationsBikesServiceInline(admin.TabularInline):
	model = VendorsLocationsBikesService

class BookingsAdmin(admin.ModelAdmin):
	list_display = [ field.name for field in Bookings._meta.fields ]
	list_filter  = ('ven_loc_bikes',)
admin.site.register(Bookings,BookingsAdmin)

class BookingsDetailsAdmin(admin.ModelAdmin):
	list_display = [ field.name for field in BookingsDetails._meta.fields ]
admin.site.register(BookingsDetails,BookingsDetailsAdmin)

class CustomerCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    # password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = Customer
        fields = ('mobile_number', 'customer_role','added_source')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        # password2 = self.cleaned_data.get("password2")
        # if password1 and password2 and password1 != password2:
        #     raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(CustomerCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class CustomerChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = Customer
        fields = ('mobile_number', 'password', 'customer_role', 'is_active', 'is_admin')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class CustomerAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = CustomerChangeForm
    add_form = CustomerCreationForm
    excludes = ('modified_by','is_active','is_admin')
    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('mobile_number', 'customer_role', 'is_admin','added_source','password')
    list_filter = ('is_admin','customer_role')
    fieldsets = (
        (None, {'fields': ('mobile_number', 'password')}),
        ('Personal info', {'fields': ('customer_role',)}),
        ('Permissions', {'fields': ('is_admin','is_active')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('mobile_number', 'added_source','customer_role', 'password1')}
        ),
    )
    search_fields = ('mobile_number',)
    ordering = ('mobile_number',)
    filter_horizontal = ()
    def save_model(self,request,obj,form,change):
    	if obj.id:
    		obj.modified_by = request.user
    	obj.save()
# Now register the new UserAdmin...
admin.site.register(Customer, CustomerAdmin)

class CitiesAdmin(admin.ModelAdmin):
	list_display = [ field.name for field in Cities._meta.fields ] 
	excludes     = ('added_by','modified_by')
	list_filter  = ('city_type',)
	readonly_fields = ('added_by','modified_by')
	
	def save_model(self,request,obj,form,change):
		if not obj.id:
			obj.added_by = request.user
		else:
			obj.modified_by = request.user
		obj.save()
admin.site.register(Cities,CitiesAdmin)

class LocationsAdmin(admin.ModelAdmin):
	list_display =[ field.name for field in Locations._meta.fields ]
	excludes =('added_by','modified_by')
	readonly_fields =('added_by','modified_by')
	list_filter = ('cities',)

	def save_model(self,request,obj,form,change):
		if not obj.id:
			obj.added_by = request.user
		else:
			obj.modified_by = request.user
		obj.save()
admin.site.register(Locations,LocationsAdmin)

class VendorsAdmin(admin.ModelAdmin):
	list_display =[ field.name for field in Vendors._meta.fields ]
admin.site.register(Vendors,VendorsAdmin)

class VendorsLocationsAdmin(admin.ModelAdmin):
	list_display =[ field.name for field in VendorsLocations._meta.fields ]
	excludes  = ('modified_by','added_by')
	readonly_fields =('added_by','modified_by')
	list_filter = ('vendors','location','status')
	# inlines = [VendorsLocationsBikesInline,VendorsLocationsBikesAccessoriesInline]
	class Media:
		js = ['collapser.js'] 	
	# def formfield_for_foreignkey(self, VendorsLocations, request, **kwargs):
	# 	if VendorsLocations.name == "vendors":
	# 		kwargs["queryset"] = VendorsLocations.objects.filter(owner=request.user)
	# 	return super(MyModelAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
admin.site.register(VendorsLocations,VendorsLocationsAdmin)

class BikesAdmin(admin.ModelAdmin):
	list_display =[ field.name for field in Bikes._meta.fields ]
	list_filter  =('make','status','featured')
	class Media:
		js = ['collapser.js']

admin.site.register(Bikes,BikesAdmin)

class AccessoriesAdmin(admin.ModelAdmin):
	list_display =[ field.name for field in Accessories._meta.fields ]
admin.site.register(Accessories,AccessoriesAdmin)

class MakeAdmin(admin.ModelAdmin):
	list_display =[ field.name for field in Make._meta.fields ]
admin.site.register(Make,MakeAdmin)

class VendorsLocationsBikesAdmin(admin.ModelAdmin):
	list_display    = [ field.name for field in VendorsLocationsBikes._meta.fields ]
	readonly_fields = ('ven_loc','bikes','added_by','modified_by','bikes_quantity')
	list_filter     = ('bikes','ven_loc')
 	# inlines = [VendorsLocationsBikesDetailsInline,]
	class Media:
		js = ['collapser.js'] 
	def save_model(self,request,obj,form,change):
		if not obj.id:
			obj.added_by = request.user
			obj.bikes_quantity = 0
		else:
			obj.modified_by = request.user
		obj.save()
admin.site.register(VendorsLocationsBikes,VendorsLocationsBikesAdmin)

class VendorsLocationsAccessoriesAdmin(admin.ModelAdmin):
	list_display =[ field.name for field in VendorsLocationsAccessories._meta.fields ]
	excludes  = ('modified_by','added_by')
	readonly_fields =('added_by','modified_by')
	list_filter =('location',)
	class Media:
		js = ['collapser.js']
admin.site.register(VendorsLocationsAccessories,VendorsLocationsAccessoriesAdmin)

class VendorsLocationsBikesDetailsAdmin(admin.ModelAdmin):
	list_display =[ field.name for field in VendorsLocationsBikesDetails._meta.fields ]
	inlines = [VendorsLocationsBikesServiceInline,]
	excludes  = ('added_by',)
	readonly_fields = ('added_by',)
	list_filter     = ('ven_loc_bikes','status','color')
	class Media:
		js = ['collapser.js']
	def save_model(self,request,obj,form,change):
		if not obj.id:
			obj.added_by = request.user
			if obj.ven_loc_bikes:
				ven_loc_bike = VendorsLocationsBikes.objects.get(id = obj.ven_loc_bikes.id)
				ven_loc_bike.bikes_quantity = F('bikes_quantity')+ 1
				ven_loc_bike.save()
		obj.save()

admin.site.register(VendorsLocationsBikesDetails,VendorsLocationsBikesDetailsAdmin)

class VendorsLoctionsBikesServiceAdmin(admin.ModelAdmin):
	list_display =[ field.name for field in VendorsLocationsBikesService._meta.fields ]
	excludes  = ('added_by',)
	readonly_fields =('added_by',)
admin.site.register(VendorsLocationsBikesService,VendorsLoctionsBikesServiceAdmin)

class VendorsLocationsBikesSoldAdmin(admin.ModelAdmin):
	list_display =[ field.name for field in VendorsLocationsBikesSold._meta.fields  ]
	excludes  = ('modified_by')
	def save_model(self,request,obj,form,change):
		if not obj.id:
			obj.added_by = request.user
			ven_loc_bike = VendorsLocationsBikes.objects.get(id= ven_loc_bikes.id)
			ven_loc_bike.bikes_quantity = F('bikes_quantity')-1
			ven_loc_bike.save()
			obj.save()
		obj.save()
admin.site.register(VendorsLocationsBikesSold,VendorsLocationsBikesSoldAdmin)

class UsersAdmin(admin.ModelAdmin):
	list_display =[ field.name for field in Users._meta.fields ]
admin.site.register(Users,UsersAdmin)

class FosAdmin(admin.ModelAdmin):
	list_display =[ field.name for field in Fos._meta.fields ]
	excludes  = ('modified_by','added_by')
	readonly_fields =('added_by','modified_by')
admin.site.register(Fos)
