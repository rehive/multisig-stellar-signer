import os
from stellar_sdk.exceptions import NotFoundError, BaseHorizonError
from stellar_sdk import TransactionBuilder, Server, Network, Keypair, Signer, TransactionEnvelope
from config import settings


class HorizonWrapper(object):
    """
    Wrapper class for common horizon calls and horizon custom error handling
    """

    def __init__(self):
        self.network = os.environ.get('STELLAR_NETWORK')
        if self.network == 'TESTNET':
            self.horizon = Server(horizon_url="https://horizon-testnet.stellar.org")
        else:
            self.horizon = Server(horizon_url="https://horizon.stellar.org")

    def get_transaction(self, tx_id):
        return self.horizon.transactions().transaction(tx_id).call()

    def get_account(self, address):
        return self.horizon.accounts().account_id(address).call()

    def submit_transaction(self, tx):
        return self.horizon.submit_transaction(tx)

    def load_account(self, account_address):
        return self.horizon.load_account(account_address)


class WalletAPI():

    def __init__(self, private_key, public_key=None, *args, **kwargs):
        self.network = os.environ.get('STELLAR_NETWORK')
        if self.network == 'TESTNET':
            self.network_passphrase = Network.TESTNET_NETWORK_PASSPHRASE
        else:
            self.network_passphrase = Network.PUBLIC_NETWORK_PASSPHRASE
        self.horizon_api = HorizonWrapper()
        if private_key:
            keypair = Keypair.from_secret(private_key)
            # Create an Account object from an address and sequence number.
            self.address = self.horizon_api.load_account(keypair.public_key)
            self.signer_account = keypair
            self.builder = TransactionBuilder(
                source_account=self.address,
                network_passphrase=self.network_passphrase,
            )
        elif public_key:
            self.address = self.horizon_api.load_account(public_key)
        else:
            raise Exception('A valid private or public key is required')

    def sign_raw(self, raw_tx):
        transaction = TransactionEnvelope.from_xdr(raw_tx, network_passphrase=self.network_passphrase)
        transaction.sign(self.signer_account)
        return transaction.to_xdr()

    def setup_two_of_three_multisig(self, signer_1, signer_2):
        sign_1 = Signer.ed25519_public_key(account_id=signer_1, weight=1)
        sign_2 = Signer.ed25519_public_key(account_id=signer_2, weight=1)
        self.builder.append_set_options_op(
            master_weight=1,
            signer=sign_1,
            low_threshold=1,
            med_threshold=2,
            high_threshold=2
        )
        self.builder.append_set_options_op(
            signer=sign_2
        )
        transaction_env = self.builder.build()
        transaction_env.sign(self.signer_account)
        res = self.horizon_api.submit_transaction(transaction_env)