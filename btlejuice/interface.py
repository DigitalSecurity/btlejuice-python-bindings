"""
BtleJuice Built-in Interfaces
"""
from btlejuice.utils import unbufferize, bufferize
from btlejuice.exceptions import HookForceResponse, HookModify

class BtleJuiceInterface(object):
    """
    Interface base class for BtleJuice.
    """

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.namespace = None

    def  set_namespace(self, namespace):
        self.namespace = namespace

    def emit(self, event, *args, **kwargs):
        if self.namespace is not None:
            self.namespace.emit(event, *args, **kwargs)

    def scan(self):
        """
        Enable BLE scanning.
        """
        self.emit('scan_devices')

    def select_target(self, target):
        """
        Select target to proxify.
        """
        self.emit('target', target)

    def get_status(self):
        """
        Asks for a status update.
        """
        self.emit('status')

    def stop(self):
        """
        Stop proxy.
        """
        self.emit('stop')

    ########################
    # Device operations.
    ########################

    def device_write(self, service, characteristic, data, offset=0, withoutResponse=False):
        """
        Write data to a device's characteristic.
        """
        self.emit('ble_write', service, characteristic, data, offset, withoutResponse)

    def device_read(self, service, characteristic):
        """
        Read data from a device's characteristic.
        """
        self.emit('ble_read', service, characteristic)

    def device_notify(self, service, characteristic, enabled):
        """
        Register for notification for a given characteristic.
        """
        self.emit('ble_notify', service, characteristic, enabled)

    ########################
    # Proxy operations
    ########################

    def proxy_write_resp(self, service, characteristic, error):
        """
        Send a write response to client.
        """
        self.emit('proxy_write_resp', service, characteristic, error)

    def proxy_read_resp(self, service, characteristic, data):
        """
        Send a read response to client.
        """
        self.emit('proxy_read_resp', service, characteristic, data)

    def proxy_notify_data(self, service, characteristic, data):
        """
        Notify client applications about a write operation performed on a
        characteristic.
        """
        self.emit('proxy_data', service, characteristic, data)

    def  proxy_notify_resp(self, service, characteristic):
        """
        Send a notify response to client.
        """
        self.emit('proxy_notify_resp', service, characteristic)


    ################
    # Device events
    ################


    def client_connect(self, client):
        """
        Called when a client is connected to the device.
        """
        pass

    def client_disconnect(self, client):
        """
        Called when a client is disconnected from the device.
        """
        pass

    def connect(self):
        """
        Called when client is connected to the remote webservice.
        """
        pass

    def disconnect(self):
        """
        Called when client is disconnected from the remote webservice.
        """
        pass

    def device_found(self, device, name, rssi):
        """
        Called when a device is found (during scanning).
        """
        pass

    def target_selected(self, target):
        """
        Called when a target has been selected (proxy mode).
        """
        pass

    def update_status(self, status):
        """
        Called when the remote webservice status is updated.
        """
        pass

    def proxy_ready(self):
        """
        Called when the proxy is ready.

        This callback is called after a target has been selected and the proxy
        successfully connected to the target device.
        """
        pass

    def write_request(self, service, characteristic, data, offset, withoutResponse):
        """
        Called before a write operation is performed.
        """
        pass

    def write_response(self, service, characteristic, error):
        """
        Called after a write operation was performed.
        """
        pass

    def read_request(self, service, characteristic, offset):
        """
        Called before a read operation is performed.
        """
        pass

    def read_reponse(self, service, characteristic, data):
        """
        Called after a read operation was performed.
        """
        pass

    def notify_request(self, service, characteristic, enabled):
        """
        Called before a notification subscription is sent.
        """
        pass

    def notify_response(self, service, characteristic):
        """
        Called after a master subscribed to a characteristic for notifications.
        """
        pass

    def update_profile(self, profile):
        """
        Called when a target has been selected, provides all the required info
        about target's profile.
        """
        pass

    def update_data(self, service, characteristic, data):
        """
        Called when a notification is sent by the remote device.
        """
        pass


class SniffingInterface(BtleJuiceInterface):
    def __init__(self, host, port, target):
        self.target = target
        BtleJuiceInterface.__init__(self, host, port)

    def connect(self):
        # Stop previous operations.
        self.stop()
        self.scan()

    def device_found(self, device, name, rssi):
        """
        Wait for our target device to be detected.
        """
        if device.lower() == self.target.lower():
            self.select_target(self.target)

    def read_request(self, service, characteristic, offset):
        """
        Forward read request to device.
        """
        self.device_read(service, characteristic)

    def read_response(self, service, characteristic, data):
        """
        Forward read response to core and notify the interface.
        """
        # Notify interface.
        self.on_data_read(service, characteristic, unbufferize(data))

        # Send response to proxy (required by client applications).
        self.proxy_read_resp(service, characteristic, data)

    def write_request(self, service, characteristic, data, offset, withoutResponse):
        """
        Forward write request to device.
        """
        # Notify interface.
        self.on_data_write(service, characteristic, unbufferize(data), offset, withoutResponse)
        self.device_write(service, characteristic, data, offset, withoutResponse)

    def write_response(self, service, characteristic, error):
        """
        Forward write response to core.
        """
        # Send response to proxy (required by client applications).
        self.proxy_write_resp(service, characteristic, error)

    def notify_request(self, service, characteristic, enabled):
        """
        Forward notification subscription.
        """
        self.on_subscribe_notification(service, characteristic, enabled)
        self.device_notify(service, characteristic, enabled)

    def notify_response(self, service, characteristic):
        self.proxy_notify_resp(service, characteristic)

    def update_data(self, service, characteristic, data):
        self.on_notification_data(service, characteristic, unbufferize(data))
        self.proxy_notify_data(service, characteristic, data)

    # Callbacks to implement
    def on_data_read(self, service, characteristic, data):
        """
        Called after a read operation was performed. Should be overriden.
        """
        pass

    def on_data_write(self, service, characteristic, data, offset, withoutResponse, error):
        """
        Called after a write operation was performed. Should be overriden.
        """
        pass

    def on_subscribe_notification(self, service, characteristic, enabled):
        """
        Called after a client application subscribed/unsubscribed to a
        characteristic for notifications.
        """
        pass

    def on_notification_data(self, service, characteristic, data):
        """
        Called after a notification was sent to a client application.
        """
        pass

class HookingInterface(BtleJuiceInterface):
    """
    Base hooking class.

    Derive this class to implement your own hooking interface. The following
    callbacks may be useful:

    - `on_before_read`: called before each read operation
    - `on_after_read`: called once the read operation has been performed
    - `on_before_write`: called before each write operation
    - `on_before_subscribe`: called before each notification subscription
    - `on_before_notification`: called before each data notification

    Use `HookForceResponse` to avoid a read or write operation to be effectively
    performed on the target device (you may also provide data if the response
    is supposed to return some). Use `HookModify` to  modify on-the-fly the data
    returned by or sent to the target device.
    """
    def __init__(self, host, port, target):
        self.target = target
        BtleJuiceInterface.__init__(self, host, port)

    def connect(self):
        # Stop previous operations.
        self.stop()
        self.scan()

    def device_found(self, device, address, rssi):
        """
        Wait for our target device to be detected.
        """
        if device.lower() == self.target.lower():
            self.select_target(self.target)
            self.on_proxy_setup()

    def read_request(self, service, characteristic, offset):
        """
        Forward read request to device.
        """
        try:
            # Default behavior: forward read request to device.
            self.on_before_read(service, characteristic, offset)
            self.device_read(service, characteristic)
        except HookForceResponse as response:
            # Send a result without forwarding the request to the device.
            self.read_response(service, characteristic, bufferize(response.data))

    def read_response(self, service, characteristic, data):
        """
        Forward read response to core and notify the interface.
        """
        try:
            self.on_after_read(service, characteristic, unbufferize(data))
            self.proxy_read_resp(service, characteristic, data)
        except HookModify as mod_resp:
            self.proxy_read_resp(service, characteristic, bufferize(mod_resp.data))
        except HookForceResponse as forced_resp:
            self.proxy_read_resp(service, characteristic, bufferize(forced_resp.data))

    def write_request(self, service, characteristic, data, offset, withoutResponse):
        """
        Forward write request to device.
        """
        try:
            self.on_before_write(service, characteristic, unbufferize(data), offset, withoutResponse)
            self.device_write(service, characteristic, data, offset, withoutResponse)
        except HookForceResponse as forced_resp:
            self.write_response(service, characteristic, False)
        except HookModify as mod_resp:
            self.device_write(
                service,
                characteristic,
                bufferize(mod_resp.data),
                mod_resp.offset,
                mod_resp.withoutResponse
            )

    def write_response(self, service, characteristic, error):
        """
        Forward write response to core.
        """
        # Send response to proxy (required by client applications).
        self.proxy_write_resp(service, characteristic, error)

    def notify_request(self, service, characteristic, enabled):
        """
        Forward notification subscription.
        """
        try:
            self.on_before_subscribe(service, characteristic, enabled)
            self.device_notify(service, characteristic, enabled)
        except HookForceResponse as forced_resp:
            self.notify_response(service, characteristic)
        except HookModify as mod_resp:
            self.device_notify(service, characteristic, mod_resp.enabled)

    def notify_response(self, service, characteristic):
        self.proxy_notify_resp(service, characteristic)

    def update_data(self, service, characteristic, data):
        try:
            self.on_before_notification(service, characteristic, unbufferize(data))
            self.proxy_notify_data(service, characteristic, data)
        except HookForceResponse as forced_resp:
            pass
        except HookModify as mod_resp:
            self.proxy_notify_data(
                service,
                characteristic,
                bufferize(mod_resp.data)
            )

    # To Implement

    def on_proxy_setup(self):
        """
        Called when the target device is found and proxy setup in progress.
        """
        pass

    def on_before_read(self, service, characteristic, offset):
        """
        Called before a read operation is performed.

        Raise `HookForceResponse` to avoid this request to be forwarded to the
        target device and provide your own data.
        """
        pass

    def on_after_read(self, service, characteristic, data):
        """
        Called after a read operation was performed.

        Raise `HookModify` to send modified data as the legitimate response.
        """
        pass

    def on_before_write(self, service, characteristic, data, offset, withoutResponse):
        """
        Called before a write operation is performed.

        Raise `HookForceResponse` to dismiss it.
        Raise `HookModify` to modify the forwarded request.
        """
        pass

    def on_before_subscribe(self, service, characteristic, enabled):
        """
        Called before subscription to notification.

        Raise `HookForceResponse` to dismiss.
        Raise `HookModify` to force enable/disable subscription.
        """
        pass

    def on_before_notification(self, service, characteristic, data):
        """
        Called before notification is sent to client application.

        Raise `HookForceResponse` to dismiss.
        Raise `HookModify` to send modified data.
        """
        pass
