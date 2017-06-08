from django.contrib.auth.decorators import user_passes_test, login_required
from django.http import HttpResponseRedirect
active_required = user_passes_test(lambda u: u.is_active,login_url='/login')

def my_login_required(view_func):
    decorated_view_func = login_required(active_required(view_func))
    return decorated_view_func

# def my_login_required(function):
#     def wrapper(request, *args, **kw):
#         user=request.user
#         if not (user.id and request.session.get('code_success')):
#             return HttpResponseRedirect('login/')
#         else:
#             return function(request, *args, **kw)
#     return wrapper
