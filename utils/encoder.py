import json
import entity.station as Stop
import utils.networks.node as Node
import utils.networks.edge as Edge

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "to_dict") and callable(obj.to_dict):
            return obj.to_dict()
        return super().default(obj)