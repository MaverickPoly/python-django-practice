from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user_type = models.CharField(max_length=50)  # Seller | Client
    country = models.CharField(max_length=200)
    profile_img = models.ImageField(upload_to="images/profile/")

    def __str__(self):
        return f"Profile<{self.user.username}>"


class Category(models.Model):
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Category<{self.title}>"


class Product(models.Model):
    title = models.CharField(max_length=400)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    stock = models.IntegerField()
    image = models.ImageField(upload_to="images/product/")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Product<{self.title}>"
    

class Review(models.Model):
    rating = models.IntegerField()
    message = models.TextField()
    user = models.ForeignKey(User, related_name="reviews", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name="reviews", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review<{self.message[:50]}>"
    

class Order(models.Model):
    STATUS_CHOICES = (
        ("Pending", "Pending"),
        ("Shipped", "Shipped"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
    )

    user = models.ForeignKey(User, related_name="orders", on_delete=models.SET_NULL, null=True)
    order_time = models.DateTimeField(auto_now_add=True)
    address = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    products = models.ManyToManyField(Product, through="OrderItem")

    def __str__(self):
        return f"Order<{self.id}, {self.status}>"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name="order_items", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"OrderItem<{self.product.title}, Quantity: {self.quantity}>"


class Cart(models.Model):
    user = models.ForeignKey(User, related_name="cart", on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through="CartItem")

    def __str__(self):
        return f"Cart<{self.user.username}>"
    

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name="cart_item", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(null=True)

    def __str__(self):
        return f"CartItem<{self.product.title}, Quantity: {self.quantity}>"
