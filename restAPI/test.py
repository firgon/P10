from rest_framework.test import APITestCase, APIClient
from django.urls import reverse_lazy
from rest_framework import status

from .models import Project
from authentication.models import User


def format_datetime(value):
    return value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def display_request_info(func):
    def decorated(self, *args, **kwargs):
        response = func(self, args, kwargs)
        print(f"Je teste la méthode {func.__name__} "
              f"sur l'uri : {response.request['PATH_INFO']} ")
        print(response)
        return response
    return decorated


class APIClientForSoftDesk(APIClient):

    @display_request_info
    def get(self, path, data=None, follow=False, **extra):
        return super().get(path, data=None, follow=False, **extra)

    @display_request_info
    def post(self, path, data=None, format=None, content_type=None,
             follow=False, **extra):
        return super().post(path, data=None, format=None, content_type=None,
                            follow=False, **extra)

    @display_request_info
    def delete(self, path, data=None, format=None, content_type=None,
               follow=False, **extra):
        return super().delete(path, data=None, format=None, content_type=None,
                              follow=False, **extra)

    @display_request_info
    def put(self, path, data=None, format=None, content_type=None,
            follow=False, **extra):
        return super().put(path, data=None, format=None, content_type=None,
                           follow=False, **extra)


class APITestCaseForSoftDesk(APITestCase):
    client_class = APIClientForSoftDesk


class TestProjects(APITestCaseForSoftDesk):
    """for URI 3 to 7"""

    basename_url = "projects"

    project_to_create = {"title": "Titre",
                         "description": "Ceci est une description",
                         "type": Project.Type.ANDROID}

    def test_list(self):
        url = reverse_lazy(self.basename_url + '-list')

        project = Project.objects.create(**self.project_to_create)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = [
            {
                'id': project.pk,
                'title': project.title
            }
        ]
        self.assertEqual(expected, response.json()['results'])

    def test_create(self):
        url = reverse_lazy(self.basename_url + '-list')

        # check that there is no object
        self.assertFalse(Project.objects.exists())

        response = self.client.post(url, data=self.project_to_create)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # check that there is one object
        self.assertTrue(Project.objects.exists())

    def test_detail(self):
        """test CREATE, UPDATE and DELETE"""
        url = reverse_lazy(self.basename_url + '-detail',
                           kwargs={'pk': 1})

        project = Project.objects.create(**self.project_to_create)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected = {
            'id': project.pk,
            'title': project.title,
            'description': project.description,
            'type': str(project.type),
            'contributors': []
        }

        self.assertEqual(expected, response.json())

        response = self.client.put(url, data={"title": "Nouveau titre"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected["title"] = "Nouveau titre"

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(expected, response.json())


class TestUser(APITestCase):
    """for URI 8 to 10"""
    basename = 'users-from-project'

    user_to_create = {"first_name": "Emmanuel",
                      "last_name": "Albisser",
                      "email": "toto@gmail.com",
                      "password": "test"}

    def test(self):
        def user_count() -> int:
            users = User.objects.filter(project=1)
            return len(users)

        # create one project
        test_project = TestProjects()
        test_project.client = self.client
        test_project.test_create()

        # create one User
        user = User.objects.create_user(**self.user_to_create)

        # It should have at least 1 project
        self.assertTrue(Project.objects.exists())

        # it should have no user on the project
        self.assertEqual(user_count(), 0)

        url = reverse_lazy(self.basename,
                           kwargs={'project_id': 1})

        # test adding one user
        response = self.client.post(url, data={'user_id': 1})

        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg="La requête post n'a pas été bien reçue.")

        self.assertEqual(user_count(), 1, msg="Il y n'a pas de contributeur "
                                              "associé à ce projet")

        # test getting the list of contributors of one project
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.json(), [{
            'first_name': user.first_name,
            'last_name': user.last_name,
            'id': user.id
        }])
