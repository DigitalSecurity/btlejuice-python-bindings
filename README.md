BtleJuice bindings
==================

BtleJuice provides bindings for both Python and NodeJS. These bindings require the BtleJuice Core to be ran in background in order to work properly.

These bindings provide two interface classes for sniffing and hooking, and an application class.

See https://github.com/DigitalSecurity/btlejuice for more details about *BtleJuice*.

Importing the required classes
------------------------------

The `btlejuice` module provides all the required application and interface classes, and should be imported as follows:

``` python
from btlejuice import BtleJuiceApp, SniffingInterface, HookingInterface
```

Creating a sniffing interface
-----------------------------

The `SniffingInterface` provides all the required methods to perform sniffing. This class should be instanciated with BtleJuice's server IP and port, as demonstrated below:

``` python
class MySniffingInterface(SniffingInterface):
    """
    Specific sniffing class.
    """
    def __init__(self, host, port, target):
        SniffingInterface.__init__(self, host, port, target)
```

The following methods are called when specific events occur:

  * `on_data_read(self, service, characteristic, data)`: called once a read operation has just been performed
  * `on_data_write(self, service, characteristic, data, offset, withoutResponse, error)`: called when a write operation has just been performed
  * `on_subscribe_notification(self, service, characteristic, enabled)`: called when a characteristic has just been (un)subscribed for notification
  * `on_notification_data(self, service, characteristic, data)`: called when a notification is received from the target device

Creating a hooking interface
----------------------------

The `HookingInterface` provides all the required methods to perform on-the-fly data manipulation. This class should be instanciated with BtleJuice's server IP and port, as demonstrated below:

``` python
class MyHookingInterface(HookingInterface):
    def __init__(self, host, port, target):
        HookingInterface.__init__(self, host, port, target)
```

The following methods are called when specific events occur:

  * `on_before_read(self, service, characteristic, offset)`: called before each read operation
  * `on_after_read(self, service, characteristic, data)`: called once the read operation has been performed
  * `on_before_write(self, service, characteristic, data, offset, withoutResponse)`: called before each write operation
  * `on_before_subscribe(self, service, characteristic, enabled)`: called before each notification subscription
  * `on_before_notification(self, service, characteristic, data)`: called before each data notification

It is possible to dismiss an operation or to alter its behavior thanks to two exception classes:

  * `HookForceResponse`: used to dismiss an operation and force the return value
  * `HookModify`: used to modify the parameters before forwarding to the target device or the central device.

In the following example, we modify the battery service's behavior in order to decrease the battery level each time this level is read:

``` python
class MyHookingInterface(HookingInterface):
    def __init__(self, host, port, target):
        HookingInterface.__init__(self, host, port, target)
        self.batt_level = 10

        def on_proxy_setup(self):
            print('[i] Target found, setting up proxy ...')

        def proxy_ready(self):
            print('[i] Proxy ready !')

        def on_before_read(self, service, characteristic, offset):
            if service.lower() == '180f' and characteristic.lower()=='2a19':
                self.batt_level -= 1
                if self.batt_level < 0:
                    self.batt_level = 100
                raise HookForceResponse(chr(self.batt_level))
```

Communicating with the target device
------------------------------------

BtleJuice bindings also provide all the required methods to communicate with the target device:

  * `device_read(self, service, characteristic)`: asks the BtleJuice proxy to read a specific characteristic on the target device
  * `device_write(self, service, characteristic, data, offset=0, withoutResponse=False)`: asks the BtleJuice proxy to write some data to a specific characteristic on the target device
  * `device_notify(self, service, characteristic, enabled)`: asks the BtleJuice proxy to subscribe for notification for a given characteristic

Creating a BtleJuice based App
------------------------------

Once your interface defined, you may use it through a `BtleJuiceApp` instance, as shown below:

``` python
import threading

[...]

try:
    app = BtleJuiceApp(
      MyHookingInterface(args.server, args.port, args.target)
    )
    app.setDaemon(True)
    app.start()
    while threading.active_count() > 0:
        time.sleep(0.1)
except KeyboardInterrupt:
    print('[i] Stopping ...')
    app.cancel()
```

Both BtleJuice core and proxy should run before this script is launched to work properly.
