from django.db import models

# Create your models here.
class Client(models.Model):
    id              = models.AutoField(db_column='id',primary_key=True)
    name            = models.CharField(max_length=30)
    address 		= models.CharField(max_length=255)
    mobile          = models.BigIntegerField()
    loanTaken       = models.BinaryField()

class ClientGroup(models.Model):
    id              = models.AutoField(db_column='id',primary_key=True)
    groupId         = models.CharField(db_column='g_id',max_length=32)
    clientId        = models.ForeignKey('Client',null=False)

class LoanFor(models.Model):
    id              = models.AutoField(db_column='id',primary_key=True)
    reason          = models.CharField(max_length=32)

class Loan(models.Model):
    id              = models.AutoField(db_column='id',primary_key=True)
    groupOrSingle   = models.BinaryField() # 0 means single user and 1 means group
    groupId         = models.ForeignKey('ClientGroup',null=True)
    clientId        = models.ForeignKey('Client',null=True)
    amount 		    = models.IntegerField()
    interestRate    = models.DecimalField(max_digits = 4, decimal_places=2)
