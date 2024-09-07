from django.urls import path
from .views import (IndexView, subscriptions_list, unsubscribe, subscribe_to_category,
                    approve_comment, reject_comment, delete_comment)

urlpatterns = [
    path('', IndexView.as_view(), name='personal'),
    path('subscriptions/', subscriptions_list, name='subscriptions_list'),
    path('subscribe/', subscribe_to_category, name='subscribe'),
    path('unsubscribe/<int:subscription_id>/', unsubscribe, name='unsubscribe'),
    path('approve/<int:response_id>/', approve_comment, name='approve_comment'),
    path('reject/<int:response_id>/', reject_comment, name='reject_comment'),
    path('delete/<int:response_id>', delete_comment, name='delete_comment')
]