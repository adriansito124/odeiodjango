from django.urls import path
from .views import index, collaborators, update_name, park

urlpatterns = [
    path('', index, name='index'),
    path('collaborators/', collaborators, name='collaborators'),
    path('park/', park, name='park'),
    path('update-name/', update_name, name='update_name'),
]
