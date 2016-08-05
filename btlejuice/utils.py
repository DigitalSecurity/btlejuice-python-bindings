from btlejuice.socketIO_client.parsers import Buffer

def unbufferize(data):
    """
    Extract content from Buffer instances if any.
    """
    if isinstance(data, Buffer):
        return data.content
    else:
        return data

def bufferize(data):
    """
    Encapsulate data in a Buffer object.

    Required to send binary data through websocket.
    """
    return Buffer(data)

def hexiify(data):
    """
    Convert data to HexII representation.
    """
    def convert_byte(b):
        if ord(b) >= ord('0') and ord(b) <= ord('z'):
            return '.%c' % ord(b)
        else:
            return '%02x' % ord(b)
    return ' '.join(map(convert_byte, list(data)))
