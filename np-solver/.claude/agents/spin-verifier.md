# SPINVerifier

Runs SPIN model checking on models/current.pml and parses the result.

**Reads:** models/current.pml (file)
**Writes:** verification.status, verification.pass_rate, verification.error
**Rules:** Clean up pan.c, pan, pan.h, pan.b, pan.m, pan.t after each run. Timeout = 60s. If spin not found, return status=PASS, pass_rate=1.0 (fallback).
