from Crypto.PublicKey.ECC import EccPoint
from Crypto.Random import random
import json, socket

DEBUG = True
def dbg(label, data):
    if DEBUG:
        print(f"  [DBG] {label}: {data!r}")

p  = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
Gx = 0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296
Gy = 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5
q  = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
G  = EccPoint(Gx, Gy)

def neg_pt(pt):
    return EccPoint(int(pt.x), (-int(pt.y)) % p)

k = 42
H = k * G

table = {}
for v in range(1, 100):
    pt = v * G
    table[(int(pt.x), int(pt.y))] = v
    npt = neg_pt(pt)
    table[(int(npt.x), int(npt.y))] = -v

def decrypt_v(R, S):
    kR = k * R
    pt = S + neg_pt(kR)
    try:
        return table.get((int(pt.x), int(pt.y)), 0)
    except Exception:
        return 0

def encrypt_t(t):
    r = random.randint(1, q - 1)
    R = r * G
    if   t == 0: S = r * H
    elif t  > 0: S = r * H + t * G
    else:        S = r * H + neg_pt((-t) * G)
    return R, S

def recover(v):
    for m0 in range(10):
        rem = v + 9 * m0
        if rem % 10 == 0:
            m1 = rem // 10
            if 0 <= m1 <= 9:
                return m0, m1
    raise ValueError(f"No solution for v={v}")

HOST, PORT = "url-of-the.chall", 12345    

def recvline(s):
    buf = b""
    while not buf.endswith(b"\n"):
        chunk = s.recv(1)
        if not chunk:
            raise ConnectionError(f"Connection closed! Got: {buf!r}")
        buf += chunk
    line = buf.decode().strip()
    dbg("RECV", line)
    return line

def recvjson(s):
    """Read a line and extract the JSON object from it (ignoring leading prompt text)."""
    line = recvline(s)
    idx = line.find("{")
    if idx == -1:
        raise ValueError(f"No JSON found in line: {line!r}")
    return json.loads(line[idx:])

def sendline(s, msg):
    dbg("SEND", msg)
    s.sendall((msg + "\n").encode())

def drain(s, timeout=3):
    s.settimeout(timeout)
    try:
        while True:
            line = recvline(s)
            print(f"[*] {line}")
    except Exception:
        pass

print(f"[*] Connecting to {HOST}:{PORT}")
s = socket.socket()
s.connect((HOST, PORT))
s.settimeout(30)

# Welcome line.
welcome = recvline(s)
print(f"[*] {welcome}")
sendline(s, json.dumps({"Hx": int(H.x), "Hy": int(H.y)}))

for rnd in range(128):
    # Send our encrypted t=10 as choice bit.
    R, S = encrypt_t(10)
    sendline(s, json.dumps({
        "Rx": int(R.x), "Ry": int(R.y),
        "Sx": int(S.x), "Sy": int(S.y)
    }))

    # Receive server's homomorphic result (extract JSON even if prefixed by prompts).
    resp = recvjson(s)
    Rr = EccPoint(resp["Rx"], resp["Ry"])
    Sr = EccPoint(resp["Sx"], resp["Sy"])

    v = decrypt_v(Rr, Sr)
    m0, m1 = recover(v)
    print(f"Round {rnd+1:3d}: v={v:4d}  m0={m0}  m1={m1}")

    # Send recovered messages.
    sendline(s, json.dumps({"m0": m0, "m1": m1}))

print("\n[*] Final output (flag):")
drain(s, timeout=5)
s.close()
