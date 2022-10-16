from rest_framework.serializers import ModelSerializer

from .models import Project, Issue, Comment


class ProjectListSerializer(ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'title']


class ProjectDetailSerializer(ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class IssueSerializer(ModelSerializer):
    class Meta:
        model = Issue
        fields = '__all__'

    def create(self, validated_data):
        validated_data['author'] = self.context['user']
        validated_data['assignee'] = self.context['user']
        validated_data['project'] = self.context['project']
        return super().create(validated_data)


class CommentSerializer(ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

    def create(self, validated_data):
        validated_data['author'] = self.context['user']
        validated_data['issue'] = self.context['issue']
        return super().create(validated_data)
