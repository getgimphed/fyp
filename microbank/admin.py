from django.contrib import admin
from .models import Client, ClientGroup,LoanFor, Loan
# Register your models here.

admin.site.register(Client)
admin.site.register(ClientGroup)
admin.site.register(Loan)
admin.site.register(LoanFor)
