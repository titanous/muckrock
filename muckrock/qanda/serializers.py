"""
Serilizers for the Q&A application API
"""

from rest_framework import serializers, permissions

from muckrock.qanda.models import Question, Answer

# pylint: disable=R0903

class QuestionPermissions(permissions.DjangoModelPermissionsOrAnonReadOnly):
    """
    Allows authenticated users to submit questions
    """

    def has_permission(self, request, view):
        """Allow authenticated users to submit rquestions"""
        if request.user.is_authenticated() and request.method == 'POST':
            return True
        return super(QuestionPermissions, self).has_permission(request, view)


class AnswerSerializer(serializers.ModelSerializer):
    """Serializer for Answer model"""
    user = serializers.RelatedField()

    class Meta:
        model = Answer
        exclude = ('question',)


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for Question model"""
    user = serializers.RelatedField()
    answers = AnswerSerializer(many=True, read_only=True)
    tags = serializers.RelatedField(many=True)

    class Meta:
        model = Question
        read_only_fields = ('date', 'slug')