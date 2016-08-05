"""
BtleJuice Bindings exceptions
"""

class HookForceResponse(Exception):
    def __init__(self, data='', offset=0, withoutResponse=False, enabled=False):
        Exception.__init__(self)
        self.data = data
        self.offset = offset
        self.withoutResponse = withoutResponse
        self.enabled = enabled

class HookModify(Exception):
    def __init__(self, data):
        Exception.__init__(self)
        self.data = data
