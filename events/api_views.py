from django.http import JsonResponse
import json
from common.json import ModelEncoder
from .models import Conference, Location, State
from django.views.decorators.http import require_http_methods
from .acls import get_photo, get_weather_data

class LocationListEncoder(ModelEncoder):
    model = Location
    properties = ["name"]

class LocationDetailEncoder(ModelEncoder):
    model = Location
    properties = [
        "name",
        "city",
        "room_count",
        "created",
        "updated",
        "picture_url",
    ]

    def get_extra_data(self, o):
        return { "state": o.state.abbreviation }

class ConferenceDetailEncoder(ModelEncoder):
    model = Conference
    properties = [
        "name",
        "description",
        "max_presentations",
        "max_attendees",
        "starts",
        "ends",
        "created",
        "updated",
        "location",
    ]
    encoders = {"location": LocationListEncoder(),}

class ConferenceListEncoder(ModelEncoder):
    model = Conference
    properties = ["name"]

@require_http_methods(["GET", "POST"])
def api_list_conferences(request):
    if request.method == "GET":
        conferences = Conference.objects.all()
        return JsonResponse({"conferences": conferences}, 
        encoder=ConferenceListEncoder, safe= False)
    else:
        content = json.loads(request.body)
        try:
            location=Location.objects.get(id=content["location"])
            content["location"] = location
        except Location.DoesNotExist:
            return JsonResponse({"message" : "Invalid locationid"},status=400,)
        conference = Conference.objects.create(**content)
        return JsonResponse(conference, encoder=ConferenceDetailEncoder, safe=False,)

@require_http_methods(["DELETE", "GET", "PUT"])
def api_show_conference(request, pk):
    if request.method == "GET":
        conference = Conference.objects.get(id=pk)
        # Use the city and state's abbreviation in the content dictionary
        # to call the get_photo ACL function

        # Use the returned dictionary to update the content dictionary
        location = conference.location
        weather = get_weather_data(city=location.city, state=location.state)
        return JsonResponse({"weather": weather, "conference": conference}, 
        encoder=ConferenceDetailEncoder, safe=False
        )
        
    elif request.method == "DELETE":
        count, _= Conference.objects.filter(id=pk).delete()
        return JsonResponse({"delete": count>0})
    else:
        content = json.loads(request.body)
        Conference.objects.filter(id=pk).update(**content)
        conference = Conference.objects.get(id=pk)
        return JsonResponse(
            conference, encoder=ConferenceDetailEncoder, safe=False
        )

@require_http_methods(["GET", "POST"])
def api_list_locations(request):
    if request.method == "GET":
        locations = Location.objects.all()
        return JsonResponse({"locations": locations}, encoder= LocationListEncoder, safe=False)
    else: 
        content = json.loads(request.body)
        try:
            state = State.objects.get(abbreviation=content["state"])
            content["state"] = state
        except State.DoesNotExist:
            return JsonResponse({"message" : "Invalid state abbreviation"}, status=400,)
        # Use the city and state's abbreviation in the content dictionary
        # to call the get_photo ACL function

        # Use the returned dictionary to update the content dictionary
        picture_url = get_photo(city =content["city"], state= state)
        content["picture_url"] = picture_url

        location = Location.objects.create(**content)
        return JsonResponse(location, encoder=LocationDetailEncoder, safe=False)

@require_http_methods(["DELETE", "GET", "PUT"])
def api_show_location(request, pk):
    if request.method == "GET":
        location= Location.objects.get(id=pk)
        return JsonResponse(
            location, encoder= LocationDetailEncoder, safe= False,
            )
    elif request.method == "DELETE":
        count, _= Location.objects.filter(id=pk).delete()
        return JsonResponse({"delete": count>0})
    else:
        content = json.loads(request.body)
        try:
            if "state" in content:
                state=State.objects.get(abbreviation=content["state"])
                content["state"] = state
        except State.DoesNotExist:
            return JsonResponse({"message":"Invalid state abbreviation"}, status=400,)
        
        Location.objects.filter(id=pk).update(**content)
        location = Location.objects.get(id=pk)
        return JsonResponse(
            location,
            encoder=LocationDetailEncoder,
            safe=False,
        )
