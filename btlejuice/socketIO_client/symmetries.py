try:
    from logging import NullHandler
except ImportError:  # Python 2.6
    from logging import Handler

    class NullHandler(Handler):

        def emit(self, record):
            pass


from six import indexbytes


try:
    from ssl import SSLError
except ImportError:
    class SSLError(Exception):
        pass


try:
    memoryview = memoryview
except NameError:
    memoryview = buffer


def get_byte(x, index):
    return indexbytes(x, index)


def get_character(x, index):
    return chr(get_byte(x, index))


def decode_string(x):
    # print('######################## X : {}'.format(x))
    # return x.decode('utf-8')
    return str(x.decode('unicode_escape'))
    # return x

def encode_string(x):
    return x.encode('utf-8')
