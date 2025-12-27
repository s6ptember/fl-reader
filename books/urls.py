from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('', views.library_view, name='library'),
    path('last-read/', views.last_read_view, name='last_read'),
    path('book/<uuid:book_id>/', views.book_detail_view, name='book_detail'),
    path('book/<uuid:book_id>/progress/', views.update_progress_view, name='update_progress'),
    path('search/', views.search_view, name='search'),
    path('download/', views.download_book_view, name='download'),
    path('book/<uuid:book_id>/delete/', views.delete_book_view, name='delete_book'),
    path('offline/', views.offline_view, name='offline'),
    path('sitemap.xml', views.sitemap_view, name='sitemap'),
    path('robots.txt', views.robots_view, name='robots'),
]
