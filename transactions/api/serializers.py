from rest_framework import serializers

from transactions.models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for the Transaction model.
    """

    candidate = serializers.PrimaryKeyRelatedField(
        queryset=Transaction._meta.get_field("candidate").related_model.objects.all(),
        allow_null=True,
        required=False,
    )

    class Meta:
        model = Transaction
        fields = [
            "id",
            "transaction_id",
            "user",
            "candidate",
            "amount",
            "payment_method",
            "status",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "transaction_id", "created_at", "updated_at"]
