# JWT Token Reference

<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

## 1. Overview

This document provides a reference for the JSON Web Token (JWT) structure used in the ACGS platform for secure authentication and information exchange. JWTs are a compact, URL-safe means of representing claims to be transferred between two parties.

## 2. JWT Structure

A JWT consists of three parts separated by dots (`.`):

- **Header**: Contains the token type (JWT) and the signing algorithm (e.g., HMAC SHA256 or RSA).
- **Payload**: Contains the claims (statements about an entity, typically the user, and additional data).
- **Signature**: Used to verify that the sender of the JWT is who it says it is and to ensure that the message hasn't been tampered with.

Example Structure:

```
xxxxx.yyyyy.zzzzz
```

Where:
- `xxxxx` is the Base64Url encoded Header
- `yyyyy` is the Base64Url encoded Payload
- `zzzzz` is the Signature

## 3. Claims

The payload of a JWT typically contains claims. These can be:

- **Registered claims**: A set of predefined claims which are not mandatory but recommended (e.g., `iss` (issuer), `exp` (expiration time), `sub` (subject)).
- **Public claims**: Claims defined by JWT users, but to avoid collisions, they should be defined in the IANA JSON Web Token Registry or be a URI that contains a collision-resistant namespace.
- **Private claims**: Custom claims created to share information between parties that agree on their meaning.

## 4. Constitutional Compliance

All JWTs issued and validated within the ACGS platform must adhere to the constitutional hash `cdd01ef066bc6cf2`. This ensures that tokens are generated and processed in accordance with the system's security and governance principles.

## 5. Related Information

- [ACGS Service Architecture Overview](../ACGS_SERVICE_OVERVIEW.md)
- [ACGS System Overview](../../SYSTEM_OVERVIEW.md)
- [Authentication Service API](authentication.md)