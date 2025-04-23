from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from .models import *
from django.http import HttpRequest, HttpResponse



# ================== General Views
def index(request: HttpRequest):
    return render(request, "index.html")



# ================== Auth Views
def login_view(request: HttpRequest):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            email_user = User.objects.get(email=email)
            user = authenticate(request, username=email_user.username, password=password)
        except:
            user = None
        
        if user:
            print("Login - User Found")
            login(request, user)
            messages.success(request, "Logged in successfully!")
            return redirect("my_profile")
        else:
            print("Login - User NOT Found")
            messages.error(request, "Invalid credentials!")
            return redirect("login_view")
    else:
        return render(request, "auth/login.html")
    

def register_view(request: HttpRequest):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        bio = request.POST.get("bio")
        user_type = request.POST.get("user_type")
        country = request.POST.get("country")
        profile_img = request.FILES.get("profile_img")

        if password != confirm_password:
            messages.warning(request, "Passwords do not match!")
            return redirect("register_view")
        if User.objects.filter(email=email).exists():
            messages.warning(request, "Email already exists!")
            return redirect("register_view")
        if User.objects.filter(username=username).exists():
            messages.warning(request, "Username already exists!")
            return redirect("register_view")

        if user_type not in ["Seller", "Client"]:
            messages.error(request, "Invalid User Type!")
            return redirect("register_view")

        user = User.objects.create(
            username=username, 
            email=email, 
            first_name=first_name, 
            last_name=last_name
        )
        user.set_password(password)
        user.save()

        profile = Profile.objects.create(
            user=user,
            bio=bio,
            user_type=user_type,
            country=country,
            profile_img=profile_img
        )
        profile.save()

        messages.success(request, "User registered successfully!")
        return redirect("login_view")
    else:
        return render(request, "auth/register.html")
    
@login_required(login_url="/auth/login/")
def logout_view(request: HttpRequest):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect("login_view")

@login_required(login_url="/auth/login/")
def change_password(request: HttpRequest):
    if request.method == "POST":
        old_password = request.POST.get("old_password")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if not request.user.check_password(old_password):
            messages.error(request, "Incorrect Password!")
            return redirect("change_password_view")
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect("change_password_view")
        request.user.set_password(password)
        request.user.save()
        login(request, request.user)
        return redirect("my_profile")
    else:
        return render(request, "auth/change_password.html")



# ================== Profile
@login_required(login_url="/auth/login/")
def profile_view(request: HttpRequest, user_id: int):
    user = get_object_or_404(User, id=user_id)
    context = {
        "current_user": user,
        "profile": user.profile
    }
    return render(request, "profile/profile.html", context)

@login_required(login_url="/auth/login/")
def my_profile(request: HttpRequest):
    return redirect("profile_view", user_id=request.user.id)

@login_required(login_url="/auth/login/")
def edit_profile(request: HttpRequest, user_id: int):
    if request.user.id != user_id:
        messages.error(request, "You can only edit your profile!")
        return redirect("profile_view", user_id=user_id)

    if request.method == "POST":
        bio = request.POST.get("bio", "")
        country = request.POST.get("country", "")
        profile_img = request.FILES.get("profile_img")

        profile: Profile = request.user.profile

        if bio:
            profile.bio = bio
        if country:
            profile.country = country
        if profile_img:
            profile.profile_img = profile_img

        profile.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("my_profile")
    else:
        return render(request, "profile/edit.html")
    
@login_required(login_url="/auth/login/")
def seller_products(request: HttpRequest, user_id):
    if is_client(request):
        messages.error(request, "Only sellers can have products!")
        return redirect("all_products")
    
    user = get_object_or_404(User, id=user_id)
    products = Product.objects.filter(author=user).order_by("created_at")
    context = {
        "products": products,
        "user": user
    }
    return render(request, "profile/seller_products.html", context)



# ================== Products Views
@login_required(login_url="/auth/login/")
def create_product(request: HttpRequest):
    if is_client(request):
        return redirect("all_products")
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        stock = request.POST.get("stock")
        image = request.FILES.get("image")
        category_title = request.POST.get("category")
        price = request.POST.get("price")

        if not Category.objects.filter(title=category_title).exists():
            messages.error(request, "Invalid category!")
            return redirect("create_product")
        
        category = Category.objects.get(title=category_title)
        product = Product.objects.create(
            title=title,
            description=description,
            stock=stock,
            image=image,
            author=request.user,
            category=category,
            price=price
        )
        product.save()
        messages.info(request, "Product created successfully!")
        return redirect("all_products")
    else:
        return render(request, "products/create.html")

@login_required(login_url="/auth/login/")
def all_products(request):
    products = Product.objects.all().order_by("created_at")
    context = {
        "products": products
    }
    return render(request, "products/all.html", context)

@login_required(login_url="/auth/login/")
def view_product(request: HttpRequest, id: int):
    product = get_object_or_404(Product, id=id)
    context = {
        "product": product
    }
    return render(request, "products/product.html", context)

@login_required(login_url="/auth/login/")
def delete_product(request: HttpRequest, id: int):
    if is_client(request):
        return redirect("all_products")
    product = get_object_or_404(Product, id=id)
    if product.author != request.user:
        messages.error(request, "You are not eligible to delete this product!")
        return redirect("view_product", id=id)
    product.delete()
    messages.success(request, "Product deleted successfully!")
    return redirect("all_products")

@login_required(login_url="/auth/login/")
def update_product(request: HttpRequest, id: int):
    if is_client(request):
        return redirect("all_products")
    
    product = get_object_or_404(Product, id=id)
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        stock = request.POST.get("stock")
        image = request.FILES.get("image")
        category_title = request.POST.get("category")
        price = request.POST.get("price")

        if not Category.objects.filter(title=category_title).exists():
            messages.error(request, "Invalid category!")
            return redirect("all_products")
        
        category = Category.objects.get(title=category_title)

        product.title = title
        product.description = description
        product.stock = stock
        product.image = image
        product.category = category
        product.price = price

        messages.success(request, "Product updated successfully!")
        return redirect("view_product", id=id)
    else:
        context = {
            "product": product
        }
        return render(request, "products/update.html", context)

@login_required(login_url="/auth/login/")
def search_products(request: HttpRequest):
    search = request.GET.get("query", "")
    category_title = request.GET.get("category")

    products = Product.objects.all()
    if Category.objects.filter(title=category_title).exists():
        category = Category.objects.get(title=category_title)
    else:
        category = None

    if search:
        products = products.filter(title__icontains=search)
    if category:
        products = products.filter(category=category)

    context = {
        "products": products,
        "search": search,
        "category": category_title
    }
    return render(request, "products/search.html", context)


# ================== Category Views
@login_required(login_url="/auth/login/")
def create_category(request: HttpRequest):
    if is_client(request):
        messages.error(request, "Clients cannot create category!")
        return redirect("all_products")

    if request.method == "POST":
        title = request.POST.get("title")

        category = Category.objects.create(title=title)
        category.save()
        messages.info(request, "Category created successfully!")
        return redirect("all_products")
    else:
        return render(request, "category/create.html")
    


# ================== Cart Views
@login_required(login_url="/auth/login/")
def cart_view(request: HttpRequest):
    if not is_client(request):
        messages.error(request, "Only clients have access to cart!")
        return redirect("all_products")
        
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    context = {
        "cart": cart,
        "cart_items": cart.items.all(),
    }
    print("Cart Items")
    print(cart.items.all())
    return render(request, "cart/cart.html", context)


@login_required(login_url="/auth/login/")
def add_to_cart(request: HttpRequest, id: int):
    if not is_client(request):
        messages.error(request, "Only clients have access to cart!")
        return redirect("all_products")
        
    product = get_object_or_404(Product, id=id)

    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    print(f"Created: {created}")
    if not created:  # Product is already in the cart
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f"{product.title} quantity updated in cart!")
        else:
            messages.warning(request, "Product stock limit has been reached!")
    else:  # Product is not in the cart
        if product.stock > 0:
            print(f"Quantity Added!")
            cart_item.quantity = 1 
            cart_item.save()
            messages.success(request, f"{product.title} added to cart!")
        else:
            messages.warning(request, "This product is out of stock!")
    return redirect("cart_view")


@login_required(login_url="/auth/login/")
def remove_from_cart(request: HttpRequest, id: int):
    if not is_client(request):
        messages.error(request, "Only clients have access to cart!")
        return redirect("all_products")
        
    product = get_object_or_404(Product, id=id)

    cart = get_object_or_404(Cart, user=request.user)
    cart_item = CartItem.objects.filter(cart=cart, product=product).first()

    if cart_item:
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            messages.success(request, f"Reduced quantity of {product.title} in cart!")
        else:
            cart_item.delete()
            messages.success(request, f"{product.title} removed from cart!")
    else:
        messages.warning(request, "This product is not in your cart!")

    return redirect("cart_view")


# ================== Review Views
@login_required(login_url="/auth/login/")
def product_reviews(request: HttpRequest, id: int):
    product = get_object_or_404(Product, id=id)
    if request.method == "POST":
        rating = request.POST.get("rating")
        message = request.POST.get("message")

        review = Review.objects.create(
            rating=rating, 
            message=message, 
            user=request.user, 
            product=product
        )
        review.save()
        messages.info(request, "Review created successfully!")
        return redirect("product_reviews", id=id)
    else:
        reviews = product.reviews.all().order_by("created_at")
        context = {
            "product": product,
            "reviews": reviews,
        }
        return render(request, "reviews/reviews.html", context)

@login_required(login_url="/auth/login/")
def product_review_delete(request: HttpRequest, id: int, review_id: int):
    product = get_object_or_404(Product, id=id)
    review = get_object_or_404(Review, id=review_id)
    if review.user == request.user:
        review.delete()
        messages.info(request, "Review deleted successfully!")
    else:
        messages.warning(request, "You do not have rights to delete this review!")
    return redirect("product_reviews", id=id)

@login_required(login_url="/auth/login/")
def product_review_update(request: HttpRequest, id: int, review_id: int):
    product = get_object_or_404(Product, id=id)
    review = get_object_or_404(Review, id=review_id)
    if review.user != request.user:
        messages.warning(request, "You cannot edit this review!")
        return redirect("product_reviews")

    if request.method == "POST":
        rating = request.POST.get("rating")
        message = request.POST.get("message")

        review.message = message
        review.rating = rating

        review.save()
        messages.info(request, "Review updated!")
        return redirect("product_reviews", id=id)
    else:
        context = {
            "product": product,
            "review": review,
        }
        return render(request, "reviews/update.html", context)
    


# ================== Orders Views
@login_required(login_url="/auth/login/")
def create_order(request: HttpRequest):
    if not is_client(request):
        messages.error(request, "Only clients can make orders!")
        return redirect("all_products")
        
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.all()

    if not cart_items.exists():
        messages.error(request, "Your cart is empty. Add items before placing an order.")
        return redirect("cart_view")
    
    if request.method == "POST":
        address = request.POST.get("address")
        if not address:
            messages.error(request, "Please provide a delivery address!")
            return redirect("cart_view")
        
        order = Order.objects.create(user=request.user, address=address)

        for cart_item in cart_items:
            if cart_item.product.stock < cart_item.quantity:
                messages.error(request, f"Not enough stock for {cart_item.product.title}")
                return redirect("cart_view")
            
            cart_item.product.stock -= cart_item.quantity
            cart_item.product.save()
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity
            )
        
        cart.items.all().delete()
        messages.success(request, "Order created successfully!")
        return redirect("user_orders", user_id=request.user.id)

    return redirect("cart_view")


@login_required(login_url="/auth/login/")
def update_order(request: HttpRequest, id: int):  # Update State only
    order = get_object_or_404(Order, id=id)

    if is_client(request):
        messages.error(request, "You do not have permission to update this order.")
        return redirect("order_detail", id=id)
    
    if request.method == "POST":
        new_status = request.POST.get("status")
        valid_statuses = [status[0] for status in Order.STATUS_CHOICES]

        if new_status in valid_statuses:
            order.status = new_status
            order.save()
            messages.success(request, f"Order status updated to {new_status}")
        else:
            messages.error(request, "Invalid status!")
    return redirect("user_orders", user_id=order.user.id)

@login_required(login_url="/auth/login/")
def delete_order(request: HttpRequest, id: int):  
    order = get_object_or_404(Order, id=id)

    if not is_client(request):
        messages.error(request, "You do not have permission to delete orders.")
        return redirect("all_products")
    
    if order.user == request.user:
        order.delete()
        messages.success(request, "Order deleted successfully!")
        return redirect("user_orders", user_id=request.user.id)
    else:
        messages.error(request, "You do not own this order!")
        return redirect("user_orders", user_id=request.user.id)


@login_required(login_url="/auth/login/")
def order_detail(request: HttpRequest, id: int):
    order = get_object_or_404(Order, id=id)

    if order.user != request.user and request.user.profile.user_type != "Seller":
        messages.error(request, "You cannot view this order!")
        return redirect("user_orders", user_id=request.user.id)
    
    context = {
        "order": order,
        "products": order.items.all(),
    }
    return render(request, "orders/detail.html", context)

@login_required(login_url="/auth/login/")
def user_orders(request: HttpRequest, user_id: int):
    if not is_client(request):
        messages.error(request, "You do not have access to orders!")
        return redirect("all_products")
    if request.user.id != user_id:
        messages.error(request, "You do not have permission to view these orders!")
        return redirect("user_orders", user_id=request.user.id)

    orders = request.user.orders.all() 

    context = {
        "orders": orders,
    }
    return render(request, "orders/user_orders.html", context)



# ================== Utils
def is_client(request: HttpRequest):
    """
     Returns true if User is Client
    """
    if request.user.profile.user_type != 'Seller':
        return True
    return False


"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your Cart</title>
</head>
<body>
    <h1>Your Cart</h1>

    <ul>
        {% for item in cart_items %}
            <li>
                <img src="{{ item.product.image.url }}" alt="{{ item.product.title }}" width="100">
                <strong>{{ item.product.title }}</strong> - ${{ item.product.price }}
                <p>Quantity: {{ item.quantity }}</p>
                <a href="{% url 'add_to_cart' item.product.id %}">Add More</a>
                <a href="{% url 'remove_to_cart' item.product.id %}">Remove</a>
            </li>
        {% endfor %}
    </ul>

    {% if not cart_items %}
        <p>Your cart is empty.</p>
    {% endif %}
</body>
</html>
"""