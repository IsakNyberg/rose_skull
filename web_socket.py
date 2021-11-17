import socketserver
import hashlib
import base64

WS_MAGIC_STRING = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


def handshake(message_bytes):
    # self.request is the TCP socket connected to the clienter
    message = message_bytes.decode("utf-8")
    headers = message.split("\r\n")
    if "Upgrade: websocket" in message:
        key = None
        for h in headers:
            if "Sec-WebSocket-Key" in h:
                key = h.split(" ")[1]
                break
        if key is None:
            print('404 invalid key', end=' ')
            return bytes(
                "HTTP/1.1 400 Bad Request\r\n" +
                "Content-Type: text/plain\r\n" +
                "Connection: close\r\n" +
                "\r\n" +
                "Incorrect request",
                'utf-8'
            )

        key = (key + WS_MAGIC_STRING).encode('utf-8')
        resp_key = base64.standard_b64encode(
            hashlib.sha1(key).digest()
        ).decode('utf-8')

        return bytes(
            "HTTP/1.1 101 Switching Protocols\r\n" +
            "Upgrade: websocket\r\n" +
            "Connection: Upgrade\r\n" +
            f"Sec-WebSocket-Accept: {resp_key}\r\n\r\n",
            'utf-8'
        )

    else:
        print('Upgrade: No', end=' ')
        return bytes(
            "HTTP/1.1 400 Bad Request\r\n" +
            "Content-Type: text/plain\r\n" +
            "Connection: close\r\n" +
            "\r\n" +
            "Incorrect request",
            'utf-8'
        )


def decode_frame(frame):
    opcode_and_fin = frame[0]
    # assuming it's masked, hence removing the mask bit(MSB) to get len.
    # also assuming len is <125
    payload_len = frame[1] - 128
    mask = frame[2:6]
    encoded_payload = frame[6: 6 + payload_len]
    payload = bytearray(
        [encoded_payload[i] ^ mask[i % 4] for i in range(payload_len)]
    )
    return payload


def encode_frame(payload):
    # setting fin to 1 and opcpde to 0x1
    frame = [129]
    # adding len. no masking hence not doing +128
    frame += [len(payload)]
    # adding payload
    frame_to_send = bytearray(frame) + payload
    return frame_to_send
