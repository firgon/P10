from rest_framework.serializers import ModelSerializer

from .models import Project, Issue, Comment, Contributor


class ProjectListSerializer(ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'title', 'type']


class ProjectDetailSerializer(ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'

    def create(self, validated_data):
        instance: Project = super().create(validated_data)
        user = self.context['request'].user
        instance.add_contributor(user, role=Contributor.Role.author)
        return instance


class IssueSerializer(ModelSerializer):
    class Meta:
        model = Issue
        fields = '__all__'

    def create(self, validated_data):
        validated_data['author_user'] = self.context['user']
        validated_data['assignee_user'] = self.context['user']
        validated_data['project'] = self.context['project']
        return super().create(validated_data)


class CommentSerializer(ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

    def create(self, validated_data):
        validated_data['author_user'] = self.context['user']
        validated_data['issue'] = self.context['issue']
        return super().create(validated_data)
