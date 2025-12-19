# Celery with Redis/Valkey for long-running tasks

Date: 2025-08-04

## Status

Open

## Context

We currently do **not** use a task queue or worker system.
In the near future we will have long-running and/or CPU-heavy tasks (e.g. preprocessing documents, creating embeddings via APIs).

We don’t want these tasks to block or slow down our FastAPI runtime, so we need an external worker. Celery is the primary candidate, and for its broker/result backend we are considering **Redis** or **Valkey**.

### Redis vs Valkey (high-level)

| Aspect                     | Redis                                                                         | Valkey                                                                                |
| -------------------------- | ----------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| **Origin**                 | Original upstream project, now partly source-available with licensing changes | Fully open-source community-driven fork created to preserve open licensing            |
| **Celery Compatibility**   | Officially supported and widely used in production                            | Aims to be fully Redis-compatible; still newer and with fewer production case studies |
| **Ecosystem & Hosting**    | Mature ecosystem, abundant tooling, many managed hosting options              | Compatibility is good, but managed hosting and ecosystem are still developing         |
| **Stability / Provenness** | Long track record, battle-tested                                              | Stable but younger; long-term trajectory promising but less proven                    |
| **Risk**                   | Some vendor lock-in concerns due to licensing changes                         | Lower licensing risk, but higher maturity risk                                        |

We have **not** yet chosen which one we will use.

## Decision

We will introduce a **Celery-style worker architecture** (separate worker process and broker) for long-running and CPU-heavy tasks, using **either Redis or Valkey** as the broker/result backend.

The concrete choice between Redis and Valkey remains open and will be decided in a follow-up ADR.

## Consequences

* FastAPI stays responsive; long-running work moves to background workers.
* We add an extra infrastructure component (broker + worker processes) to operate and monitor.
* A future ADR must:

  * Compare Redis vs Valkey in more depth for our specific workload.
  * Decide which one to standardize on for Celery.
