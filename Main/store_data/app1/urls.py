from django.urls import path
from app1 import views

app_name="app1"
urlpatterns=[
    path("",views.get_data,name="Home"),
    path("show_db/",views.show_db,name="DB")
]