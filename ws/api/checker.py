# File for checking status of inactive/active bikes and correcting bikes_quantity in the database
from api.models import VendorsLocationsBikes , VendorsLocationsBikesDetails , VendorsLocationsBikesSold
def __init__():
	bikessold 	= VendorsLocationsBikesSold.objects.all()
	for i in bikessold:
		bikedetails = VendorsLocationsBikesDetails.objects.get(id=i.ven_loc_bikes.id)
		print(str(bikedetails) + str(bikedetails.status))
		bikedetails.status = 'sold'
		bikedetails.save()
	bikedetails = VendorsLocationsBikesDetails.objects.all()
	print("Active Bikes   : "+str(len(bikedetails.filter(status = 'active'))))
	print("Inactive Bikes : "+str(len(bikedetails.filter(status = 'inactive'))))
	bikes       = VendorsLocationsBikes.objects.all()
	for bike in bikes:
		print(str(bike.get_bike())+" : "+str(len(bikedetails.filter(ven_loc_bikes=bike.id).filter(status = 'active'))))
		bike.bikes_quantity = len(bikedetails.filter(ven_loc_bikes=bike.id).filter(status = 'active'))
		bike.save()