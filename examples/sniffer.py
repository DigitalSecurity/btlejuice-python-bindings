import argparse
import threading
import time
from btlejuice import BtleJuiceApp, SniffingInterface, hexiify

class MySniffingInterface(SniffingInterface):
    """
    Specific sniffing class.
    """
    def __init__(self, host, port, target):
        SniffingInterface.__init__(self, host, port, target)

    def on_data_read(self, service, characteristic, data):
        """
        Read callback
        """
        # print('[<][%s - %s] %s' % (service, characteristic, hexiify(data)))
        print('[<][{} - {}] {}'.format(service, characteristic, data))

    def on_data_write(self, service, characteristic, data, offset, withoutResponse):
        """
        Write callback.
        """
        # print('[>][%s - %s] %s' % (service, characteristic, hexiify(data)))
        print('[>][{} - {}] {}'.format(service, characteristic, data))

    def on_notification_data(self, service, characteristic, data):
        """
        Data notification callback.
        """
        # print('[!][%s - %s] %s' % (service, characteristic, hexiify(data)))
        print('[!][{} - {}] {}'.format(service, characteristic, data))

    def on_subscribe_notification(self, service, characteristic, enabled):
        # print('[N][%s - %s] %s' % (service, characteristic, enabled))
        print('[N][{} - {}] {}'.format(service, characteristic, enabled))

    def client_connect(self, client):
        """
        BD master connection callback.
        """
        print('** Connection from %s' % client)

    def client_disconnect(self, client):
        """
        BD master disconnection callback.
        """
        print('** Disconnection from %s' % client)

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
        app = BtleJuiceApp(MySniffingInterface(args.server, args.port, args.target))
        app.setDaemon(True)
        app.start()
        while threading.active_count() > 0:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print('[i] Stopping sniffer ...')
        app.cancel()
