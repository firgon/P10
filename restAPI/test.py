from django.urls import reverse_lazy
from rest_framework import status
from rest_framework.test import APITestCase

from authentication.models import User
from .models import Project, Issue, Comment


def format_datetime(value):
    return value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


class InitializeServer:
    user_to_create = {"first_name": "Emmanuel",
                      "last_name": "Albisser",
                      "email": "toto@gmail.com",
                      "password": "test"}

    other_user = {"first_name": "test",
                      "last_name": "test",
                      "email": "test@gmail.com",
                      "password": "test"}

    project_to_create = {"title": "Titre",
                         "description": "Ceci est une description",
                         "type": Project.Type.ANDROID}

    issue_to_create = {"title": "Voici mon problème",
                       "desc": "Impossible de se connecter",
                       "tag": Issue.Type.BUG,
                       "priority": Issue.Priority.ELEVEE}

    issue_to_modify = {"title": "NOUVEAU TITRE",
                       "desc": "Impossible de se connecter",
                       "tag": Issue.Type.BUG,
                       "priority": Issue.Priority.ELEVEE}

    comment_to_create = {
        "description": "Je trouve ça pas bien"
    }

    comment_to_modify = {
        "description": "En fait, si, c'est pas mal"
    }

    def __init__(self, client):
        self.user = self.create_user(self.user_to_create)
        self.user2 = self.create_user(self.other_user)
        self.project = self.create_project(self.user)
        self.issue = self.create_issue(self.project, self.user)
        self.comment = self.create_comment(self.issue, self.user)
        self.client = client

        self.client.force_authenticate(user=self.user)

    @staticmethod
    def issue_count() -> int:
        issues = Issue.objects.filter(project=1)
        return len(issues)

    @staticmethod
    def comment_count() -> int:
        comments = Comment.objects.filter(issue=1)
        return len(comments)

    @classmethod
    def create_user(cls, user) -> User:
        return User.objects.create_user(**user)

    @classmethod
    def create_project(cls, user=None) -> Project:
        project = Project.objects.create(**cls.project_to_create)
        if user is not None:
            project.add_contributor(user)
        return project

    @classmethod
    def create_issue(cls, project=None, user=None) -> Issue:
        issue = Issue.objects.create(**cls.issue_to_create,
                                     project_id=project.id,
                                     author_user=user,
                                     assignee_user=user)

        return issue

    @classmethod
    def create_comment(cls, issue, user) -> Comment:
        comment = Comment.objects.create(**cls.comment_to_create,
                                         author_user=user,
                                         issue=issue)
        return comment


class TestProjects(APITestCase):
    """for URI 3 to 7"""
    basename_url = "projects"

    def test_list(self):
        """Test LIST projects URI 3"""
        db = InitializeServer(self.client)
        project = db.project

        url = reverse_lazy(self.basename_url + '-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = [
            {
                'id': project.pk,
                'title': project.title,
                'type': project.type
            }
        ]
        self.assertEqual(expected, response.json()['results'])

    def test_create(self):
        """test CREATE a project URI 4"""
        url = reverse_lazy(self.basename_url + '-list')

        db = InitializeServer(self.client)
        db.project.delete()

        # check that there is no object
        self.assertFalse(Project.objects.exists())

        response = self.client.post(url,
                                    data=InitializeServer.project_to_create)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # check that there is one object
        self.assertTrue(Project.objects.exists())

        project = Project.objects.get(id=2)
        expected_project = InitializeServer.project_to_create

        self.assertEqual(project.type, expected_project['type'])
        self.assertEqual(project.title, expected_project['title'])
        self.assertEqual(project.description, expected_project['description'])

    def test_detail(self):
        """test READ, UPDATE and DELETE URIs 5 to 7"""
        url = reverse_lazy(self.basename_url + '-detail',
                           kwargs={'pk': 1})

        db = InitializeServer(self.client)

        project = db.project

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected = {
            'id': project.pk,
            'title': project.title,
            'issues': [1],
            'description': project.description,
            'type': str(project.type),
            'contributors': [1]
        }

        self.assertEqual(expected, response.json())

        response = self.client.put(url, data={"title": "Nouveau titre",
                                              "type": project.type,
                                              "description":
                                                  project.description})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected["title"] = "Nouveau titre"

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(expected, response.json())


class TestUser(APITestCase):
    """for URI 8 to 10"""

    def test(self):
        """test inline URIs 8 to 10"""

        def user_count() -> int:
            users = User.objects.filter(project=1)
            return len(users)

        # initialize db
        db = InitializeServer(self.client)

        # it should have no user on the project
        self.assertEqual(user_count(), 1)

        # test removing one user
        url = reverse_lazy('delete-user-from-project',
                           kwargs={'project_id': 1, 'user_id': 1})

        response = self.client.delete(url)

        self.assertEqual(user_count(), 0)

        # test adding one user
        url = reverse_lazy('users-from-project',
                           kwargs={'project_id': 1})

        response = self.client.post(url, data={'user_id': 1})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(user_count(), 1)

        # test getting the list of contributors of one project
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.json(), [{
            'first_name': db.user.first_name,
            'last_name': db.user.last_name
        }])


class TestIssue(APITestCase):
    """Class to test all Issue related URIs (from 11 to 14)"""

    def test_get(self):
        """GET Issue List (URI 11)"""
        db = InitializeServer(self.client)

        url = reverse_lazy('issues-from-project',
                           kwargs={'project_id': 1})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = {
            'assignee_user': db.issue.assignee_user.id,
            'author_user': db.issue.author_user.id,
            'created_time': format_datetime(db.issue.created_time),
            'desc': db.issue.desc,
            'id': 1,
            'priority': db.issue.priority.value,
            'project': 1,
            'status': db.issue.status.value,
            'tag': db.issue.tag.value,
            'title': db.issue.title
        }

        self.assertEqual(response.json(), [expected])

    def test_post(self):
        """POST Issue List (URI 12)"""

        db = InitializeServer(self.client)

        url = reverse_lazy('issues-from-project',
                           kwargs={'project_id': 1})

        self.assertEqual(db.issue_count(), 1)

        response = self.client.post(url, data=InitializeServer.issue_to_create)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        issue = Issue.objects.get(id=2)

        self.assertEqual(issue.title,
                         InitializeServer.issue_to_create['title'])

        self.assertEqual(db.issue_count(), 2)

    def test_delete(self):
        """test DELETE on URI 14"""
        db = InitializeServer(self.client)

        self.assertEqual(db.issue_count(), 1)

        url = reverse_lazy('issue-from-project',
                           kwargs={'project_id': 1,
                                   'issue_id': 1})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(db.issue_count(), 0)

    def test_put(self):
        """test PUT on URI 13"""
        db = InitializeServer(self.client)

        issue = Issue.objects.get(id=1)

        self.assertEqual(issue.title,
                         InitializeServer.issue_to_create['title'])

        url = reverse_lazy('issue-from-project',
                           kwargs={'project_id': 1,
                                   'issue_id': 1})

        response = self.client.put(url, data=db.issue_to_modify)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        issue = Issue.objects.get(id=1)

        self.assertEqual(issue.title,
                         InitializeServer.issue_to_modify['title'])


class TestComment(APITestCase):
    """Class to test all Comment related URIs (from 15 to 20)"""

    def test_get_on_list(self):
        """GET Comment List (URI 16)"""
        db = InitializeServer(self.client)

        url = reverse_lazy('comments-from-issues-from-project',
                           kwargs={'project_id': 1,
                                   'issue_id': 1})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = {
            "id": 1,
            "description": db.comment.description,
            "author_user": db.comment.author_user.id,
            "created_time": format_datetime(db.comment.created_time),
            "issue": db.comment.issue.id
        }

        self.assertEqual(response.json(), [expected])

    def test_post(self):
        """POST Comment List (URI 15)"""

        db = InitializeServer(self.client)

        url = reverse_lazy('comments-from-issues-from-project',
                           kwargs={'project_id': 1,
                                   'issue_id': 1})

        self.assertEqual(db.comment_count(), 1)

        response = self.client.post(url,
                                    data=InitializeServer.comment_to_create)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        comment = Comment.objects.get(id=2)

        self.assertEqual(comment.description,
                         InitializeServer.comment_to_create['description'])

        self.assertEqual(db.comment_count(), 2)

    def test_delete(self):
        """test DELETE COMMENT on URI 18"""
        db = InitializeServer(self.client)

        self.assertEqual(db.comment_count(), 1)

        url = reverse_lazy('comment-from-issues-from-project',
                           kwargs={'project_id': 1,
                                   'issue_id': 1,
                                   'comment_id': 1})

        self.assertEqual(db.comment.author_user, db.user)

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(db.comment_count(), 0)

    def test_put(self):
        """test PUT on URI 17"""
        db = InitializeServer(self.client)

        comment = Comment.objects.get(id=1)

        self.assertEqual(comment.description,
                         InitializeServer.comment_to_create['description'])

        url = reverse_lazy('comment-from-issues-from-project',
                           kwargs={'project_id': 1,
                                   'issue_id': 1,
                                   'comment_id': 1})

        response = self.client.put(url, data=db.comment_to_modify)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        comment = Comment.objects.get(id=1)

        self.assertEqual(comment.description,
                         InitializeServer.comment_to_modify['description'])

    def test_get(self):
        """test PUT on URI 19"""
        db = InitializeServer(self.client)

        url = reverse_lazy('comment-from-issues-from-project',
                           kwargs={'project_id': 1,
                                   'issue_id': 1,
                                   'comment_id': 1})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected = {
            "id": db.comment.id,
            "description": db.comment.description,
            "created_time": format_datetime(db.comment.created_time),
            "author_user": db.comment.author_user.id,
            "issue": db.comment.issue.id
        }
        self.assertEqual(response.json(),
                         expected)





