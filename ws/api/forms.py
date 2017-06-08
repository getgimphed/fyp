from django.forms import modelformset_factory
from django.shortcuts import render
from api.models import VendorsLocationsBikes, VendorsLocations, VendorsLocationsBikesDetails, VendorsLocationsAccessories, VendorsLocationsBikesService, Bikes , Locations, \
 Fos, Vendors, Customer, VendorsLocationsBikesSold, Accessories
from django import forms
from material import Layout, Row, Column, Fieldset, Span2, Span3, Span4, Span5, Span6, Span10

FIELD_NAME_MAPPING = {'location': 'location_id','fos': 'fos_id','bikes':'bikes_id','bikes_rent':'bikes_rent'}

class CustomerForm(forms.ModelForm):
	password          = forms.CharField(max_length=30, min_length=8 , widget=forms.PasswordInput)
	confirm_password  = forms.CharField(max_length=30, min_length=8,widget=forms.PasswordInput)
	class Meta:
		model     = Customer
		fields    = ("mobile_number",'password','confirm_password')

class BookingForm(forms.Form):
    start          = forms.DateTimeField(input_formats=['YYYY-MM-DD HH:00:00'])
    end            = forms.DateTimeField(input_formats=['YYYY-MM-DD HH:00:00'])
    layout = Layout(
        Row('start', 'end'))

class MakeBookingForm(forms.Form):
    start          = forms.DateTimeField(input_formats=['YYYY-MM-DD HH:00:00'])
    end            = forms.DateTimeField(input_formats=['YYYY-MM-DD HH:00:00'])
    location       = forms.ModelChoiceField(queryset= VendorsLocations.objects.all())

    def __init__(self, ven_id, *args, **kwargs):
        super(MakeBookingForm, self).__init__(*args, **kwargs)
        self.fields['location'] = forms.ModelChoiceField(queryset=VendorsLocations.objects.filter(vendors = ven_id))



class VendorForm(forms.ModelForm):
	class Meta:
		model     = Vendors
		fields    = ("customer","username","company","company_register_address","company_corporate_address","bank_name","bank_account_number","bank_ifsc_code")


class VendorsLocationsBikesForm(forms.ModelForm):
    class Meta:
        model            = VendorsLocationsBikes
        fields           =("ven_loc","bikes","bikes_deposit",'bikes_rent')

    def add_prefix(self, field_name):
        # look up field name; return original if not found
        field_name = FIELD_NAME_MAPPING.get(field_name, field_name)
        return super(VendorsLocationsBikesForm, self).add_prefix(field_name)

    def __init__(self, id, *args, **kwargs):
        super(VendorsLocationsBikesForm, self).__init__(*args, **kwargs)
        self.ven_loc = id
        ven_location_bikes = [i.bikes.id for i in VendorsLocationsBikes.objects.filter(ven_loc = id)]
        instance = kwargs.pop('instance',None)
        if instance is not None:
        	self.fields['bikes'] = forms.ModelChoiceField(queryset=Bikes.objects.filter(id=instance.bikes.id),initial=instance.bikes.id )
        else:
        	self.fields['bikes'] = forms.ModelChoiceField(queryset=Bikes.objects.all().exclude(id__in  = ven_location_bikes))



class VendorsLocationsBikesDetailsForm(forms.ModelForm):
    class Meta:
        model            = VendorsLocationsBikesDetails
        fields           = ("ven_loc_bikes","reg_number","color","insurance_last_date_time","years_of_manu","next_service_date_time")
        widgets          = {'insurance_last_date_time': forms.DateInput(attrs={'class': 'datepicker'}),'years_of_manu': forms.DateInput(attrs={'class': 'datepicker'}),'next_service_date_time':forms.DateInput(attrs={'class':'datepicker'})}

    def __init__(self, id, *args, **kwargs):
        super(VendorsLocationsBikesDetailsForm, self).__init__(*args, **kwargs)
        self.ven_loc_bikes = id


class VendorsLocationsForm( forms.ModelForm):
    class Meta:
        model = VendorsLocations
        fields =('location','latitude','longitude','address','store_open_time','store_close_time','fos')
        widgets = {'store_open_time': forms.TimeInput(attrs={'class': 'timepicker'}),'store_close_time': forms.TimeInput(attrs={'class': 'timepicker'}),'latitude':forms.TextInput(attrs={'id':'latitude'}),'longitude':forms.TextInput(attrs={'id':'longitude'})}

    def add_prefix(self, field_name):
        # look up field name; return original if not found
        field_name = FIELD_NAME_MAPPING.get(field_name, field_name)
        return super(VendorsLocationsForm, self).add_prefix(field_name)

    def __init__(self, id , *args , **kwargs):
        super(VendorsLocationsForm,self).__init__(*args , **kwargs)
        self.add_prefix('fos')
        self.add_prefix('location')
        ven_locations = [i.location.id for i in VendorsLocations.objects.filter( vendors = id)]
        instance = kwargs.pop('instance',None)
        if instance is not None:
            ven_locations.remove(instance.location.id)
            self.fields['location'] = forms.ModelChoiceField(queryset=Locations.objects.all().exclude(id__in = ven_locations),initial=instance.id)
            self.fields['fos']      = forms.ModelChoiceField(queryset = Fos.objects.all() , initial = instance.fos)
        else :
            self.fields['location'] = forms.ModelChoiceField(queryset=Locations.objects.all().exclude(id__in = ven_locations))
            self.fields['fos']      = forms.ModelChoiceField(queryset = Fos.objects.all())


class VendorsLocationsAccessoriesForm(forms.ModelForm):
    class Meta:
        model            = VendorsLocationsAccessories
        fields           = ("location","accessories_id","rent",'quantity')

    def __init__(self,id,*args,**kwargs):
        super(VendorsLocationsAccessoriesForm, self).__init__(*args, **kwargs)
        self.location = id
        instance = kwargs.pop('instance',None)
        presentaccessoriesid = [accessories.accessories_id.id for accessories in VendorsLocationsAccessories.objects.filter(location = id )]
        if instance is not None:
            self.fields['accessories_id'] = forms.ModelChoiceField( queryset = Accessories.objects.all().filter(id=instance.accessories_id.id),initial =instance.accessories_id )
            self.fields['rent']           = forms.IntegerField(initial = instance.rent)
            self.fields['quantity']       = forms.IntegerField(initial = instance.quantity)
        else:
            self.fields['accessories_id'] = forms.ModelChoiceField( queryset = Accessories.objects.all().exclude(id__in = presentaccessoriesid))


class VendorsLocationsBikesServiceForm(forms.ModelForm):
    class Meta:
        model            = VendorsLocationsBikesService
        fields           = ("ven_loc_bikes","reason","service_start_date_time","service_end_date_time")
        widgets          = {'service_start_date_time': forms.DateTimeInput(attrs={'class': 'datetimepicker'}),'service_end_date_time': forms.DateTimeInput(attrs={'class': 'datetimepicker'})}


    def __init__(self,id,*args,**kwargs):
       super(VendorsLocationsBikesServiceForm, self).__init__(*args, **kwargs)
       self.ven_loc_bikes = id

class VendorsLocationsBikesSoldForm(forms.ModelForm):
    class Meta:
        model    = VendorsLocationsBikesSold
        fields   = ('reason','ven_loc_bikes')

    def __init__(self, id , *args ,**kwargs):
        super(VendorsLocationsBikesSoldForm,self).__init__(*args,**kwargs)
        instance = kwargs.pop('instance',None)
        self.fields['ven_loc_bikes'] = forms.ModelChoiceField(queryset=VendorsLocationsBikesDetails.objects.filter(id = id),initial=id)
