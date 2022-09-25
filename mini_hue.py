import json
from os import system
import requests


class System(object):

    def __init__(self, bridge, key):

        self.bridge = bridge
        self.key = key
        self.devices = []
        self.lights = []

    def refresh(self):

        r = self.get("resource/device")
        
        for item in r["data"]:
            if item["type"] == "device":
                self.devices.append(Device(self, item))

        r = self.get("resource/light")

        for item in r["data"]:
            if item["type"] == "light":
                self.lights.append(Light(self, item))

    def get(self, api):

        url = "https://%s/clip/v2/%s" % (self.bridge, api)
        # print(url)

        response = requests.get(url, verify = False, headers = {"hue-application-key": self.key})
        # response = requests.get(url, cert="huebridge_cacert.pem", headers = {"hue-application-key": self.key})
        # print(response.status_code)
        # print(response.reason)
        # print(response.text)

        return json.loads(response.text)

    def put(self, api, data):

        url = "https://%s/clip/v2/%s" % (self.bridge, api)
        # print(url)

        response = requests.put(url, verify = False, headers = {"hue-application-key": self.key}, data = json.dumps(data))
        # response = requests.put(url, cert="huebridge_cacert.pem", headers = {"hue-application-key": self.key}, data = json.dumps(data))
        # print(response.status_code)
        # print(response.reason)
        # print(response.text)

        return json.loads(response.text)

        
    def get_light_by_name(self, name):

        for light in self.lights:
            if light.name == name:
                return light

        return None


class Hue(object):

    def __init__(self, system, data):

        self.data = data
        self.system = system
        self.id = data["id"]
        self.type = data["type"]
        self.name = data["metadata"]["name"]
        self.archetype = data["metadata"]["archetype"]


    def raw(self):
        return self.data


class Device(Hue):

    def __init__(self, system, data):
        super().__init__(system, data)
        assert self.type == "device"
        self.services = []

        for service in data["services"]:
            self.services.append(Service(service))

    def get_service(self, service):

        for item in self.services:
            if item.rtype == service:
                return item.rid

        return None


class Light(Hue):

    def __init__(self, system, data):
        super().__init__(system, data)
        assert self.type == "light"

    def on(self):

        self.system.put("resource/light/%s" % self.id, {"on" : {"on": True}})

    def off(self):

        self.system.put("resource/light/%s" % self.id, {"on" : {"on": False}})


class Service(object):

    def __init__(self, data):

        self.rid = data["rid"]
        self.rtype = data["rtype"]
