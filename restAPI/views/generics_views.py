from django.db import models
from django.shortcuts import get_object_or_404
from rest_framework import status

from rest_framework.serializers import ModelSerializer
from rest_framework.views import APIView
from rest_framework.response import Response

from restAPI.models import Project, Issue, Comment

from authentication.models import User


class GenericAPIViewForSoftDesk(APIView):
    """
    Generic super class collecting data for its subclasses
    """
    # permission_classes = [permissions.IsAuthenticated]
    serializer: ModelSerializer = None
    model_class: models.Model = None
    project: Project
    issue: Issue = None
    comment: Comment = None
    user_to_add_or_delete: User = None

    def dispatch(self, request, *args, **kwargs):
        """Method to collect generics data and return ERROR 404
        if data slug are not correct"""
        project_id = kwargs.get('project_id', None)
        issue_id = kwargs.get('issue_id', None)
        comment_id = kwargs.get('comment_id', None)
        user_id = kwargs.get('user_id', None)
        # probably impossible
        # if project_id is None:
        #     response = Response({'fail': 'You should give project_id'},
        #                         status=status.HTTP_400_BAD_REQUEST)
        #     return self.answer(request, response, args, kwargs)

        # project must always been given
        self.project = get_object_or_404(Project, id=project_id)

        # other data are optional
        if issue_id is not None:
            self.issue = get_object_or_404(Issue, id=issue_id)

        if comment_id is not None:
            self.comment = get_object_or_404(Comment, id=comment_id)

        if user_id is not None:
            self.user_to_add_or_delete = get_object_or_404(User, id=user_id)

        # probably useless
        # if not self.request.user.is_authenticated:
        #     response = Response(status=status.HTTP_403_FORBIDDEN)
        #     return self.answer(request, response, args, kwargs)

        return super().dispatch(request, *args, **kwargs)


class AccessGenericAPIViewForSoftDesk(GenericAPIViewForSoftDesk):
    """This class implements generics GET method
    could implement POST method in future"""

    def get(self, *args, **kwargs):
        """give a list of instances from a class linked to a project
        can be Users, Issues..."""
        queryset = self.model_class.objects.filter(project=self.project.id)
        serializer = self.serializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, *args, **kwargs):
        """with a POST request, add a issue in a project
        Response can be :
        HTTP_200_OK : Issue added

        HTTP_400_BAD_REQUEST : project_id or user_id are missing"""
        serializer = self.serializer(data=self.request.data,
                                     context={'user': self.user,
                                              'issue': self.issue,
                                              'project': self.project})

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class ManagingGenericAPIViewForSoftDesk(GenericAPIViewForSoftDesk):
    """This class implements generics DELETE and PUT method"""

    def delete(self, *args, **kwargs):
        """with a delete, remove the element at the end of the tree
        Response can be :
        HTTP_200_OK : deletion done
        HTTP_304_NOT_MODIFIED : user was not a contributor
        """
        element_to_delete = None
        # if comment is not None, delete it
        if element_to_delete := self.comment:
            element_to_delete.delete()
        # if issue is not None, delete it
        elif element_to_delete := self.issue:
            element_to_delete.delete()
        elif element_to_delete := self.user_to_add_or_delete:
            if not self.project.delete_contributor(element_to_delete):
                return Response(f'{self.project.title} has not been modified, '
                                f'{element_to_delete.username} was '
                                f'not a contributor',
                                status=status.HTTP_304_NOT_MODIFIED)

        return Response(f'{element_to_delete} has been deleted',
                        status=status.HTTP_200_OK)
