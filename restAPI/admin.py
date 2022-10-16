from django.contrib import admin
from .models import Project, Issue, Comment


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'type')


admin.site.register(Project, ProjectAdmin)
admin.site.register(Issue)
admin.site.register(Comment)

