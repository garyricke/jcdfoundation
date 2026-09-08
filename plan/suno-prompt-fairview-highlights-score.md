# Suno prompt — underscore for the Fairview highlights film

**Pairs with:** the Fairview highlights reel (`jcd/fairview-highlights-v2`, 4:20 captioned · `jcd/fairview-highlights-v1`, 4:54)
**Job:** sit underneath six people talking, recorded on a phone in a dental office, without ever masking a consonant
**Written:** 2026-09-08

---

## This is a different job from the John Dunham score

`plan/suno-prompt-about-vo-score.md` scores a **written narration** — one produced voice, even level, elegiac, 1928, 74 BPM heartland acoustic. Do not reuse it here.

This film is **interview audio**: six people in their twenties to sixties, lav-on-phone, uneven levels, room tone, a dental office humming in the background. And the subject is a job a seventeen-year-old could start next year. So the bed should read **contemporary and forward-moving**, not archival and not reverent.

The failure mode is the same as always though: **inspirational nonprofit score.** Rising piano, strings at forty seconds, major-key swell under the last line. Suno will hand you that on request. It would undo the tone of the whole site.

---

## The two constraints that actually decide this

**1. The midrange belongs to the speech.** Phone-and-lav dialogue lives roughly 200 Hz to 4 kHz, and that is exactly where piano, acoustic guitar and strings live. Anything with a melody in that band will eat consonants. The bed must be built from **low sustained tone plus high air**, with the middle deliberately hollow.

**2. The music is only ever exposed for about a second and a half.** There are seven title cards, and the gaps between them run 20 to 66 seconds:

| Card | In | Exposed for |
|---|---|---|
| 1 · The demand | 0:00 | 1.5 s |
| 2 · What they look for | 0:23 | 1.5 s |
| 3 · Starting pay | 0:44 | 1.5 s |
| 4 · What hygienists mean to the practice | 1:04.5 | 1.5 s |
| 5 · Why they chose it | 1:32 | 1.5 s |
| 6 · The education | 2:14 | 1.5 s |
| 7 · Is this a long-term career? | 3:20 | 1.5 s |

A second and a half is not enough to land a musical idea. **So do not compose to the cards.** No stingers, no hits, no resolution on the cut. The bed runs flat and even and simply becomes audible when the talking stops. That is what makes the cards feel intentional rather than like a gap.

It also means you want a **loop, not a through-composed piece**. Generate 90 to 120 seconds that circles cleanly and repeat it. Nobody will hear the seam under dialogue, and it beats fighting Suno for five unbroken minutes.

---

## Primary prompt

**Style box** (short — safe for any Suno version):

```
sparse instrumental documentary underscore, muted electric guitar plucks with tape delay, warm analog synth bass pulse, soft felt mallets, 84 BPM, hollow midrange, no melody, patient, loopable, leaves room for dialogue
```

**Style box** (long — if your Suno accepts ~1000 characters):

```
Sparse instrumental underscore for a documentary interview film. Muted palm-damped electric guitar plucks with a short tape delay, warm analog synth bass holding root notes, felt mallets and a soft shaker low in the mix, and a slow filtered pad underneath. 84 BPM, steady and unhurried, lots of air between the notes. Warm major tonality with one unresolved suspended note — hopeful, never triumphant, earned rather than sentimental. No lead melody and nothing in the vocal register: the midrange is deliberately hollow so a speaking voice sits on top. Dynamics stay flat and low — no build, no climax, no orchestral swell, no drum fills, no risers. Analog tape saturation and room tone, slightly worn, nothing glossy or cinematic. Contemporary and young rather than nostalgic; this plays under people in their twenties talking about their careers. Repeating and loopable, the same short figure circling with small variations. Instrumental only.
```

**Settings**

| | |
|---|---|
| **Instrumental** | **ON.** Non-negotiable. |
| **Exclude styles** | `vocals, singing, choir, orchestral swell, cinematic trailer, corporate inspirational, epic, piano ballad, EDM, heavy percussion, drum fills, risers, lo-fi hip hop` |
| **Length** | Generate **90–120 s and loop it.** Only reach for Extend if you want a genuinely evolving five minutes. |
| **Weirdness** | Low, ~20% |
| **Style influence** | High, ~75–80% — you want obedience to the restraint, not invention |

`lo-fi hip hop` is on the exclude list on purpose. It is the obvious reach for a young audience and it would date the film in about a year.

---

## Three directions worth trying

Generate a couple of each. Which one is right depends on how much room the dialogue actually leaves once it is ducked.

**A · Modern documentary pulse** *(the primary above — my recommendation)*
Muted guitar plucks, synth bass, felt mallets. Forward motion without hype. Reads current, which matters when the audience is eighteen.

**B · Warm minimal** *(safest under dialogue, least characterful)*
```
minimal instrumental bed, low warm synth pad, single felt piano notes, subtle room tone, 76 BPM, very sparse, no melody, unresolved, ambient documentary underscore, instrumental only
```
Use this if A keeps crowding the speech. "Felt piano" matters — a normal piano sits right on top of a speaking voice.

**C · Fox Valley workshop** *(ties the three sector films together)*
```
sparse instrumental score, muted electric guitar with tape delay, low analog drone, soft mallet percussion, distant metallic room tone, 80 BPM, patient, spacious, warm not cold, industrial documentary, instrumental only
```
Leans into the working-building feel. Slightly more serious.

---

## Make it a family, not a one-off

Two more sector films are coming — advanced manufacturing and the building trades. **Pick one palette now and make three variants of it**, rather than scoring each film from scratch. Same instruments, same tempo family, one thing changed per sector:

| Sector | Variant |
|---|---|
| Health sciences (Fairview) | the primary as written |
| Advanced manufacturing | same palette, add the distant metallic room tone from direction C |
| Building trades | same palette, swap felt mallets for a woodier, drier percussion |

Three films that sound related read as a series. Three films with unrelated music read as three one-offs.

---

## Mixing it in — the numbers that worked

From the John Dunham video, which is the same problem one voice at a time:

- **Bed sits about −22 to −24 dB under the speech.** Lower than feels right on first listen; interview audio is less even than a produced read, so leave more headroom than you think you need.
- **Sidechain duck** the bed against the dialogue: ratio 3:1, attack ~60 ms, release ~900 ms. The long release stops it pumping between sentences.
- **EQ the bed, not the voice.** High-pass around 60 Hz for rumble, then scoop **250 Hz to 4 kHz by 4–6 dB**. That is the single change that keeps consonants intact.
- **Fade in across the first card, fade out over the last four seconds.**
- **Loudness:** measure the mix, then apply one static gain to hit −16 LUFS. Do not run a single-pass `loudnorm` over a voice-plus-music mix — it levels the music-only intro up to speech loudness.

### ⚠️ And leave Studio Sound at 65%

Learned the hard way on this exact film, 2026-09-08. Studio Sound at **100%** smeared consonants badly enough that "appointment" played as "point" and "I won't lie" played as "I will lie". There was no edit near either word — it was purely the processing. **65% restored both.** Adding music will not hide this; it makes it worse. Verify any export by transcribing it and reading the words back against the source.

---

## Takes

### "Open Floor" — 2026-09-08, 0:24
**Keep the palette. Get it longer.** The hard part of this brief is already solved: the energy sits below 250 Hz and the consonant band at 2–4 kHz is **28 dB down** on the low end, so it does not touch speech. Measured bands:

| Band | Level |
|---|---|
| 20–120 Hz | −19.6 dB |
| 120–250 Hz | −22.4 dB |
| 250–800 Hz | −23.0 dB |
| 800–2000 Hz | −34.7 dB |
| 2000–4000 Hz | −47.9 dB |

Two things stop it looping: it **fades to silence from 0:21**, and there is a **16 dB dropout at 0:09–0:10** that turns into a recurring hole every pass. Test mix (24 s crossfade-looped under the 4:20 cut) was at `jcd/fairview-highlights-musictest` — it held up, but the dip was audible in the quiet stretches.

**Superseded by "Open Loop" below.**

### "Open Loop" — 2026-09-08, 4:40.9 — ✅ **this is the one**
A fresh generation, not an extension of "Open Floor" (correlation of the openings is ~0.00), but it kept the palette and fixed everything:

| | Open Floor | Open Loop |
|---|---|---|
| Length | 0:24 | **4:40.9** |
| Loudness range | 17.3 LRA | **4.7 LRA** — genuinely flat, which is what a bed wants |
| 2–4 kHz (consonants) | −47.9 dB | −42.1 dB, still 24 dB under the low end |
| Dropouts | 16 dB hole at 0:09 | none; everything sits between −13.5 and −18.5 dB |
| Ending | fades to silence at 0:21 | **no fade** — full level at 4:39, so you shape your own |

Covers the 4:20 captioned cut outright. It is 13.8 s short of the 4:54 uncaptioned cut, so that one uses a 6 s crossfade of the 2:00–2:40 passage onto the end — inaudible.

## The delivered mix — settings that shipped

Both scored cuts were built 2026-09-08 with these exact settings, and every key line was re-transcribed afterwards to prove the music does not mask speech:

- Bed: high-pass 60 Hz, then −5 dB at 500 Hz, −5 dB at 1.5 kHz, −4 dB at 3 kHz (Q≈1.0), then −9 dB overall
- Sidechain against the dialogue: **threshold 0.03, ratio 4:1, attack 40 ms, release 450 ms** — the 450 ms release (not the 900 ms used on the John film) is what lets the bed breathe back up inside the 1.5 s title cards
- Fade in 1.2 s, fade out 5 s
- Master: static gain to **−16 LUFS**, then `alimiter=limit=0.76:level=disabled` for **−2.2 dBFS** peak

### ⚠️ ffmpeg `alimiter` auto-levels by default
`alimiter` has `level=enabled` as its default, which **normalises the output straight back to 0 dBFS** and silently undoes the headroom you just asked for. Peaks measured 0.0 dBFS no matter what `limit` was set to. Always pass **`level=disabled`**.

Note also that the Descript export itself came out at **−21.7 LUFS** — quiet for web. The scored masters are brought up to −16.

## Where it goes

The captioned cut lives in Descript (composition "Fairview Highlights — 7 Points (v1)"), so the bed can be dropped on a music track there. The uncaptioned ffmpeg cut is mixed from `assets/fairview-dental-interviews-aug2026/highlights/` — the mix recipe in the John video render script applies unchanged, only the levels above differ.

Fairview still sees the final cut before anything goes public.
