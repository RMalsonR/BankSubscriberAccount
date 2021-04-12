from enum import Enum


class AccountStatusEnum(Enum):
    OPEN = 'OPEN'
    CLOSE = 'CLOSE'

    @classmethod
    def as_choices(cls):
        return (
            (cls.OPEN.value, 'Open'),
            (cls.CLOSE.value, 'Close')
        )


class BankAccountOperationsEnum(Enum):
    UNDEFINED = 'undefined'
    ADD = 'balance ADDING'
    SUB = 'balance SUBTRACT'
    STATUS = 'get account STATUS'


