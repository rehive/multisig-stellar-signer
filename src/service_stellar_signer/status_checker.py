from service_stellar_signer.models import Keypair, Transaction, Wallet, APIUser, Configuration

class StatusChecker(object):
    """
    Class for running status check functions either for display on the status page or for internal debugging
    """

    def return_full_diagnostic_dict(self):
        # False is assumed as check rely on the previous ones to succeed
        diag = {
            "is_user_created": False,
            "is_wallet_created": False,
            "is_a_backup_key_configured": False,
            "is_the_keypair_created": False,
            "wallet_status": None,
            "is_the_keypair_accessable": False
        }

        diag['is_user_created'] = self.is_user_created()
        if not diag['is_user_created']:
            return diag
        
        diag['is_wallet_created'] = self.is_wallet_created()
        if not diag['is_wallet_created']:
            return diag
        
        diag['is_a_backup_key_configured'] = self.is_a_backup_key_configured()
        diag['wallet_status'] = self.get_wallet_status()
        diag['is_the_keypair_created'] = self.is_the_keypair_created()
        if not diag['is_the_keypair_created']:
            return diag
        diag['is_the_keypair_accessable'] = self.is_the_keypair_accessable()
        return diag


    def is_user_created(self):
        # For now this assume a single user setup
        try:
            APIUser.objects.first()
            return True
        except APIUser.DoesNotExist:
            return False
    
    def is_wallet_created(self):
        try:
            Wallet.objects.first()
            return True
        except APIUser.DoesNotExist:
            return False

    def is_a_backup_key_configured(self):
        config = Configuration.objects.first()
        if config.backup_public_key:
            return True
        else:
            return False

    def is_the_keypair_created(self):
        try:
            Keypair.objects.first()
            return True
        except Keypair.DoesNotExist:
            return False

    def get_wallet_status(self):
        # Returns a dict containing info on the status of different wallet fields
        wallet = Wallet.objects.first()
        return {
            "setup": wallet.setup,
            "block_transactions": wallet.block_transactions,
            "external_public_key": True if wallet.external_public_key else False,
            "backup_public_key": True if wallet.backup_public_key else False,
            "keypair": True if wallet.keypair else False
        }

    def is_the_keypair_accessable(self):
        keypair = Keypair.objects.first()

        try:
            keypair.private_key
            return True
        except Exception as exc:
            return False
