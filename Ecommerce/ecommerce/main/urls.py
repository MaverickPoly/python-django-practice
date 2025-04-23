from django.urls import path
from . import views


urlpatterns = [
    # General
    path("", views.index, name="index"),

    # Auth
    path("auth/login/", views.login_view, name="login_view"),
    path("auth/register/", views.register_view, name="register_view"),
    path("auth/logout/", views.logout_view, name="logout_view"),
    path("auth/password/change/", views.change_password, name="change_password_view"),

    # Profile
    path("user/<int:user_id>/", views.profile_view, name="profile_view"),
    path("user/me/", views.my_profile, name="my_profile"),
    path("user/<int:user_id>/edit/", views.edit_profile, name="edit_profile"),
    path("user/<int:user_id>/products/", views.seller_products, name="seller_products"),

    # Products
    path("product/create/", views.create_product, name="create_product"),
    path("products/all/", views.all_products, name="all_products"),
    path("product/<int:id>/", views.view_product, name="view_product"),
    path("product/<int:id>/delete/", views.delete_product, name="delete_product"),
    path("product/<int:id>/update/", views.update_product, name="update_product"),

    path("s/products/", views.search_products, name="search_products"),

    # Category
    path("category/create/", views.create_category, name="create_category"),

    # Cart
    path("cart/", views.cart_view, name="cart_view"),
    path("product/<int:id>/add_to_cart/", views.add_to_cart, name="add_to_cart"),
    path("product/<int:id>/remove_to_cart/", views.remove_from_cart, name="remove_from_cart"),

    # Review
    path("product/<int:id>/reviews/", views.product_reviews, name="product_reviews"),
    path("product/<int:id>/review/<int:review_id>/delete/", views.product_review_delete, name="product_review_delete"),
    path("product/<int:id>/review/<int:review_id>/update/", views.product_review_update, name="product_review_update"),

    # Orders
    path("order/create/", views.create_order, name="create_order"),
    path("order/<int:id>/update/", views.update_order, name="update_order"), # Only State
    path("order/<int:id>/delete/", views.delete_order, name="delete_order"),
    path("order/<int:id>/", views.order_detail, name="order_detail"),
    path("user/<int:user_id>/orders/", views.user_orders, name="user_orders"),
]
