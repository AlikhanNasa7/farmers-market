from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra):
        if not email:
            raise ValueError("The email data must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password, **extra):
        extra.setdefault('is_staff', True)
        extra.setdefault('is_superuser', True)

        if extra.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")
        return self.create_user(email, password, **extra)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=25, blank=True)
    last_name = models.CharField(max_length=25, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email









class Admin(models.Model):
    id = models.OneToOneField('User', models.DO_NOTHING, db_column='id', primary_key=True)
    permissions = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Admin'


class Buyer(models.Model):
    id = models.OneToOneField('User', models.DO_NOTHING, db_column='id', primary_key=True)
    purchase_history = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Buyer'


class Delivery(models.Model):
    delivery_method = models.CharField(max_length=11)
    cost = models.DecimalField(max_digits=10, decimal_places=0)
    status = models.CharField(max_length=10, blank=True, null=True)
    order_date = models.DateTimeField()
    delivery_date = models.DateTimeField()
    farmer_confirmation = models.IntegerField(blank=True, null=True)
    buyer_confirmation = models.IntegerField(blank=True, null=True)
    buyer = models.ForeignKey(Buyer, models.DO_NOTHING)
    farmer = models.ForeignKey('Farmer', models.DO_NOTHING)
    order = models.OneToOneField('Order', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'Delivery'


class Farm(models.Model):
    farm_size = models.CharField(max_length=25)
    farm_location = models.CharField(max_length=200)
    farm_name = models.CharField(unique=True, max_length=100)
    farmerid = models.ForeignKey('Farmer', models.DO_NOTHING, db_column='farmerID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Farm'


class Farmer(models.Model):
    id = models.OneToOneField('User', models.DO_NOTHING, db_column='id', primary_key=True)
    selling_history = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Farmer'


class Order(models.Model):
    created_at = models.DateTimeField(blank=True, null=True)
    buyerid = models.ForeignKey(Buyer, models.DO_NOTHING, db_column='buyerID')  # Field name made lowercase.
    status = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Order'


class Product(models.Model):
    productid = models.AutoField(db_column='productID', primary_key=True)  # Field name made lowercase.
    productname = models.CharField(db_column='productName', max_length=100)  # Field name made lowercase.
    category = models.CharField(max_length=9, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    quantity = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.CharField(max_length=200, blank=True, null=True)
    farmid = models.ForeignKey(Farm, models.DO_NOTHING, db_column='farmID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Product'




