from django.db import models
from django.contrib.auth.models import AbstractUser,User
from django.contrib.auth.models import Group, Permission

from django.contrib.auth.models import User
from PIL import Image
from datetime import datetime, timedelta
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe
from django.utils import timezone


# Create your models here.



class CustomUser(AbstractUser):
# ignore this model just a sample for testing
# try this for upcoming projects
    birthday = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True, null=True)  # Add the 'address' field
    groups = models.ManyToManyField(Group, verbose_name='groups', blank=True, related_name='customuser_groups')
    user_permissions = models.ManyToManyField(Permission, verbose_name='user permissions', blank=True, related_name='customuser_permissions')

class Contact(models.Model):
    sno = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=13)
    message = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True, blank=True)
    
    def __str__(self) :
        return 'Message from ' + self.first_name + ' - ' + self.email
    

class Profile(models.Model):

    user=models.OneToOneField(User,on_delete=models.CASCADE)

    image=models.ImageField(default='default.jpg',upload_to='profile_pics')

    birthday = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=13,blank=True, null=True)
    aadhar_card = models.CharField(max_length=12,blank=False, null=True)

    DisplayFields = ['id','user','address','phone','profile_image','birthday','aadhar_card']
    SearchableFields = ['user__username','user__first_name','user__last_name']
    FilterFields=['address']

    def __str__(self) :
        return f'{self.user.username} Profile'
    
    def profile_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url)) 

    def save(self,*args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)

        if  img.height > 300 or img.width > 300:
            output_size = (300,300)
            img.thumbnail(output_size)
            img.save(self.image.path)

class Category(models.Model):

    cid = ShortUUIDField(unique=True,length=10,max_length=20,prefix='cat',alphabet='abcdefgh12345')
    title=models.CharField(max_length=100, default="Items")
    image=models.ImageField(default='default.jpg',upload_to='category_pics')

    class Meta:
        verbose_name_plural = "Categories"

    def category_image(self):
        return mark_safe('<img src= "%s" width="50" height="50"/>' % (self.image.url))
    
    def __str__(self) :
        return self.title

    def save(self,*args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)

        if  img.height > 300 or img.width > 300:
            output_size = (300,300)
            img.thumbnail(output_size)
            img.save(self.image.path)
    
class Seller(models.Model):

    sid = ShortUUIDField(unique=True,length=10,max_length=20,prefix='sel',alphabet='abcdefgh12345')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    title=models.CharField(max_length=100, default="")
    # image=models.ImageField(default='default.jpg',upload_to='product_pics')
    description = models.TextField(null=True,blank=True, default="I am an Ama=azing Seller")

    address=models.CharField(max_length=100, default="123 Main Street London")
    contact=models.CharField(max_length=100, default="+91 (1234) 567890")


    class Meta:
        verbose_name_plural = "Sellers"

    def __str__(self) :
        return self.title  
    

class Product(models.Model):
    pid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet='abcdefgh12345')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    Category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="category")
    total_bids = models.IntegerField(default=0)
    highest_bid = models.IntegerField(default=0)  # New field for highest bid
    winner_details = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_products')
    shipping_details_submitted = models.BooleanField(default=False)

    product_name = models.CharField(max_length=100, default="Items")
    image = models.ImageField(default='default.jpg', upload_to='product_pics')
    description = models.TextField(null=True, blank=True, default="This is the product")

    min_price = models.DecimalField(max_digits=10, decimal_places=2, default=2000)    
    price_interval = models.DecimalField(max_digits=10, decimal_places=2, default=100)

    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        verbose_name_plural = "Products"

    def product_image(self):
        return mark_safe('<img src="%s" width="50" height="50"/>' % self.image.url)

    def __str__(self):
        return self.product_name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)

    def status(self):
        current_time = datetime.now().time()
        if self.start_time <= current_time < self.end_time:
            return "Live"
        elif current_time < self.start_time:
            return "Upcoming"
        elif current_time > self.end_time:
            return "Closed"
        else:
            return "Unknown"

    @classmethod
    def place_bid(cls, user, product, amount):
        product.total_bids += 1

        # Check if the bid amount is higher than the current highest bid
        if amount > product.highest_bid:
            product.highest_bid = amount
            product.winner_details = user  # Set the winner_details field to the user who placed the bid
            product.save()

        bid = Bid.objects.create(user=user, product=product, amount=amount)

        # Create bid history
        BidHistory.objects.create(product=product, user=user, amount=amount, timestamp=timezone.now())

        return bid

    def is_live_for_bidding(self):
        current_datetime = datetime.now()
        return self.date == current_datetime.date() and self.start_time <= current_datetime.time() < self.end_time

    def is_valid_bid(self, amount):
        """
        Check if the bid amount is valid (higher than the current highest bid and follows the price interval).
        """
        current_highest_bid = self.highest_bid
        price_interval = self.price_interval
        
        # Calculate the minimum valid bid amount based on the current highest bid and price interval
        minimum_bid_amount = current_highest_bid + price_interval
        
        return amount >= minimum_bid_amount
    
    def total_bids_count(self):
    
        return self.bid_history.count()

    def get_winner(self):
        if self.bid_history.exists():
            highest_bid = self.bid_history.order_by('-amount').first()
            return highest_bid.user.username
        else:
            return "No winner yet"

    @property
    def winner(self):
        return self.get_winner()


class Bid(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='bids')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bid by {self.user.username} on {self.product.product_name}"

class BidHistory(models.Model):

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='bid_history')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bid history for {self.product.product_name} by {self.user.username}"



class ShippingDetails(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='shipping_details')
    address = models.TextField(blank=False, null=False)
    city = models.CharField(max_length=100,blank=False, null=False)
    state = models.CharField(max_length=100,blank=False, null=False)
    country = models.CharField(max_length=100,blank=False, null=False)
    pincode = models.CharField(max_length=6,blank=False, null=False)

    def __str__(self):
        return f"Shipping details of {self.product.product_name} for {self.user.first_name} {self.user.last_name} "


class Payment(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='payment')

    razor_pay_order_id = models.CharField(max_length=100,blank=True, null=True)
    razor_pay_payment_id = models.CharField(max_length=100,blank=True, null=True)
    razor_pay_payment_signature = models.CharField(max_length=100,blank=True, null=True)
    
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.product.product_name}"