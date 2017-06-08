from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Client(models.Model):
    user            = models.ForeignKey(User)
    id              = models.AutoField(db_column='id',primary_key=True)
    # name            = models.CharField(max_length=30)
    address 		= models.TextField()
    mobile          = models.CharField(unique=True,max_length=11)
    loanTaken       = models.IntegerField()
    # loanId          = models.ForeignKey('Loan',to_field='id',null=True)
    singleOrGroup   = models.IntegerField()

    def __str__(self):
        return str(self.user.id)

class ClientGroup(models.Model):
    id              = models.AutoField(db_column='id',primary_key=True)
    groupId         = models.CharField(db_column='g_id',max_length=32)
    clientId        = models.ForeignKey('Client',null=False)

class LoanFor(models.Model):
    id              = models.AutoField(db_column='id',primary_key=True)
    reason          = models.CharField(max_length=32)

class Loan(models.Model):
    id              = models.AutoField(db_column='id',primary_key=True)
    groupOrSingle   = models.IntegerField() # 0 means single user and 1 means group
    groupId         = models.ForeignKey('ClientGroup',null=True)
    clientId        = models.ForeignKey('Client',null=True)
    amount 		    = models.IntegerField()
    interestRate    = models.DecimalField(max_digits = 4, decimal_places=2)
