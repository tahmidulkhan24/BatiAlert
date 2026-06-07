from core.models import Appliance


def appliance_context(request):

    return {

        "appliances":
        Appliance.objects.all()

    }