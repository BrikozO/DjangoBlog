from django.urls import path, re_path, include
from rest_framework.authtoken import views

from .views import PostList, PostDetail
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('<int:pk>', PostDetail.as_view(), name='post_detail'),
    path('', PostList.as_view(), name='post_list'),
    # re_path('^user/(?P<username>.+)/$', UserPostList.as_view()),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger_ui'),
    path('api-auth/', include('rest_framework.urls')),
    path('api-token-auth/', views.obtain_auth_token),
]
