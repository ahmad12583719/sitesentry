# SiteSentry scoring rubric

SiteSentry uses a **fixed, additive, deterministic** scoring system. It is intentionally simple: every run starts at 100 points, and each open finding subtracts a fixed penalty based on its severity. Findings marked as a pass subtract no points.

| Severity | Fixed penalty | Examples in this MVP |
| --- | ---: | --- |
| Critical | 30 | Exposed `.env` or `.git` metadata; publicly reachable Redis service |
| High | 15 | Expired certificate; legacy TLS; publicly exposed database service; public SMB/RDP service |
| Medium | 8 | Missing CSP, HSTS, or X-Frame-Options; administration route responding publicly |
| Low | 3 | Missing `X-Content-Type-Options` or `Referrer-Policy`; a probe that could not complete |
| Informational / pass | 0 | Present baseline header; certificate still valid; expected HTTPS port open |

The calculation is:

```text
score = max(0, 100 - sum(open-finding penalties))
```

| Score | Grade | Interpretation |
| ---: | :---: | --- |
| 90–100 | A | Strong baseline; review all remaining findings as context-specific configuration decisions. |
| 80–89 | B | Good baseline with improvements to schedule. |
| 70–79 | C | Meaningful protections are present, but remediation should be planned. |
| 55–69 | D | Material configuration gaps need attention. |
| 40–54 | E | High-risk gaps are likely present; prioritize remediation. |
| 0–39 | F | Critical or widespread high-risk findings require urgent review. |

## Boundaries

This grade is a deterministic configuration signal, not a penetration-test result, compliance certification, or guarantee of security. The scanner does not identify the running software version behind a port, exploit a service, test authentication, or test for application-level vulnerabilities. It only applies the documented fixed checks to the entered target.
