from django.urls import path
from . import views

urlpatterns = [
    # Auth Endpoints
    path('api/auth/login/', views.api_login, name='api_login'),
    path('api/auth/register/', views.api_register, name='api_register'),
    path('api/auth/logout/', views.api_logout, name='api_logout'),
    path('api/auth/token/refresh/', views.api_token_refresh, name='api_token_refresh'),
    path('api/auth/password-reset/', views.api_forgot_password, name='api_forgot_password'),
    path('api/auth/password-reset-confirm/', views.api_reset_password, name='api_reset_password_confirm'),

    # Data Endpoints
    path('api/profile/', views.api_profile, name='api_profile'),
    path('api/leaderboard/', views.api_leaderboard, name='api_leaderboard'),
    path('api/add-visit/', views.api_add_visit, name='api_add_visit'),
    path('api/add-play/', views.api_add_play, name='api_add_play'),
    path('api/save-score/', views.api_save_score, name='api_save_score'),
    path('api/send-feedback/', views.api_send_feedback, name='api_send_feedback'),

    # Tracking (Legacy compatibility)
    path('accounts/add-visit/', views.api_add_visit),
    path('accounts/add-play/', views.api_add_play),

    # Legacy (for compatibility if needed)
    path('logout/', views.logout, name='logout'),
]
