from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('rem-upc/', views.remupc_view, name="rem-upc"),
    path('download/', views.download_files, name='download'),

]
