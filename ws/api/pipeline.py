from api.models import  Users, FacebookConnect, GoogleConnect, Customer

def createUser(strategy, backend, response,details, user=None, *args, **kwargs ):
    if backend.__class__.__name__ == 'FacebookOAuth2':

        mobile_number = "999999999"
        customer = Customer(mobile_number=mobile_number,customer_role='user',added_source='Facebook',added_by='self')
        customer.set_password('sexypassword')
        customer.save()

        email = response.get('email','noemail@test.com')
        user = Users(
            name=response['name'],
            email=email,
            customer = customer,
            )
        user.save()

        fb_connect = FacebookConnect(fb_id=response['id'],users_id=user)
        fb_connect.save()


    if backend.__class__.__name__ == 'GoogleOAuth2':
        mobile_number = "999999999"
        customer = Customer(mobile_number=mobile_number,customer_role='user',added_source='Google',added_by='self')
        customer.set_password('sexypassword')
        customer.save()

        email = response.get('email','noemail@test.com')
        user = Users(
            name=response['name'],
            email=email,
            customer = customer,
            )
        user.save()

        g_connect = GoogleConnect(google_id=response['id'],users_id=user)
        g_connect.save()