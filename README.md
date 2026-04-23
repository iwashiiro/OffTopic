# OffTopic - FHE-based OT Exploit (ECSC 2024)

![cryptography](https://img.shields.io/badge/topic-cryptography-red)
![challenge](https://img.shields.io/badge/type-ctf--challenge-orange)
![ECC](https://img.shields.io/badge/primitive-ECC-blue)
![Python](https://img.shields.io/badge/language-Python-grey)

---

## Overview.

This repository contains a solution to a challenge from **ECSC 2024 (European Cyber Security Challenge)**.

The challenge implements a flawed version of **Oblivious Transfer (OT)** using **Elliptic Curve Cryptography (ECC)** combined with homomorphic properties.

Participants interact with a remote service that:
- Accepts a public key.
- Receives an encrypted choice.
- Returns a transformed ciphertext.
- Requires recovery of two hidden messages (`m0`, `m1`).

Due to incorrect assumptions in the design, the protocol is vulnerable and allows an attacker to recover both messages in every round.

---

## Vulnerability.

The scheme is based on:
S = rH + tG.

Where:
- `H = kG` is the public key.
- `t` encodes the user’s choice.
- `r` is a random nonce.

The server returns a transformed pair `(R, S)`.

### Core issue:

The attacker can:
- Fully control `t`.
- Exploit linearity of elliptic curve arithmetic.
- Recover the hidden scalar `v`.

Because the message space is small (`0–9`), we obtain:
v = m1 - 9*m0.

Which uniquely determines `(m0, m1)`.

---

## Exploitation strategy.

1. Fix a known private key `k`.
2. Precompute lookup table for small scalar values.
3. Send crafted ciphertext using `t = 10`.
4. Receive `(R, S)` from the server.
5. Compute:
v = S - kR.

6. Recover messages via:
v = m1 - 9*m0.

7. Repeat for all 128 rounds.

---

## Running the exploit.

Install dependencies:

```bash
pip install pycryptodome
```
Run:
```python solve.py```

## Example execution.

```[*] Connecting to challenge server
[*] Welcome to my new guessing game! Are you ready?

Round   1: v=  32  m0=2  m1=5
Round   2: v=  81  m0=1  m1=9
Round   3: v= -27  m0=3  m1=0
...
Round 128: v=  -6  m0=4  m1=3

[*] Final output (flag):
ECSC{ch3w1n5_m0r3_7h4n_y0u_c4n_b1t_bd1b5c58}
```
## Why it works.

The protocol incorrectly assumes:

- t is hidden and uncontrollable.

- ECC operations are non-invertible in this setting.

---
## In reality:

The attacker fully controls inputs.

ECC is linear over group operations.

Message space is extremely small.

This makes full recovery trivial.

---
## How to fix it.
Do not design custom OT protocols.

Use vetted cryptographic constructions.

Avoid exposing raw ECC operations.

Enforce strict input validation.

Prevent attacker-controlled ciphertext structure.

---
## Files.
solve.py → exploit script.

README.md → this file.

---
## References.
ECSC 2024 (European Cyber Security Challenge).

Elliptic Curve Cryptography (ECC).

Oblivious Transfer protocols.

Secure multiparty computation.

---
