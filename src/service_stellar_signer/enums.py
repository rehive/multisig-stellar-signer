from enumfields.enums import Enum

class TransactionStatus(Enum):
    UNSIGNED = 'unsigned'
    SIGNED = 'signed'
    REJECTED = 'rejected'

class KeypairType(Enum):
    ENCRYPTED_KEY = 'encrypted key'
    KMS_KEY = 'kms key'