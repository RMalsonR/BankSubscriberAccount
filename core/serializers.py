from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core.enums import AccountStatusEnum
from core.models import BankAccount


# TODO: may be it's not necessary
class BankAccountForListSerializer(serializers.ModelSerializer):
    """BankAccount serializer for List representation"""
    balance = serializers.DecimalField(
        max_digits=8,
        decimal_places=2,
        read_only=True
    )

    def get_balance(self, obj):
        if obj.hold > 0:
            return obj.balance - obj.hold
        return obj.balance

    class Meta:
        model = BankAccount
        fields = ('id', 'owner_name', 'balance', 'status')


class BankAccountValidateStatusSerializer(serializers.Serializer):
    def validate(self, attrs):
        if self.instance.status == AccountStatusEnum.CLOSE.value:
            raise ValidationError("You can't do anything with this account, because its status is `CLOSE`")
        return super(BankAccountValidateStatusSerializer, self).validate(attrs)


class BankAccountForAddSerializer(BankAccountValidateStatusSerializer):
    """BankAccount serializer for `add` action."""
    add_value = serializers.DecimalField(
        max_digits=8,
        decimal_places=2,
        min_value=0.01,
        required=True,
        write_only=True,
        help_text='The value, that want to add to the balance'
    )

    def update(self, instance, validated_data):
        """Updating instance balance."""
        instance.balance += validated_data['add_value']
        instance.save()
        return instance

    def create(self, validated_data):
        """Not provided."""
        pass


class BankAccountForSubtractSerializer(BankAccountValidateStatusSerializer):
    """BankAccount serializer for `subtract` action."""
    sub_value = serializers.DecimalField(
        max_digits=8,
        decimal_places=2,
        min_value=0.01,
        required=True,
        write_only=True,
        help_text='The value, you want to subtract from the balance'
    )

    def update(self, instance, validated_data):
        """Updating instance hold."""
        instance.hold += validated_data
        instance.save()
        return instance

    def validate(self, attrs):
        attrs = super(BankAccountForSubtractSerializer, self).validate(attrs)
        if self.instance.balance < self.instance.hold + attrs['sub_value']:
            raise ValidationError("Don't have enough money for this operation")
        return attrs


class BankAccountForStatusSerializer(BankAccountForListSerializer):
    pass
