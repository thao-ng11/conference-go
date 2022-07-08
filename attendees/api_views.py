from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Attendee
from events.models import Conference
import json
from common.json import ModelEncoder

class AttendeeListEncoder(ModelEncoder):
    model = Attendee
    properties = ["name"]


class AttendeeDetailEncoder(ModelEncoder):
    model = Attendee
    properties = [
        "email",
        "name",
        "company_name",
        "created",
    ]

@require_http_methods(["GET", "POST"])
def api_list_attendees(request, conference_id):
    
    if request.method =="GET":
        attendees = Attendee.objects.filter(conference=conference_id)
        return JsonResponse(
            {"attendees": attendees},
            encoder=AttendeeListEncoder,
    )
    else:
        content = json.loads(request.body)
        try:
            conference = Conference.objects.get(id=conference_id)
            content["conference"] = conference
        except Conference.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid conference id"},
                status=400,
            )

        attendee = Attendee.objects.create(**content)
        return JsonResponse(
            attendee,
            encoder=AttendeeDetailEncoder,
            safe=False,
        )

@require_http_methods(["GET", "PUT", "DELETE"])
def api_show_attendee(request, pk):
    if request.method == "GET":
        attendee = Attendee.objects.get(id=pk)
        return JsonResponse(
            attendee,
            encoder=AttendeeDetailEncoder,
            safe=False,
        )
    elif request.method == "DELETE":
        count, _= Attendee.objects.filter(id=pk).delete()
        return JsonResponse({"delete": count>0})

    else:
        content = json.loads(request.body)
        Attendee.objects.filter(id=pk).update(**content)
        attendee = Attendee.objects.get(id=pk)
        return JsonResponse(
            attendee,
            encoder=AttendeeDetailEncoder,
            safe=False,
        )