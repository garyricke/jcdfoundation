# Suno prompt — underscore for the About page voiceover

**Pairs with:** `plan/vo-script-about-hero.md` (v3, ~3:40)
**Job:** sit underneath a spoken narration without ever competing with it
**Written:** 2026-07-28

---

## The one thing that matters

This is a **bed**, not a piece of music. If you find yourself listening to it, it's wrong. The voice is the content; the score's entire job is to make silence feel intentional and to carry the turn at *"This is what it's for."*

The failure mode is specific and very easy to hit: **inspirational nonprofit score.** Rising piano arpeggio, strings entering at 40 seconds, big major-key swell under the call to action. Suno will hand you that on a plate if you let it, and it would undo the tone of the entire site — the brand is gritty documentary, not fundraising gala.

---

## Primary prompt

**Style box** (short version, safe for any Suno version):

```
sparse instrumental documentary underscore, fingerpicked acoustic guitar, upright bass, brushed drums, warm pedal steel swells, 74 BPM, tape saturation, patient, hopeful, restrained, leaves space for narration
```

**Style box** (longer version, if your Suno accepts ~1000 characters):

```
Sparse instrumental documentary underscore for a narrated film. Fingerpicked steel-string acoustic guitar carrying a simple repeating figure, upright bass on root notes, brushed snare and felt-mallet percussion low in the mix, occasional pedal steel swells for warmth. A single sustained electric guitar note under the turns. 74 BPM, unhurried, lots of air between notes. Warm major tonality with an unresolved minor turn — hopeful but not triumphant, earned rather than sentimental. Analog tape saturation, room tone, slight wow and flutter, nothing glossy. Dynamics stay flat and low; no builds to a climax, no orchestral swell, no drum fills. Midrange deliberately empty so a speaking voice sits on top. American heartland and small-industry feeling — a factory town, not a prairie. Instrumental only.
```

**Settings**

| | |
|---|---|
| **Instrumental** | **ON.** Non-negotiable. |
| **Exclude styles** (if available) | `orchestral swell, cinematic trailer, corporate inspirational, epic, choir, vocal pads, EDM, heavy percussion, piano ballad` |
| **Length** | 4:00 if your version supports it; otherwise generate ~2:00 and use Extend. You want **~4:00 to cover a 3:40 read** with handles at both ends. |
| **Weirdness / style influence** | Weirdness low (~20%). Style influence high (~70–80%) — you want it to obey the restraint, not get creative. |

---

## Three directions worth trying

Generate a couple of each. They're genuinely different feels, and which one is right depends on the voice you land on.

**A · Heartland acoustic** *(the primary above — my recommendation)*
Fingerpicked guitar, upright bass, brushed drums, pedal steel. Warm, human, slightly worn. Matches the archival photographs and the Fox Valley setting without being folksy about it.

**B · Warm industrial**
```
sparse instrumental score, muted electric guitar with tape delay, low analog synth drone, soft mallet percussion, distant metallic room tone, 70 BPM, patient, spacious, warm not cold, industrial documentary, instrumental only
```
Leans into the factory. Slightly more modern and a little more serious. Good if the read comes back on the graver side — pairs well with the Equipto footage.

**C · Minimal, most neutral**
```
minimal instrumental underscore, felt piano single notes, warm low synth pad, subtle room tone, 68 BPM, very sparse, unresolved, no melody, ambient documentary bed, instrumental only
```
The safest under a voice, and the least characterful. Use this if A and B keep crowding the narration. "Felt piano" matters — regular piano sits right on top of a male speaking voice.

---

## How to judge a take

Play it **under the actual voiceover**, never on its own. A bed that sounds boring solo is usually the correct one.

**Keep it if:**
- You stop noticing it within fifteen seconds
- The one-line paragraphs in the script still land — the music fills the pauses without filling the meaning
- It can loop or be cut without an obvious seam
- Nothing arrives on a schedule that fights the script's own turns

**Reject it if:**
- Anything swells. At all.
- There's a discernible tune you could hum — that competes with the words
- Percussion has a backbeat you can march to
- It resolves triumphantly at the end. The script ends on an open question; the music must not answer it.
- Suno slipped in wordless "oohs" or a vocal-sounding pad. Common even with Instrumental on — regenerate.

---

## Fitting it to the read

**Be realistic about what Suno can do here.** It won't hit your narration's beats on command, and prompting for a specific arc ("builds at 2:10") mostly doesn't work. The practical workflow:

1. Generate a **flat, even ~4:00 bed** with no dramatic arc — that's what the prompt above is tuned for.
2. Lay the VO over it and cut the music to fit, rather than the reverse.
3. If you want lift at **"This is what it's for"** (the 1928 → now turn, roughly halfway), the cleanest trick is to generate a **second, slightly fuller take from the same prompt** and crossfade into it at that line. Same DNA, subtle gear change, no obvious edit.
4. Fade the music out under the last four lines and let *"So. What do you want to do?"* land nearly dry. That silence is the strongest production choice available and it costs nothing.

---

## Mixing under the voice

- **Music around −18 to −22 LUFS under the VO**, roughly 12–15 dB below the narration. If you're deciding between two levels, take the quieter one.
- **Carve, don't just duck.** A gentle 3–4 dB dip in the music around **1–3 kHz** is where speech intelligibility lives — it buys you clarity without pulling the bed down.
- **Let the music up in the gaps.** The script's pauses are deliberate — after *"He took it,"* after *"That's the part nobody can do for you."* Riding the bed up a few dB there makes those beats feel composed rather than empty.
- **Keep the low end.** Upright bass under a mid-register male voice is free warmth; don't high-pass it away.
- Export the final mix as **MP3 128 kbps mono** to `assets/jcd-dunham-vo.mp3` — the play button picks it up automatically.

---

## A note on rights

Suno output is generated, so there's no sync licence to clear — but the audio ends up on a public 501(c)(3) website, so check the terms attached to whichever Suno plan generated it before launch. Commercial-use rights differ by tier, and a foundation site counts as commercial use in most licence language. Worth five minutes now rather than a takedown later.
