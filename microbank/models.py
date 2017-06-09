from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Client(models.Model):
    user            = models.ForeignKey(User)
    id              = models.AutoField(db_column='id',primary_key=True)
    # name            = models.CharField(max_length=30)
    address 		= models.TextField()
    mobile          = models.CharField(unique=True,max_length=11)
    # loanTaken       = models.IntegerField()
    # loanId          = models.ForeignKey('Loan',to_field='id',null=True)
    singleOrGroup   = models.IntegerField()
    groupId         = models.ForeignKey('ClientGroup',blank=True,null=True,related_name='g_id')
    deposit         = models.IntegerField()

    def __str__(self):
        return str(self.user.first_name)

class ClientGroup(models.Model):
    id              = models.AutoField(db_column='id',primary_key=True)
    group           = models.CharField(db_column='g_id',max_length=32)
    def __str__(self):
        return self.group

class LoanFor(models.Model):
    id              = models.AutoField(db_column='id',primary_key=True)
    reason          = models.CharField(max_length=32)

class Loan(models.Model):
    id              = models.AutoField(db_column='id',primary_key=True)
    groupOrSingle   = models.IntegerField() # 0 means single user and 1 means group
    groupId         = models.ForeignKey('ClientGroup',null=True,blank=True)
    clientId        = models.ForeignKey('Client',null=True,blank=True)
    amount 		    = models.IntegerField()
    interestRate    = models.DecimalField(max_digits = 4, decimal_places=2)
    loanPayed       = models.IntegerField()
    duration        = models.IntegerField()

    def __str__(self):
        if self.groupId is not None:
            return self.groupId.group
        else:
            return self.clientId.user.first_name
