"""
BtleJuice Python bindings
"""

from time import sleep
from threading import Thread

from btlejuice.socketIO_client import SocketIO, BaseNamespace
from btlejuice.socketIO_client.parsers import Buffer
from btlejuice.interface import BtleJuiceInterface, SniffingInterface, HookingInterface
from btlejuice.exceptions import HookForceResponse, HookModify
from btlejuice.utils import hexiify

class CoreNamespace(BaseNamespace):
    """
    BtleJuice Core namespace.

    This class handles all the messages sent by the remote application
    and forward them to our registered interfaces.
    """

    def __init__(self, io, path):
        self.interfaces = []
        super(CoreNamespace, self).__init__(io, path)

    def on_event(self, event, *args):
        """
        Main event dispatcher.
        """
        if event == 'app.status':
            self.on_update_status(*args)
        elif event == 'app.target':
            self.on_update_target(*args)
        elif event == 'app.connect':
            self.on_client_connect(*args)
        elif event == 'app.disconnect':
            self.on_client_disconnect(*args)
        elif event == 'peripheral':
            self.on_new_peripheral(*args)
        elif event == 'ready':
            self.on_ready(*args)
        elif event == 'data':
            self.on_notify_data(*args)
        elif event == 'ble_write_resp':
            self.on_ble_write_resp(*args)
        elif event == 'ble_read_resp':
            self.on_ble_read_resp(*args)
        elif event == 'ble_notify_resp':
            self.on_ble_notify_resp(*args)
        elif event == 'profile':
            self.on_update_profile(*args)
        elif event == 'proxy_write':
            self.on_ble_write(*args)
        elif event == 'proxy_read':
            self.on_ble_read(*args)
        elif event == 'proxy_notify':
            self.on_ble_notify(*args)

    def register(self, interface):
        self.interfaces.append(interface)

    def unregister(self, interface):
        if interface in self.interfaces:
            self.interfaces.remove(interface)

    def on_connect(self):
        for interface in self.interfaces:
            interface.connect()

    def on_disconnect(self):
        for interface in self.interfaces:
            interface.disconnect()

    def on_client_connect(self, client):
        for interface in self.interfaces:
            interface.client_connect(client)

    def on_client_disconnect(self, client):
        for interface in self.interfaces:
            interface.client_disconnect(client)

    def on_new_peripheral(self, peripheral, name, rssi):
        for interface in self.interfaces:
            interface.device_found(peripheral, name, rssi)

    def on_update_target(self, target):
        for interface in self.interfaces:
            interface.target_selected(target)

    def on_update_status(self, status):
        for interface in self.interfaces:
            interface.update_status(status)

    def on_ready(self):
        for interface in self.interfaces:
            interface.proxy_ready()

    def on_ble_write(self, service, characteristic, data, offset, withoutResponse):
        for interface in self.interfaces:
            interface.write_request(service, characteristic, data, offset, withoutResponse)

    def on_ble_write_resp(self, service, characteristic, error):
        for interface in self.interfaces:
            interface.write_response(service, characteristic, error)

    def on_ble_read(self, service, characteristic, offset):
        for interface in self.interfaces:
            interface.read_request(service, characteristic, offset)

    def on_ble_read_resp(self, service, characteristic, data):
        for interface in self.interfaces:
            interface.read_response(service, characteristic, data)

    def on_ble_notify(self, service, characteristic, enabled):
        for interface in self.interfaces:
            interface.notify_request(service, characteristic, enabled)

    def on_ble_notify_resp(self, service, characteristic):
        for interface in self.interfaces:
            interface.notify_response(service, characteristic)

    def on_notify_data(self, service, characteristic, data):
        for interface in self.interfaces:
            interface.update_data(service, characteristic, data)

    def on_profile(self, profile):
        for interface in self.interfaces:
            interface.update_profile(profile)

class BtleJuiceApp(Thread):
    def __init__(self, interface):
        Thread.__init__(self)
        # Create client
        self.client = SocketIO(interface.host, interface.port,CoreNamespace)

        # Save namespace
        self.interface = interface
        self.namespace = self.client.get_namespace()
        self.namespace.register(self.interface)
        self.interface.set_namespace(self.namespace)

        # Thread is not cancelled by default
        self.canceled = False

    def run(self):
        while not self.canceled:
            sleep(0.001)
            self.client.wait(seconds=0.1)

    def cancel(self):
        self.canceled = True

# Main exports

__all__ = [
    'SniffingInterface',
    'HookingInterface',
    'BtleJuiceInterface',
    'BtleJuiceApp',
    'HookForceResponse',
    'HookModify',
    'hexiify'
]
