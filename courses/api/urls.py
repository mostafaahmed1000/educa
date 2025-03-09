from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register("courses", views.CourseViewSet)
app_name = "courses"
urlpatterns = [
    path("subjects/", views.SubjectListView.as_view(), name="subject_list"),
    path("subjects/<pk>/", views.SubjectDetailView.as_view(), name="subject_detail"),
    path(
        "modules/<int:module_id>/contents/",
        views.ContentCreateView.as_view(),
        name="content_create",
    ),
    path(
        "contents/<int:pk>/",
        views.ContentDetailView.as_view(),
        name="content_detail",
    ),
    path("", include(router.urls)),
    path("login/", views.user_login, name="api_login"),
    path("signup/", views.user_signup, name="api_signup"),
]
