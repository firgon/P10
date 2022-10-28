"""softDesk URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views \
    import TokenObtainPairView, TokenRefreshView, TokenBlacklistView

from authentication.views import RegisterView
from restAPI.views.views import ProjectViewSet, \
    UsersFromProjectAPIView, \
    ManageUserFromProjectAPIView, \
    IssuesFromProjectAPIView, ManageIssuesFromProjectAPIView, \
    CommentsFromIssueFromProjectAPIView, \
    ManageCommentsFromIssueFromProjectAPIView

# create a router to handle classical uri as projects/ or projects/{id}/
router = routers.SimpleRouter()
router.register('projects', ProjectViewSet, basename='projects')

urlpatterns = [
    path('admin/', admin.site.urls),

    # path('api-auth/', include('rest_framework.urls')),

    path('signup/', RegisterView.as_view(), name='signup'),
    path('login/',
         TokenObtainPairView.as_view(),
         name='login'),
    # path('login/refresh/',
    #      TokenRefreshView.as_view(),
    #      name='token_refresh'),
    path('logout/',
         TokenBlacklistView.as_view(),
         name='logout'),

    # router for projects views (URI from 3 to 7)
    path('', include(router.urls)),

    # Users views (URI from 8 to 11)
    path('projects/<int:project_id>/users/',
         UsersFromProjectAPIView.as_view(),
         name='users-from-project'),
    path('projects/<int:project_id>/users/<int:user_id>',
         ManageUserFromProjectAPIView.as_view(),
         name='delete-user-from-project'),

    # Issues views (URI 11 to 14)
    path('projects/<int:project_id>/issues/',
         IssuesFromProjectAPIView.as_view(),
         name='issues-from-project'),
    path('projects/<int:project_id>/issues/<int:issue_id>',
         ManageIssuesFromProjectAPIView.as_view(),
         name='issue-from-project'),

    # Comment views (URI 15 to 19)
    path('projects/<int:project_id>/issues/<int:issue_id>/comments/',
         CommentsFromIssueFromProjectAPIView.as_view(),
         name='comments-from-issues-from-project'),
    path('projects/<int:project_id>/issues/'
         '<int:issue_id>/comments/<int:comment_id>',
         ManageCommentsFromIssueFromProjectAPIView.as_view(),
         name='comment-from-issues-from-project'),

]
