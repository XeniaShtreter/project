from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404, render

from django.views import View
from django.views.generic import ListView, TemplateView, DetailView

from .models import Photo, Tag


class HomeView(ListView):
    model = Photo
    template_name = 'mainapp/home.html'
    context_object_name = 'photos'
    paginate_by = 12
    queryset = Photo.objects.filter(status='APPROVED')


class AboutView(TemplateView):
    template_name = 'mainapp/about.html'


class PhotoListView(ListView):
    model = Photo
    template_name = 'mainapp/home.html'
    context_object_name = 'photos'

    def get_queryset(self):
        queryset = super().get_queryset()
        tag = self.kwargs.get('tag_name')
        print(tag)
        queryset = queryset.filter(tags__name=tag, status='APPROVED')
        print(queryset)
        return queryset


class PhotoDetailView(DetailView):
    model = Photo
    template_name = 'mainapp/photo_detail.html'
    context_object_name = 'photo'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tags = self.object.tags.all()
        similar_photos = Photo.objects.filter(tags__in=tags, status='APPROVED').exclude(pk=self.object.pk).distinct()[:3]
        context['similar_photos'] = similar_photos

        return context


class PhotoDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        photo = get_object_or_404(Photo, pk=pk)
        if request.user == photo.user or request.user.is_staff:
            photo.delete()
            return redirect('home')
        else:
            return HttpResponse('You are not authorized to delete this photo.', status=403)


class PhotoEditView(View):
    template_name = 'mainapp/photo_edit.html'

    def get(self, request, photo_id):
        photo = get_object_or_404(Photo, id=photo_id)
        context = {
            'photo': photo
        }
        return render(request, self.template_name, context)

    def post(self, request, photo_id):
        photo = get_object_or_404(Photo, id=photo_id)

        photo.title = request.POST.get('title', '')
        photo.description = request.POST.get('description', '')
        tags_input = request.POST.get('tags', '')
        tags = [tag.strip() for tag in tags_input.split(' ') if tag.strip()]

        photo.tags.clear()
        for tag_name in tags:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            photo.tags.add(tag)

        if 'photo' in request.FILES:
            photo.image = request.FILES['photo']

        photo.save()
        return redirect('photo_detail', pk=photo.id)


class PhotoUploadView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        title = request.POST.get('title')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        tags_input = request.POST.get('tags', '')

        new_photo = Photo.objects.create(
            user=request.user,
            title=title,
            description=description,
            image=image
        )

        tag_names = tags_input.split()
        for tag_name in tag_names:
            tag_name = tag_name.strip()
            if tag_name:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                new_photo.tags.add(tag)

        return redirect('profile', request.user.id)


class ModerateView(ListView):
    model = Photo
    template_name = 'mainapp/moderate.html'
    context_object_name = 'photos'
    paginate_by = 12
    queryset = Photo.objects.filter(status='PENDING')


class ApprovePhotoView(LoginRequiredMixin, View):
    def post(self, request, photo_id):
        photo = get_object_or_404(Photo, id=photo_id)
        if request.user == photo.user or request.user.is_staff:
            photo.status = 'APPROVED'
            photo.save()
        return redirect('uploaded_photos')


class DisapprovePhotoView(LoginRequiredMixin, View):
    def post(self, request, photo_id):
        photo = get_object_or_404(Photo, id=photo_id)
        if request.user == photo.user or request.user.is_staff:
            photo.status = 'DISAPPROVED'
            photo.save()
        return redirect('uploaded_photos')


class UserPhotosView(ListView):
    model = Photo
    template_name = 'mainapp/user_photos.html'
    context_object_name = 'photos'

    def get_queryset(self):
        queryset = super().get_queryset().filter(user=self.request.user)
        sort = self.request.GET.get('sort')

        if sort == 'status':
            status = self.request.GET.get('status')
            if status:
                queryset = queryset.filter(status=status)  # Фильтрация по статусу модерации
        return queryset


class AuthorPhotosView(ListView):
    model = Photo
    template_name = 'mainapp/author_photos.html'
    context_object_name = 'photos'

    def get_queryset(self):
        author_name = self.kwargs['author_name']
        return Photo.objects.filter(user__username=author_name)


class SearchResultsView(ListView):
    model = Photo
    template_name = 'mainapp/search_results.html'
    context_object_name = 'photos'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Photo.objects.filter(
                Q(user__username__icontains=query) | Q(tags__name__icontains=query)
            ).distinct()
        return Photo.objects.all()