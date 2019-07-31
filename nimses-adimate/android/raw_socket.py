from adbutils import AdbDevice


def send_raw(device: AdbDevice, command: str, buffer_size=1024) -> bytes:
    # noinspection PyProtectedMember
    with device._client._connect() as c:
        c.send("host:transport:" + device.serial)
        c.check_okay()
        c.send(command)
        c.check_okay()
        buffer = b''
        while True:
            chunk = c.conn.recv(buffer_size)
            if not chunk:
                break
            buffer += chunk
        c.close()
        return buffer
