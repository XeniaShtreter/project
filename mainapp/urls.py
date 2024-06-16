from django.urls import path

from .views import HomeView, AboutView, PhotoDetailView, PhotoListView, ModerateView, \
    DisapprovePhotoView, ApprovePhotoView, \
    PhotoDeleteView, PhotoEditView, PhotoUploadView, SearchResultsView, AuthorPhotosView, UserPhotosView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('about/', AboutView.as_view(), name='about'),

    path('tag/<str:tag_name>/', PhotoListView.as_view(), name='photo_list'),

    path('photo/<int:pk>/', PhotoDetailView.as_view(), name='photo_detail'),
    path('upload/', PhotoUploadView.as_view(), name='photo_upload'),
    path('photo/<int:photo_id>/edit/', PhotoEditView.as_view(), name='photo_edit'),
    path('delete/<int:pk>/', PhotoDeleteView.as_view(), name='photo_delete'),

    path('moderate/', ModerateView.as_view(), name='uploaded_photos'),
    path('approve/<int:photo_id>/', ApprovePhotoView.as_view(), name='approve_photo'),
    path('disapprove/<int:photo_id>/', DisapprovePhotoView.as_view(), name='disapprove_photo'),

    path('user/photos/', UserPhotosView.as_view(), name='user_photos'),


    path('photos/', PhotoListView.as_view(), name='photo_list'),
    path('photos/author/<str:author_name>/', AuthorPhotosView.as_view(), name='author_photos'),
    path('search/', SearchResultsView.as_view(), name='search'),
]
