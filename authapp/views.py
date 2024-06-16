from authapp.models import Profile
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import DetailView, UpdateView

from authapp.forms import LoginForm, RegisterForm, ProfileForm


class LoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, 'authapp/login.html', {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                error_message = "Неверные учетные данные"
                return render(request, 'authapp/login.html', {'form': form, 'error_message': error_message})
        else:
            error_message = "Недействительная форма"
            return render(request, 'authapp/login.html', {'form': form, 'error_message': error_message})


class RegisterView(View):
    def get(self, request):
        form = RegisterForm()
        return render(request, 'authapp/register.html', {'form': form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            # Создаем профиль для нового пользователя
            profile = Profile.objects.create(user=user)

            # Логиним пользователя
            login(request, user)

            return redirect('home')  # Перенаправление на главную страницу после успешной регистрации

        return render(request, 'authapp/register.html', {'form': form})


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('home')  # Перенаправление на главную страницу после выхода


@method_decorator(login_required, name='dispatch')
class UserView(DetailView):
    model = User
    template_name = 'authapp/profile.html'
    context_object_name = 'user'

    def get_object(self, queryset=None):
        # Получаем объект пользователя
        user = super().get_object(queryset=queryset)

        # Пытаемся получить профиль пользователя, создаем, если не существует
        profile, created = Profile.objects.get_or_create(user=user)

        # Возвращаем объект пользователя
        return user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Фотографии пользователя
        context['photos'] = self.object.photos.all()[:6]

        # Статистика загруженных фотографий
        user_photos = self.object.photos.all()

        # Всего фотографий загружено
        context['total_photos_uploaded'] = user_photos.count()

        # Фотографии, загруженные в текущую неделю
        start_of_week = timezone.now().date() - timezone.timedelta(days=timezone.now().weekday())
        end_of_week = start_of_week + timezone.timedelta(days=6)
        context['photos_uploaded_this_week'] = user_photos.filter(upload_date__range=[start_of_week, end_of_week]).count()

        # Фотографии, загруженные в текущем месяце
        start_of_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_of_month = start_of_month + timezone.timedelta(days=32)  # Примерное число дней в месяце
        context['photos_uploaded_this_month'] = user_photos.filter(upload_date__range=[start_of_month, end_of_month]).count()

        # Фотографии, загруженные в текущем году
        start_of_year = timezone.now().replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end_of_year = start_of_year + timezone.timedelta(days=366)  # Учет високосных годов
        context['photos_uploaded_this_year'] = user_photos.filter(upload_date__range=[start_of_year, end_of_year]).count()

        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'authapp/profile_setup.html'

    def get_success_url(self):
        return reverse_lazy('profile', kwargs={'pk': self.request.user.profile.user.id})

    def get_object(self, queryset=None):
        return self.request.user.profile

    def form_valid(self, form):
        return super().form_valid(form)
