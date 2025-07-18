import json
import random
import time

from agora_token_builder import RtcTokenBuilder
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .models import RoomMember

# Create your views here.


def lobby(request):
    return render(request, "videochat/lobby.html")


def room(request):
    return render(request, "videochat/room.html")


import os


def getToken(request):
    appId = os.environ.get("AGORA_APP_ID")
    appCertificate = os.environ.get("AGORA_APP_CERTIFICATE")
    channelName = request.GET.get("channel")
    uid = random.randint(1, 230)
    expirationTimeInSeconds = 3600
    currentTimeStamp = int(time.time())
    privilegeExpiredTs = currentTimeStamp + expirationTimeInSeconds
    role = 1

    token = RtcTokenBuilder.buildTokenWithUid(
        appId, appCertificate, channelName, uid, role, privilegeExpiredTs
    )

    return JsonResponse({"token": token, "uid": uid}, safe=False)


@csrf_exempt
def createMember(request):
    data = json.loads(request.body)
    member, created = RoomMember.objects.get_or_create(
        name=data["name"], uid=data["UID"], room_name=data["room_name"]
    )

    return JsonResponse({"name": data["name"]}, safe=False)


def getMember(request):
    uid = request.GET.get("UID")
    room_name = request.GET.get("room_name")

    member = RoomMember.objects.get(
        uid=uid,
        room_name=room_name,
    )
    name = member.name
    return JsonResponse({"name": member.name}, safe=False)


@csrf_exempt
def deleteMember(request):
    data = json.loads(request.body)
    member = RoomMember.objects.get(name=data["name"], uid=data["UID"], room_name=data["room_name"])
    member.delete()
    return JsonResponse("Member deleted", safe=False)
