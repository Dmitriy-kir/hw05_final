from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    # Авторизация
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='users/login.html'),
        name='login',
    ),
    # Регистрация
    path('signup/', views.SignUp.as_view(), name='signup'),
    # Выход
    path(
        'logout/',
        LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout',
    ),
    # Смена пароля
    path(
        'password_change/',
        auth_views.PasswordChangeView.as_view(
            template_name='users/password_change_form.html'
        ),
        name='password_change',
    ),
    # Сообщение об успешном изменении пароля
    path(
        'password_change/done/',
        auth_views.PasswordChangeDoneView.as_view(
            template_name='users/password_change_done.html'
        ),
        name='password_change_done',
    ),
    # Восстановление пароля
    path(
        'password_reset/',
        auth_views.PasswordResetView.as_view(
            template_name='users/password_reset_form.html',
            # success_url = reverse_lazy('users:password_reset_done')
        ),
        name='password_reset',
    ),
    # Сообщение об отправке ссылки для восстановления пароля
    path(
        'password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='users/password_reset_done.html'
        ),
        name='password_reset_done',
    ),
    # Вход по ссылке для восстановления пароля
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html'
        ),
        name='password_reset_confirm',
    ),
    # Сообщение об успешном восстановлении пароля
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='users/password_reset_complete.html'
        ),
        name='password_reset_complete',
    ),
]
