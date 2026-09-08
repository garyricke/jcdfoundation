# Fairview highlights — cut sheet built on Bob's 7 points
**For:** the "Fairview video focusing on the highlights" Bob asked for Sept 1 (promised for Fri Sept 4)
**Source:** the raw `IMG_E####.MOV` files in `assets/fairview-dental-interviews-aug2026/`. The `E8481 02:55` style references below are from the original VTTs (approximate); the seconds in each section heading are the actual cut points used.
**Built Sept 4, Bruno added Sept 8:** ffmpeg cut now 4:54, Descript cut 4:20. 1080×1920, seven title cards. Master + web encode + EDL in `assets/fairview-dental-interviews-aug2026/highlights/` (git-ignored). Review link: `https://res.cloudinary.com/dsbllwpbh/video/upload/q_auto,vc_auto/jcd/fairview-highlights-v1.mp4` (82 MB, unlisted by obscurity only, not gated).

**How it was cut:** raw `_E` MOVs → faster-whisper word timestamps (whisper.cpp's were off by up to 1.6 s, do not use them for cuts) → in/out snapped to the gap between neighbouring words → ffmpeg h264_videotoolbox → concat → single loudnorm pass. Every clip was re-transcribed afterwards to confirm it starts and ends on the intended words. **Descript version (v2, built same day after a 1,000-credit top-up):** same 17 segments fed to Agent Underlord as media-file timecodes, plus filler removal, Studio Sound and captions. 3:54. Share: `https://share.descript.com/view/3hyf3pm7sWW` · Cloudinary `jcd/fairview-highlights-v2` · local `highlights/fairview-highlights-v2-descript.mp4`. Cost: 114 + 64 + 41 ≈ 219 credits over three rounds. **Both "clipped word" flaws were fixed Sept 8 — and the cause was not filler removal.** "appointment"→"point" and "I won't lie"→"I will lie" were **Studio Sound at 100% intensity smearing consonants**. There was no splice near either word. Dropping Studio Sound to **65%** restored both, verified by transcribing the export. Studio Sound is track-wide, so 65% now applies to the whole film. Title cards are smaller than the ffmpeg version; captions are Classic style, lower third.

**Which to send Bob:** v1 (ffmpeg) has every word intact but no captions or audio cleanup; v2 (Descript) has captions and Studio Sound but the two clipped words. Fix v2 by hand and send that.

Bob's order is the running order. One title card per section, in his words.

---

## 1 · The demand for people in this profession  *(cut: Gorenz 174.8–180.7 · Dominguez 184.3–190.4 · Gorenz 197.3–210.4)*
- **Dr. Gorenz** `E8481 02:55–03:28` — "It's a well-known fact that there's a shortage of hygienists out there… with that shortage has come higher pay for hygienists. I think hygienists are making more than they ever have at this time… it's a great time to get into it. It's a great field at this time."
- **Dr. Dominguez** `E8477 02:39–03:08` — "It is hard to have a fully staffed hygiene team… I do see a big need for hygiene. It's a field that I never see is gonna go away."

## 2 · What they look for in a candidate  *(cut: Gorenz 223.0–251.2 only; Dominguez's take is a stumble, dropped)*
- **Dr. Gorenz** `E8481 03:42–04:10` — "High energy… you got to have a drive to want to help people. Patients come first, an ability to put others before yourself… interpersonal skills is really big."
- **Dr. Dominguez** `E8477 06:02–06:15` — "Someone that has a strong character, can carry on a conversation, hard worker, a team player, flexibility."

## 3 · Starting salary  *(cut: Cardenas 209.0–213.9 · Dominguez 233.5–248.6; benefits list dropped for length)*
- **Dr. Cardenas** `E8479 03:29` — "Our office, we'd start them out at $45 an hour. So not a bad gig right out of school."
- **Dr. Dominguez** `E8477 03:55–04:10` — "On average like $45 is a good initial pay" + the benefits list (401k, holiday pay, PTO, medical, free dental work).
- Gorenz says it a third time at `E8481 05:31`; hold in reserve, three in a row is too many.

## 4 · The role hygienists play in the business  *(cut: Dominguez 92.8–98.7 · Gorenz 139.0–162.0, with Bob's question)*
- **Dr. Dominguez** `E8477 01:37` — "Hygiene is the heart and soul of our practice."
- **Dr. Gorenz** `E8481 02:19–02:38` — Q: "How important is the hygienist to the overall success of the practice?" — "Super important. Hygiene is the engine that keeps our practice going."

## 5 · Why the young professionals chose it, and are they happy  *(cut: Cassie 20.6–38.2 · Bethany 53.6–79.9)*
- **Cassie** `E8483 00:20–00:37` — "I've been a hygienist here for seven months." / "It's going fantastic. I love it here." / "Hygiene was something I stumbled upon, but as soon as I got into it I fell in love with it and kept going, and now here I am."
- **Bethany** `E8483 00:52–01:10` — "I always wanted to do something in healthcare, but didn't want to take the traditional nursing route… This is my home office, I grew up in this office… didn't find my true passion for it until I was actually in the program."
- Optional: **Bethany** `E8483 ~03:00` — the introvert line, "it's made me come out of my shell."

## 6 · Education: difficulty, cost, time  *(cut: 208.8–233.5 · 544.2–555.3 · 292.1–307.0 · 334.2–345.3 · 365.4–375.6)*
- **Bethany** `E8483 03:29` — "College of DuPage… about a total of four years… two years of gen eds prereqs and then two years in the actual program."
- **Cassie** `E8483 03:41` — "Illinois Valley Community College… about three and a half years to do everything."
- **Both** `E8483 09:04` — cost: "between 25 to 30" / "mine was between 20 to 25" (thousand).
- **Bethany** `E8483 04:48–05:05` — "Once I was in the program I was no longer a straight-A student. It was hard, it's very competitive, lots of work. But with the hard work you're so rewarded when you finally finish."
- **Bethany** `E8483 05:35–06:10` — "A very competitive entry process. I know hygienists that waited two, maybe three years on a wait list… COD accepts 30… out of 100-plus."
- **Do not use** Gorenz's "all it takes is two years" (`E8481 05:28`) next to the hygienists' 3.5–4. Same contradiction as the page; the hygienists' lived numbers win.

## 7 · "Do you think you made the right career choice?"  *(cut: hygienists 200.7–204.2 · Gorenz 375.7–390.8 · 395.0–413.6)*
- **Decision Sept 4 (Gary): no pickup.** The card now carries the question that was actually asked, **"Is this a long-term career?"** (E8483 03:20, Bob to both hygienists: "Absolutely." / "Oh yeah, I agree."), and that exchange opens the section. The email to Bob says so plainly and puts "did you make the right choice?" on the list for the next two shoots.
- **Never asked on Aug 20.** Nothing on tape answers it literally.
  - **Close for this cut, after the long-term-career exchange:** **Dr. Gorenz** `E8481 06:15–06:29` — "If you have any inclination towards going into nursing or any of the other health professions, very highly consider hygiene… you're making a really good rate from the get-go." Then `06:34–06:52` — "They love going to the hygienist… the hygienist is the fun part of the appointment. I envy that a little bit."
- #7 becomes the last question at the two remaining sector shoots.

## 8 · Dr. Michele Bruno — added Sept 8 at Bob's request  *(cut: 1.9–7.9 · 101.5–106.6 · 244.8–257.0 in E8475)*
Bob, 9/6: *"Looks great but we fit a short snippet of Michelle the dentist as she is on the Dunham Foundation board."* She was not in the reel at all. Placed inside **section 7**, after the hygienists' "Absolutely" and before Gorenz's close. ~23 s, three cuts:
- **ID** `E8475 00:01.9–00:07.9` — "My name is Michele Bruno. I'm a dentist and former part owner of Fairview Dental."
- **The ladder punch** `E8475 01:41.5–01:46.6` — Q: "Did you imagine yourself owning a practice when you were starting as a dental hygienist?" A: **"Never."**
- **The closer** `E8475 04:04.8–04:17.0` — "Being a hygienist is a great career. Being a dentist is a great career, and whether you stop after two years of a junior college or you decide to go on, it's amazing."

**Her board seat is NOT named on screen or in the email.** She is introduced only as a dentist and former part owner of Fairview, in her own words — [[feedback_dunham_nondisclosure]]. Bob's reason for including her is internal.

**Timing gotcha:** faster-whisper's word times for this file shift with the transcription window. The 235–262 s window put "being" at 243.94; a 240–258 s window put it at 245.06, which matches the measured silence at 244.71–245.04. The tighter window is right — cutting on the stale value clipped "be-" off "Being". Always re-cut and re-transcribe the rendered clip.

**Spelling:** her embroidered scrubs read **Dr. Michele Bruno** — one L, as verified. Bob writes "Michelle".

---

## Notes
- Six of the 21 clips on Cloudinary are truncated to ~1 s (`four-years`, `west-aurora`, `ladder-path`, `heart-soul`, `package`, `fun-part`). They were never used on the page; re-cut them from Descript if they're needed there.
- Subtitles and light JCD branding are still on the list for every clip, as told to Bob Aug 25.
- Fairview sees the final cut before anything goes public. This highlights reel is for Bob first.
