from django.urls import path
from . import views
from django.conf import settings
urlpatterns = [
path('', views.home, name='home'),
path('register/', views.register, name='register'),
path('login/', views.user_login, name='login'),
path('logout/', views.user_logout, name='logout'),
path('send-email-otp/',views.send_email_otp,name='send_email_otp'),
path("verify-email-otp/",views.verify_email_otp,name="verify_email_otp"),
path("products/",views.products,name="products"),
path("product/<int:id>/", views.product_detail, name="product_detail"),
path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
path('cart/', views.cart, name='cart'),
path('increase/<int:id>/', views.increase_quantity, name='increase_quantity'),
path('decrease/<int:id>/', views.decrease_quantity, name='decrease_quantity'),
path('remove/<int:id>/', views.remove_item, name='remove_item'),
path('update-quantity/<int:id>/<int:qty>/', views.update_quantity, name='update_quantity'),
path('clear-cart/', views.clear_cart, name='clear_cart'),
path('checkout/', views.checkout, name='checkout'),
path('order-success/<int:order_id>/', views.order_success, name='order_success'),
path('payment/', views.payment, name='payment'),
path('orders/', views.order_history, name='order_history'),
path('order/<int:id>/', views.order_detail, name='order_detail'),
path("apply-coupon/", views.apply_coupon, name="apply_coupon"),
path("remove-coupon/", views.remove_coupon, name="remove_coupon"),
path("clear-address/", views.clear_address, name="clear_address"),
path('cancel-order/<int:id>/', views.cancel_order, name='cancel_order'),
path('download-receipt/<int:id>/', views.download_receipt, name='download_receipt'),
path("settings/", views.user_settings, name="user_settings"),
path("change-password/", views.change_password, name="change_password"),
path("forgot-password/", views.forgot_password, name="forgot_password"),
path("send-forgot-otp/", views.send_forgot_otp, name="send_forgot_otp"),
path("verify-forgot-otp/", views.verify_forgot_otp, name="verify_forgot_otp"),
path("reset-password/", views.reset_password, name="reset_password"),
path("faq/", views.faq, name="faq"),
path("contact/", views.contact, name="contact"),
path("add-testimonial/", views.add_testimonial, name="add_testimonial"),
path("about/", views.about, name="about"),

# admin panel
path("dashboard/", views.admin_dashboard, name="admin_dashboard"),
path("admin-orders/", views.admin_orders, name="admin_orders"),
path("admin-orders/update/<int:id>/", views.update_order_status, name="update_order_status"),
path("admin-products/", views.admin_products, name="admin_products"),
path("admin-products/add/", views.add_product, name="add_product"),
path("admin-products/edit/<int:id>/", views.edit_product, name="edit_product"),
path("admin-products/delete/<int:id>/", views.delete_product, name="delete_product"),
path('admin-users/', views.admin_users, name='admin_users'),
path('admin-users/delete/<int:id>/', views.delete_user, name='delete_user'),
path('admin-categories/', views.manage_categories, name='manage_categories'),
path('delete-category/<int:id>/', views.delete_category, name='delete_category'),







]
