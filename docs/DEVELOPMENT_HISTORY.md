# Behind the Scenes: When an "Advanced" Tractor Mod Stress-Tested Codex

> **Development history · 23 October–10 November 2026**
> A documented episode from building **Advanced Realism Suite (ARS)** for Farming Simulator 25. This is a retrospective, **not** a release note, feature announcement, or performance benchmark.

## It started with a tractor

ARS was supposed to connect three things in one Farming Simulator 25 mod: **GIANTS-native vehicle physics**, realistic mechanical wear and damage, and a workshop that lets players understand and repair the consequences. The Advanced Damage System (ADS) and Realistic Mechanical Systems (RMS) were important *functional references*, while ARS's own physics would provide the missing link.

Enter **Walter**: the nickname for the OpenAI Codex coding agent working on ARS. Not a second developer, a separate model, or a real mechanic—just an unusually persistent autonomous software-development assistant.

The original idea was ambitious, but finite. Then the project evolved through multiple research rounds, changing requirements, agent handoffs, automated tests, and a major reorganization of its surrounding development workflow. The code gained *a few* more mechanical subsystems and dependencies than anyone had intended to build in one uninterrupted run.

At one point, it felt less like writing a game mod and more like asking a real tractor to provide a complete autobiography of every bearing, gasket, filter, and oil pump.

## A timeline of the escalation

- **23 October:** The retained local Git history already records work on ARS vehicle condition and physics.
- **24–30 October:** Long autonomous development sessions. The publicly available Physics Beta continued to evolve, while the broader suite remained under development.
- **6–10 November:** Another extended coding phase focused on the vehicle core, mechanical systems, workshop, and their integration.
- **10 November:** The original sprawling development brief was superseded by a tighter, *physics-first* scope. Finishing working player-facing systems became more important than inventing another layer of mechanical detail.
- **10 November:** A long-running Codex Goal encountered a remote context-compaction failure: `Incomplete response returned, reason: max_output_tokens`. The Goal appeared stalled in the app. The event was reported upstream as [openai/codex#60652](https://github.com/openai/codex/issues/60652).

The bug report includes an [additional evidence-based telemetry follow-up](https://github.com/openai/codex/issues/60652#issuecomment-6778946193).

## What the preserved logs actually showed

A read-only analysis of retained local Codex JSONL session metadata, including a preserved October archive, produced the following figures **as of 10 November 2026**:

| Measurement | Recorded value |
| --- | ---: |
| Retained session files | 24 |
| Combined local JSONL history | About 2.0 GB |
| Unique token-usage records | 45,987 |
| Duplicate response IDs found | 0 |
| Cumulative tokens across those records | **7.145 billion** |
| Cached input tokens | **6.934 billion** |
| Input-token cache proportion | **97.65%** |
| Successful compaction events | **649** |
| Sessions associated with an ARS working directory | 16 |
| Tokens in those ARS-associated sessions | **6.077 billion** |
| Compactions in those ARS-associated sessions | **556** |

Two especially long ARS sessions spanned approximately **74.8 hours (212 compactions)** and **69.6 hours (137 compactions)**, respectively. These are *wall-clock spans*, not proof of uninterrupted execution or billable time. A working-directory association does **not** prove that every token in a session was exclusively spent on ARS.

The Codex app separately displayed approximately **8.8 billion account-level tokens**, a **995.7-million-token peak day**, and a **13-hour-19-minute longest task**. Those app-wide counters have a broader scope than the retained local records and must not be added to them.

**Important:** Cached tokens are repeatedly processed input tokens, **not** billions of unique tokens simultaneously resident in one context window.

## The compaction incident

For the affected November session, the recorded model context window was **258,400 tokens**. The final ordinary token sample preceding the reported failure contained **243,991 input tokens plus 4,208 output tokens**, or approximately **96.05%** of that window when combined.

The failed remote-compaction call subsequently recorded:

| Field | Value |
| --- | ---: |
| Input tokens | 248,236 |
| Cached input tokens | 248,064 |
| Output tokens | **128,000** |
| Error | `max_output_tokens` |

Exactly 128,000 output tokens is consistent with exhaustion of an output-token limit. It **does not prove** why the remote compaction reached that limit, or whether the Goal's stalled UI state was directly caused by the same failure. OpenAI's [issue #60652](https://github.com/openai/codex/issues/60652) is the source for the full incident and follow-up; the underlying private session logs were not published.

## What changed in the development process

The useful outcome was not another simulation subsystem. It was a clearer boundary between:

1. **Product vision:** ARS physics plus coherent damage, diagnosis, service, and workshop gameplay.
2. **Active development scope:** Finish and integrate what is already approved, then hand over a testable development build.
3. **Research archive:** Preserve prior decisions and detailed future ideas without treating every historical note as a standing implementation order.
4. **Acceptance:** The operator performs in-game testing after handoff; a development ZIP does not have to pass every future release criterion before it can be delivered.

The game engine should be responsible for being a game engine. ARS should add realism to it—not construct a complete virtual tractor manufacturer from scratch.

## The moral of the story

The project is called **Advanced Realism Suite**.

Apparently, we took **"Advanced"** a little too seriously.

We set out to stress-test tractor engines, transmissions, tires, and hydraulics. Somewhere along the way, we ended up stress-testing the **AI context-compaction architecture** as well.

In other words: we briefly invented an *Advanced Codex Endurance Test* while trying to finish a Farming Simulator mod.

The tractor is supposed to break under abuse. The development assistant, ideally, should recover gracefully. 🐗

---

**Provenance and scope:** Historical notes and aggregated, locally verified development telemetry recorded on 10 November 2026. See [upstream issue #60652](https://github.com/openai/codex/issues/60652) and its [telemetry follow-up](https://github.com/openai/codex/issues/60652#issuecomment-6778946193). No private source archives, credentials, raw sessions, or internal project documents are embedded here. The full ARS suite was still unreleased at the time of this incident; see the [changelog](../CHANGELOG.md) for actual public releases.
