from django.contrib import admin
from service_stellar_signer.models import *


class CustomModelAdmin(admin.ModelAdmin):
    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields]
        super(CustomModelAdmin, self).__init__(model, admin_site)


admin.site.register(APIUser)
admin.site.register(Transaction)
admin.site.register(Wallet)
