import json
from django.shortcuts import get_object_or_404
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from authentication.models import User
from authentication.serializers import UserSerializer
from restAPI.models import Project, Issue, Comment
from restAPI.serializers import ProjectListSerializer, \
    ProjectDetailSerializer, IssueSerializer, \
    CommentSerializer
from .generics_views import ManagingGenericAPIViewForSoftDesk, \
    AccessGenericAPIViewForSoftDesk


class ProjectViewSet(ModelViewSet):
    serializer_class = ProjectListSerializer
    detail_serializer_class = ProjectDetailSerializer

    def get_queryset(self):
        queryset = Project.objects.all()

        # if we have a user, we filter queryset
        if user := self.request.user:
            queryset = queryset.filter(contributors=user)
            # print(f'Nous accueillons {user.email}')
        #
        # else:
        #     print(f'Utilisateur inconnu')

        return queryset

    def get_serializer_class(self):
        # return detail serializer if detail asked
        if self.action == 'retrieve':
            return self.detail_serializer_class
        else:
            return super().get_serializer_class()


class UsersFromProjectAPIView(AccessGenericAPIViewForSoftDesk):
    """This class gives actions POST and GET on '/projects/{id}/users/urls"""
    serializer = UserSerializer
    model_class = User

    # def get(self, *args, **kwargs):
    #     """with a get give all user from a project"""
    #     project_id = kwargs.get('project_id', None)
    #     queryset = User.objects.filter(project=project_id)
    #     serializer = self.serializer(queryset, many=True)
    #     return Response(serializer.data)

    def post(self, *args, **kwargs):
        """with a post, add a user in a project
        Response can be :
        HTTP_200_OK : user added
        HTTP_400_BAD_REQUEST : user_id is missing
        HTTP_404_NOT_FOUND : user_to_add haven't been found
        HTTP_304_NOT_MODIFIED : user had not been added"""
        user_id = self.request.POST.get('user_id', None)
        # if user_id is not defined => error 400
        if user_id is None:
            return Response({'You should give an user_id'},
                            status=status.HTTP_400_BAD_REQUEST)

        user_to_add = get_object_or_404(User, id=user_id)

        if self.project.add_contributor(user_to_add):
            return Response(f'{user_to_add.username} '
                            f'have been added to '
                            f'{self.project.title}',
                            status=status.HTTP_200_OK)
        else:
            # probably because user_to_add was already a contributor
            return Response(f'Nothing has changed, {user_to_add.username} was '
                            f'probably already a contributor '
                            f'to {self.project.title}',
                            status=status.HTTP_304_NOT_MODIFIED)


class ManageUserFromProjectAPIView(ManagingGenericAPIViewForSoftDesk):
    """a class to delete a user with project-id and user-id in the slug"""

    def delete(self, *args, **kwargs):
        """with a delete, remove a user from a project
        Response can be :
        HTTP_200_OK : deletion done
        HTTP_304_NOT_MODIFIED : user was not a contributor
        """
        # if deletion have been done
        if self.project.delete_contributor(self.user_to_add_or_delete):
            return Response(f'{self.user_to_add_or_delete} '
                            f'have been removed from '
                            f'{self.project}',
                            status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_304_NOT_MODIFIED)


class IssuesFromProjectAPIView(AccessGenericAPIViewForSoftDesk):
    """GenericAPIViewForSoftDesk class listing Issue from a project with GET
    or adding a Issue to a Project with POST"""
    serializer = IssueSerializer
    model_class = Issue


class ManageIssuesFromProjectAPIView(ManagingGenericAPIViewForSoftDesk):
    serializer = IssueSerializer
    model_class = Issue

    def put(self, *args, **kwargs):
        """with a correct PUT request, modify an existing project
        """
        serializer = self.serializer(data=self.request.data)


class CommentsFromIssueFromProjectAPIView(AccessGenericAPIViewForSoftDesk):
    serializer = CommentSerializer
    model_class = Comment


class ManageCommentsFromIssueFromProjectAPIView(
                                        ManagingGenericAPIViewForSoftDesk):
    serializer = CommentSerializer
    model_class = Comment

    def get(self, *args, **kwargs):
        """give data on 1 comment corresponding to id furnished"""
        serializer = self.serializer(self.comment)
        return Response(serializer.data)
