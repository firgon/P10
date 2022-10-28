from django.db import models
from softDesk import settings
from authentication.models import User


class Contributor(models.Model):
    """Class to make links between users and project,
    Users can have several roles : Author (only one) or Contributor
    Author can delete a project
    Contributors can modify a project"""

    class Role(models.TextChoices):
        author = "Auteur"
        contributor = "Contributeur"

    user = models.ForeignKey(to=settings.AUTH_USER_MODEL,
                             # TODO use special method
                             #  to handle when author is delete
                             on_delete=models.CASCADE,
                             related_name="contribute_to")

    project = models.ForeignKey(to='Project',
                                on_delete=models.CASCADE,
                                related_name='contributed_by')
    role = models.CharField(
        choices=Role.choices,
        verbose_name="Rôle",
        max_length=128
    )
    objects = models.Manager()  # Only useful for pycharm developing

    class Meta:
        unique_together = ['user', 'project']

    def __str__(self):
        return f"{self.user} est {self.role} dans {self.project}"


class Project(models.Model):
    """Class that groups several Issues"""

    class Type(models.TextChoices):
        BACK_END = "Back-end"
        FRONT_END = "Front-end"
        IOS = "IOS"
        ANDROID = "Android"

    title = models.CharField(
        max_length=128,
        verbose_name="Titre",
        blank=False,
        null=False
    )
    description = models.CharField(
        max_length=2048,
        verbose_name="Description"
    )
    type = models.CharField(
        choices=Type.choices,
        max_length=128
    )
    contributors = models.ManyToManyField(
        to=settings.AUTH_USER_MODEL,
        through=Contributor
    )
    objects = models.Manager()  # Only useful for pycharm developing

    def __str__(self):
        return f'{self.title}'

    def add_contributor(self,
                        user: User,
                        role=Contributor.Role.contributor) -> bool:
        # check if user is not already a contributor
        if not Contributor.objects.filter(user=user, project=self).exists():
            contributor = Contributor()
            contributor.user = user
            contributor.project = self
            contributor.role = role
            contributor.save()
            return True
        else:
            return False

    def delete_contributor(self,
                           user: User) -> bool:
        contributor = Contributor.objects.filter(user=user, project=self)
        if contributor.exists():
            contributor.delete()
            return True
        else:
            return False


class Issue(models.Model):
    """Class to document a part of a project,
    it has a Priority (from 1 low, to 3 high) and
    a type BUG, TASK or IMPROVEMENT
    It has an Author, the user who has created the Issue, and
    an Assignee, the user who is in charge of handling this Issue"""

    class Priority(models.IntegerChoices):
        FAIBLE = 1
        MOYENNE = 2
        ELEVEE = 3

    class Type(models.IntegerChoices):
        BUG = 3
        TASK = 2
        IMPROVEMENT = 1

    class Status(models.IntegerChoices):
        TODO = 1
        ON_GOING = 2
        DONE = 3

    title = models.CharField(max_length=128, verbose_name="Titre")
    desc = models.CharField(max_length=2048, verbose_name="Description")
    tag = models.IntegerField(choices=Type.choices)
    priority = models.IntegerField(choices=Priority.choices)
    project = models.ForeignKey(to=Project, related_name="issues",
                                on_delete=models.CASCADE
                                )
    status = models.IntegerField(choices=Status.choices, default=Status.TODO)
    author_user = models.ForeignKey(to=settings.AUTH_USER_MODEL,
                                    # TODO Decide
                                    on_delete=models.DO_NOTHING,
                                    related_name="created_by"
                                    )
    assignee_user = models.ForeignKey(to=settings.AUTH_USER_MODEL,
                                      # TODO Decide
                                      on_delete=models.DO_NOTHING,
                                      related_name="handled_by"
                                      )
    created_time = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()  # Only useful for pycharm developing

    def __str__(self):
        return f'{self.title}'


class Comment(models.Model):
    """Comment are created by users to comment Issues,
    one issue can have several comments"""
    description = models.CharField(max_length=2048, verbose_name="Description")
    author_user = models.ForeignKey(to=settings.AUTH_USER_MODEL,
                                    on_delete=models.CASCADE)
    issue = models.ForeignKey(to=Issue, on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()  # Only useful for pycharm developing

    def __str__(self):
        return f'Comment n°{self.id}'
