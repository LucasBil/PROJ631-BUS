import json
import entity.stop as Stop

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Stop.Stop):
            return { "name": obj.name }
        return super().default(obj)