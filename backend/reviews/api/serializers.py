from rest_framework import serializers
from reviews.models import ProductReview


class ProductReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = ProductReview
        fields = ['id', 'product', 'user', 'username', 'full_name', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'user', 'username', 'full_name', 'created_at']

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username


class CreateReviewSerializer(serializers.Serializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)
    comment = serializers.CharField()
