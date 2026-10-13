#!/usr/bin/env python3
"""Load SAMPLE applications into the review tool so Bob's team can try it.

Every person, school answer, note and letter here is made up. Every sample row
is marked is_sample = true, and re-running this script first deletes the old
sample rows, so it's safe to run again after edits.

Go-live cleanup (run in the Supabase SQL editor; see review-schema.sql):
    delete from public.review_applications where is_sample;
    delete from public.review_reviewers    where is_sample;
    delete from public.review_audit        where is_sample;

Needs SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in the environment (they live
in the Netlify site's env vars; never commit them). Standard library only.

Run:  python3 supabase/review-sample-data.py
"""
import json
import os
import random
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
if not URL or not KEY:
    sys.exit("Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY first.")

MODEL = "Sample flag (written by hand, not a real AI read) · instructions v0"
rng = random.Random(27)


def req(method, path, body=None, prefer="return=minimal"):
    if isinstance(body, list):
        # PostgREST bulk inserts need every row to carry the same keys.
        keys = sorted({k for row in body for k in row})
        body = [{k: row.get(k) for k in keys} for row in body]
    r = urllib.request.Request(
        f"{URL}/rest/v1/{path}", method=method,
        data=None if body is None else json.dumps(body).encode(),
        headers={"apikey": KEY, "Authorization": f"Bearer {KEY}",
                 "Content-Type": "application/json", "Prefer": prefer})
    try:
        with urllib.request.urlopen(r) as resp:
            text = resp.read().decode()
            return json.loads(text) if text else None
    except urllib.error.HTTPError as e:
        sys.exit(f"{method} {path.split('?')[0]} failed ({e.code}): {e.read().decode()[:400]}")


# ---------------------------------------------------------------- reviewers
REVIEWERS = [
    dict(id="bob", name="Bob Vaughan", role="final", label="Final decision", is_sample=False),
    dict(id="gary", name="Gary Ricke", role="admin", label="Admin · Orbis", is_sample=False),
    dict(id="s-nurse", name="Pat Morales", role="reviewer", focus_area="Health Sciences",
         label="Sample reviewer · Nurse", is_sample=True),
    dict(id="s-mfg", name="Dana Kowalski", role="reviewer", focus_area="Advanced Manufacturing",
         label="Sample reviewer · Manufacturer", is_sample=True),
    dict(id="s-trades", name="Luis Ortega", role="reviewer", focus_area="Building Trades",
         label="Sample reviewer · Electrician", is_sample=True),
    dict(id="s-edu", name="Terri Banks", role="reviewer", focus_area=None,
         label="Sample reviewer · Educator", is_sample=True),
    dict(id="s-coach", name="Sam Reyes", role="reviewer", focus_area=None,
         label="Sample reviewer · Coach", is_sample=True),
]

# Placeholder distance tiers until Bob supplies his real ZIP lists.
ZIP_TIERS = {
    "core": ["60119", "60134", "60151", "60502", "60503", "60504", "60505", "60506",
             "60510", "60538", "60542", "60543", "60554"],
    "edge": ["60174", "60175", "60512", "60545", "60560", "60564", "60585", "60586"],
    "placeholder": True,
}

HM = "Health Sciences"
MF = "Advanced Manufacturing"
BT = "Building Trades"


def L(name, role, org, body):
    return dict(rec_name=name, rec_role=role, rec_org=org, body=body)


def F(reason, quote):
    return dict(reason=reason, quote=quote)


# ---------------------------------------------------------------- applicants
# Each dict: identity, school, plan, the free-text answers, letters, the sample
# AI flag, and the sample review state (recommendations / notes / decision).
APPS = [
    dict(first="Marisol", last="Vega", city="Aurora", zip="60505", school="East Aurora",
         grad="May 2025", focus=HM, profession="Registered nurse (ADN, then BSN)",
         level="Community college", year="2nd year", start="Already enrolled",
         inst="Waubonsee Community College, Nursing (ADN)", cost=4300,
         act_school="Student nurses club at Waubonsee. In high school: HOSA, girls' soccer.",
         act_comm="CNA at a memory-care home, 24 hours a week. I help my mom with my two little brothers after school.",
         goal="I'm in my third semester of the nursing program at Waubonsee. My spring tuition is due January 15 and my car broke down in November, so the money I saved went to that. If I can't pay I have to sit out a semester and lose my spot in the cohort. I've worked as a CNA for two years and I know this is what I want to do. I want to finish my ADN, pass the NCLEX, and work nights while I finish my BSN.",
         other_aid="Filed FAFSA. Got a Pell grant for fall but it doesn't cover spring after my hours went up.",
         letters=[L("Karen Liu, RN", "Employment supervisor", "Memory-care home, Aurora",
                    "Marisol is the aide families ask for by name. She has never missed a shift in two years, including the week her car died. She will be an excellent nurse."),
                  L("Mr. Daniel Ortiz", "Teacher", "East Aurora High School",
                    "Marisol carried a full course load while working and helping at home. She is steady, honest and kind.")],
         flag="read_first",
         reasons=[F("Mid-program and at risk of having to stop", "If I can't pay I have to sit out a semester and lose my spot in the cohort."),
                  F("Has held a job in the field for two years", "I've worked as a CNA for two years"),
                  F("Specific plan with dates", "finish my ADN, pass the NCLEX, and work nights while I finish my BSN")],
         urgent=True, urgent_note="Spring tuition due Jan 15. Decide early per Bob's urgent-case rule.",
         recs={"s-nurse": "tier1", "s-edu": "tier1"},
         notes=[("s-nurse", "This is exactly the case Bob described. Two years as a CNA, already mid-program. Fund before the Jan 15 deadline."),
                ("bob", "Agree. Paying Waubonsee directly for spring.")],
         final=("fund", 4300, "Waubonsee Community College"),
         transcript=True, cost_est=True, days=4),

    dict(first="Tyler", last="Brandt", city="Elburn", zip="60119", school="Kaneland",
         grad="May 2027", focus=MF, profession="Welder",
         level="Community college", year="1st year", start="August 2027",
         inst="Waubonsee Community College, Welding Technology certificate", cost=5200,
         act_school="FFA chapter vice president. Ag mechanics class two years.",
         act_comm="Part-time at a farm equipment repair shop in Maple Park since sophomore year, about 15 hours a week, more in summer.",
         goal="I want to be a welder. I've been welding at the shop where I work for two years, mostly repairs on planters and trailers, and I'm good at it but I want the certifications so I can get on at a fabrication shop. The welding certificate at Waubonsee gets me my AWS certs. My boss said he'd hire me back full time once I'm certified.",
         other_aid="None yet. Will file FAFSA in December.",
         letters=[L("Rick Hanley", "Employment supervisor", "Farm equipment repair, Maple Park",
                    "Tyler shows up early, cleans his station without being asked and his beads are better than some of my journeymen. I'll hire him full time the day he's certified.")],
         flag="read_first",
         reasons=[F("Held a job while in school", "Part-time at a farm equipment repair shop in Maple Park since sophomore year"),
                  F("Concrete plan and a job waiting", "My boss said he'd hire me back full time once I'm certified.")],
         recs={"s-mfg": "tier1"},
         notes=[("s-mfg", "Employer is already committed. This is a high-confidence pick.")],
         transcript=True, cost_est=True, days=60),

    dict(first="Andre", last="Collins", city="Aurora", zip="60506", school="West Aurora",
         grad="May 2027", focus=BT, profession="Electrician",
         level="Vocational training", year="1st year", start="June 2027",
         inst="Electrical apprenticeship (non-union contractor), classroom hours at COD", cost=3100,
         act_school="Track (400m). Tech theater crew, ran lighting for the spring musical.",
         act_comm="Helps his uncle on weekend residential electrical jobs.",
         goal="I want to be a licensed electrician. Running lights for our musical is what got me interested, and my uncle lets me help on weekend jobs. A contractor in Aurora said they'd take me on as an apprentice in June if I can pay for the first year of classroom hours and my tools.",
         other_aid="No other aid yet.",
         letters=[L("Ms. Rachel Kim", "Teacher", "West Aurora High School",
                    "Andre is the student I trust with the lighting board on opening night."),
                  L("Marcus Collins", "Other", "Family friend / electrician",
                    "Reliable, careful around live work, asks good questions.")],
         flag="standard",
         reasons=[F("Has an apprenticeship lined up", "A contractor in Aurora said they'd take me on as an apprentice in June"),
                  F("Some hands-on experience", "my uncle lets me help on weekend jobs")],
         recs={"s-trades": "tier1"},
         notes=[("s-trades", "Second letter is from a relative-ish family friend. Fine, but the teacher letter carries more weight.")],
         transcript=True, cost_est=True, days=55),

    dict(first="Priya", last="Nair", city="Aurora", zip="60504", school="Metea Valley",
         grad="May 2027", focus=HM, profession="Dental hygienist",
         level="Community college", year="1st year", start="August 2027",
         inst="College of DuPage, Dental Hygiene (AAS)", cost=8900,
         act_school="HOSA, Science Olympiad, orchestra (viola).",
         act_comm="Volunteer at a free dental clinic on Saturdays, front desk and sterilizing instruments.",
         goal="I want to be a dental hygienist. Volunteering at the free clinic showed me how many adults haven't seen a dentist in years and how much a good hygienist changes that visit. The COD program is competitive, so I'm finishing my prerequisites this spring.",
         other_aid="Applied to two local scholarships. Will file FAFSA.",
         letters=[L("Dr. Anita Shah, DDS", "Other", "Free dental clinic",
                    "Priya is calm with nervous patients and meticulous about sterilization."),
                  L("Mr. Tom Becker", "Teacher", "Metea Valley High School",
                    "One of the most organized students I've taught.")],
         flag="standard",
         reasons=[F("Relevant volunteer work", "Volunteer at a free dental clinic on Saturdays"),
                  F("Clear, specific program", "College of DuPage, Dental Hygiene (AAS)")],
         recs={}, notes=[], transcript=False, cost_est=True, days=40),

    dict(first="Caleb", last="Lindqvist", city="Geneva", zip="60134", school="Homeschooled",
         homeschool_area="Geneva", grad="June 2027", focus=BT, profession="HVAC technician",
         level="Community college", year="1st year", start="August 2027",
         inst="College of DuPage, HVAC certificate", cost=4600,
         act_school="Homeschool co-op robotics team. Took two dual-credit classes at Elgin CC.",
         act_comm="Works in his father's handyman business three days a week. Volunteers with a home-repair ministry.",
         goal="I've been working with my dad since I was fourteen. Most of the calls we turn down are HVAC because neither of us is certified. I want to get my HVAC certificate and my EPA 608 so we can take that work, and eventually run the business.",
         other_aid="None.",
         letters=[L("Grace Fellowship home-repair ministry", "Other", "Volunteer coordinator",
                    "Caleb has led three furnace and water-heater replacements for elderly homeowners this year."),
                  L("Mrs. Joan Ivers", "Teacher", "Homeschool co-op",
                    "Self-directed and practical.")],
         flag="read_first",
         reasons=[F("Has worked while in school", "Works in his father's handyman business three days a week"),
                  F("Specific goal tied to real demand", "Most of the calls we turn down are HVAC because neither of us is certified.")],
         recs={"s-trades": "tier1", "s-coach": "tier1"}, notes=[],
         transcript=True, cost_est=False, days=50),

    dict(first="Jordan", last="Pierce", city="Plano", zip="60545", school="My school isn't listed",
         homeschool_area="", grad="May 2027", focus=MF, profession="Machinist",
         level="Community college", year="1st year", start="August 2027",
         inst="Waubonsee Community College, Machine Tool Technology", cost=5000,
         act_school="Plano High School. Wrestling, shop class.",
         act_comm="Works at a grocery store 20 hours a week.",
         goal="I want to be a machinist. My grandpa was a tool and die maker and I like shop class more than anything else in school.",
         other_aid="None.",
         letters=[],
         flag="human_look",
         reasons=[F("School is not on the qualifying list", "Plano High School"),
                  F("No letters yet", "")],
         recs={"s-edu": "reviewed"},
         notes=[("s-edu", "Plano isn't one of our 13. Bob to decide whether 'not listed' students are ever eligible.")],
         transcript=False, cost_est=False, days=35),

    dict(first="Hannah", last="Okafor", city="Plainfield", zip="60586", school="Oswego East",
         grad="May 2027", focus=HM, profession="Registered nurse (BSN)",
         level="Undergraduate", year="1st year", start="August 2027",
         inst="Aurora University, Nursing (BSN)", cost=31000,
         act_school="National Honor Society, cross-country captain, Key Club.",
         act_comm="Lifeguard every summer since 15. Volunteers at a hospital gift shop.",
         goal="I want to be a pediatric nurse. My little sister spent three weeks in the NICU and the nurses were the ones who explained everything to my parents. I've been accepted to Aurora University's BSN program.",
         other_aid="AU merit scholarship $12,000/yr. FAFSA filed.",
         letters=[L("Coach Brian Ellis", "Teacher", "Oswego East High School", "A leader by example."),
                  L("Pool manager", "Employment supervisor", "Plainfield Park District", "Four summers, never a missed shift.")],
         flag="standard",
         reasons=[F("Clear goal and accepted to a program", "I've been accepted to Aurora University's BSN program."),
                  F("Steady job history", "Lifeguard every summer since 15.")],
         recs={"s-nurse": "tier2"},
         notes=[("s-nurse", "Strong applicant, already has a big merit award. Lives at the edge of the area (Plainfield).")],
         transcript=True, cost_est=True, days=30),

    dict(first="Kevin", last="Tran", city="Aurora", zip="60504", school="Waubonsie Valley",
         grad="May 2027", focus=MF, profession="Automation / mechatronics technician",
         level="Community college", year="1st year", start="August 2027",
         inst="Waubonsee Community College, Automation & Robotics", cost=5400,
         act_school="FIRST Robotics (build lead), math team.",
         act_comm="Repairs phones and laptops for neighbors.",
         goal="I want to work on the robots in factories, not just build competition ones. Waubonsee's automation program has a pathway into local plants.",
         other_aid="None.",
         letters=[L("Mr. Paul Grant", "Teacher", "Waubonsie Valley High School", "Kevin taught our freshmen how to wire the drivetrain.")],
         flag="standard",
         reasons=[F("Clear goal", "I want to work on the robots in factories"),
                  F("Relevant activity", "FIRST Robotics (build lead)")],
         recs={}, notes=[], transcript=False, cost_est=True, days=26, dup_of=None),

    dict(first="Kevin", last="Tran", city="Aurora", zip="60504", school="Waubonsie Valley",
         grad="May 2027", focus=MF, profession="Automation / mechatronics technician",
         level="Community college", year="1st year", start="August 2027",
         inst="Waubonsee Community College, Automation & Robotics", cost=5400,
         act_school="FIRST Robotics (build lead), math team.",
         act_comm="Repairs phones and laptops for neighbors. Started at a machine shop in January, 12 hrs/week.",
         goal="I want to work on the robots in factories, not just build competition ones. Waubonsee's automation program has a pathway into local plants. Since my first application I started part-time at a machine shop.",
         other_aid="None.",
         letters=[],
         flag="human_look",
         reasons=[F("Possible duplicate: same name and email as an earlier application", "Since my first application I started part-time at a machine shop."),
                  F("Newer version adds a job", "Started at a machine shop in January, 12 hrs/week.")],
         recs={}, notes=[], transcript=False, cost_est=True, days=6, dup=True),

    dict(first="Brianna", last="Scott", city="Batavia", zip="60510", school="Batavia",
         grad="May 2027", focus=MF, profession="CNC machinist",
         level="Community college", year="1st year", start="August 2027",
         inst="Waubonsee Community College, CNC Operator certificate", cost=4800,
         act_school="Softball, metals class.",
         act_comm="Babysits.",
         goal="I want to run CNC machines. We toured a plant in Batavia in metals class and I liked it.",
         other_aid="",
         letters=[],
         flag="human_look",
         reasons=[F("Incomplete: no letters and no cost estimate yet", ""),
                  F("Plan is short but specific", "Waubonsee Community College, CNC Operator certificate")],
         recs={}, notes=[], transcript=False, cost_est=False, days=12),

    dict(first="Elena", last="Ruiz", city="Aurora", zip="60506", school="Rosary College Prep",
         grad="May 2021", focus=HM, profession="Nurse practitioner (MSN)",
         level="Graduate", year="1st year", start="August 2027",
         inst="Aurora University, MSN (Family Nurse Practitioner)", cost=19000,
         act_school="BSN from NIU, 2025.",
         act_comm="RN on a med-surg floor in Aurora, full time. Volunteers at a parish health fair.",
         goal="I'm a med-surg nurse and I want to become a family nurse practitioner and work in a community clinic on Aurora's east side, where people wait weeks for a primary-care visit. My hospital covers part of tuition but not all of it.",
         other_aid="Employer tuition assistance $5,250/yr.",
         letters=[L("Nurse manager", "Employment supervisor", "Aurora hospital", "One of our most dependable nurses."),
                  L("Dr. Maria Flores", "Other", "Community clinic", "We'd hire her.")],
         flag="standard",
         reasons=[F("Graduate study, which Bob confirmed is included", "Aurora University, MSN (Family Nurse Practitioner)"),
                  F("Works full time in the field", "RN on a med-surg floor in Aurora, full time.")],
         recs={"s-nurse": "tier1"}, notes=[], transcript=True, cost_est=True, days=45),

    dict(first="Mike", last="Dombrowski", city="North Aurora", zip="60542", school="Aurora Christian",
         grad="May 2027", focus=BT, profession="Plumber",
         level="Vocational training", year="1st year", start="June 2027",
         inst="Plumbing apprenticeship, classroom at COD", cost=2800,
         act_school="Football.",
         act_comm="Works for my uncle's plumbing company summers.",
         goal="I want to be a plumber like my uncle. I've worked for him two summers.",
         other_aid="no",
         letters=[L("Steve Dombrowski", "Employment supervisor", "Plumbing company", "He works hard."),
                  L("Coach", "Teacher", "Aurora Christian", "Never late.")],
         flag="standard",
         reasons=[F("Short answer, but a specific goal and real work history", "I've worked for him two summers."),
                  F("Length and writing style are not used as signals", "")],
         recs={"s-trades": "tier2", "s-coach": "tier1"},
         notes=[("s-coach", "Short answer, but he's been working summers since freshman year. Don't let length count against him.")],
         transcript=True, cost_est=True, days=52),

    dict(first="Destiny", last="Harris", city="Aurora", zip="60505", school="East Aurora",
         grad="May 2025", focus=HM, profession="Surgical technologist",
         level="Community college", year="1st year", start="August 2027",
         inst="College of DuPage, Surgical Technology", cost=7600,
         act_school="Graduated 2025. Gap year working.",
         act_comm="Full-time at a warehouse since graduation, nights. Saved for a car.",
         goal="After graduation I took a year to work and figure it out. A friend's mom is a surgical tech and let me shadow her for a day. I want to be in the OR. I have a car now so I can get to COD.",
         other_aid="FAFSA filed.",
         letters=[L("Shift supervisor", "Employment supervisor", "Warehouse, Aurora", "Promoted to trainer in six months."),
                  L("Mrs. Ann Wells", "Teacher", "East Aurora High School", "Quietly determined.")],
         flag="read_first",
         reasons=[F("Gap year spent working, which Bob confirmed is fine", "Full-time at a warehouse since graduation"),
                  F("Did the research", "let me shadow her for a day")],
         recs={"s-nurse": "tier1", "s-edu": "tier1"}, notes=[], transcript=True, cost_est=True, days=48),

    dict(first="Sofia", last="Petrakis", city="Geneva", zip="60134", school="Geneva",
         grad="May 2027", focus=HM, profession="Radiologic technologist",
         level="Community college", year="1st year", start="August 2027",
         inst="College of DuPage, Radiography (AAS)", cost=6900,
         act_school="Volleyball, Spanish club.",
         act_comm="Volunteer at Northwestern Delnor gift shop.",
         goal="I broke my wrist playing volleyball and the X-ray tech explained every image to me. I want to do that job. COD's radiography program is two years and has clinicals at local hospitals.",
         other_aid="FAFSA.",
         letters=[L("Coach", "Teacher", "Geneva High School", "Great teammate.")],
         flag="standard",
         reasons=[F("Clear goal", "I want to do that job."),
                  F("Knows the program", "COD's radiography program is two years and has clinicals")],
         recs={}, notes=[], transcript=False, cost_est=True, days=22),

    dict(first="Ethan", last="Wolfe", city="Batavia", zip="60510", school="Batavia",
         grad="May 2027", focus=MF, profession="Industrial maintenance / automation tech",
         level="Community college", year="1st year", start="August 2027",
         inst="Waubonsee Community College, Industrial Maintenance", cost=5100,
         act_school="Robotics club, jazz band.",
         act_comm="Part-time at a manufacturing plant in Batavia through a youth apprenticeship, 16 hrs/week.",
         goal="Through my youth apprenticeship I work with the maintenance crew at a plant in Batavia. When a line goes down they're the ones everybody waits on. I want to be that person. The plant will keep me on part-time while I'm at Waubonsee.",
         other_aid="Employer pays $1,500 toward tuition.",
         letters=[L("Maintenance lead", "Employment supervisor", "Batavia plant", "Already troubleshooting PLC faults on his own."),
                  L("Mr. Greg Haas", "Teacher", "Batavia High School", "Curious and careful.")],
         flag="read_first",
         reasons=[F("Working in the field during school", "youth apprenticeship, 16 hrs/week"),
                  F("Employer is invested", "The plant will keep me on part-time while I'm at Waubonsee.")],
         recs={"s-mfg": "tier1"}, notes=[], transcript=True, cost_est=True, days=38),

    dict(first="Isaiah", last="Brooks", city="Aurora", zip="60506", school="Aurora Central Catholic",
         grad="May 2027", focus=BT, profession="Carpenter",
         level="Vocational training", year="1st year", start="June 2027",
         inst="Carpentry apprenticeship, classroom hours", cost=2600,
         act_school="Basketball, Habitat for Humanity club.",
         act_comm="Habitat builds most Saturdays.",
         goal="I've worked on eight Habitat houses. I want to be a carpenter and some day a superintendent.",
         other_aid="None.",
         letters=[L("Habitat site supervisor", "Other", "Fox Valley Habitat", "He's the first one on site.")],
         flag="standard",
         reasons=[F("Hands-on experience", "I've worked on eight Habitat houses."),
                  F("Clear goal", "I want to be a carpenter")],
         recs={"s-trades": "tier1"}, notes=[], transcript=True, cost_est=False, days=28),

    dict(first="Jasmine", last="Lee", city="Aurora", zip="60504", school="Waubonsie Valley",
         grad="May 2027", focus=HM, profession="Phlebotomist, then RN",
         level="Vocational training", year="1st year", start="June 2027",
         inst="Phlebotomy certificate (8 weeks), then Waubonsee nursing", cost=1400,
         act_school="HOSA, dance team.",
         act_comm="Works at a pharmacy register 15 hrs/week.",
         goal="I want to start working in a hospital right away as a phlebotomist and then go to nursing school while I work.",
         other_aid="None.",
         letters=[L("Pharmacy manager", "Employment supervisor", "Pharmacy, Aurora", "Trustworthy with customers and cash.")],
         flag="standard",
         reasons=[F("Step-by-step plan", "start working in a hospital right away as a phlebotomist and then go to nursing school"),
                  F("Holds a job", "Works at a pharmacy register 15 hrs/week.")],
         recs={}, notes=[], transcript=False, cost_est=True, days=18),

    dict(first="Gabriel", last="Santos", city="Oswego", zip="60543", school="Oswego",
         grad="May 2027", focus=MF, profession="Machinist / CNC programmer",
         level="Community college", year="1st year", start="August 2027",
         inst="Waubonsee Community College, Machine Tool Technology", cost=5000,
         act_school="Engineering club, soccer.",
         act_comm="Works at a machine shop in Montgomery after school, 18 hrs/week. Deburring and running a lathe.",
         goal="I already work in a machine shop. I want to learn programming so I'm not just loading parts. My boss said if I get through the machine tool program he'll move me to the programming side.",
         other_aid="None.",
         letters=[L("Shop owner", "Employment supervisor", "Machine shop, Montgomery", "Best young hand I've had in ten years."),
                  L("Ms. Carla Diaz", "Teacher", "Oswego High School", "Strong in geometry and very hands-on.")],
         flag="read_first",
         reasons=[F("Already working in the field", "Works at a machine shop in Montgomery after school, 18 hrs/week."),
                  F("Employer path", "he'll move me to the programming side")],
         recs={"s-mfg": "tier1", "s-coach": "tier1"},
         notes=[("bob", "This is the kid we're built for.")],
         final=("fund", 5000, "Waubonsee Community College"),
         transcript=True, cost_est=True, days=57),

    dict(first="Ava", last="Thompson", city="Aurora", zip="60506", school="West Aurora",
         grad="May 2027", focus=HM, profession="Medical assistant",
         level="Vocational training", year="1st year", start="August 2027",
         inst="Medical Assistant certificate", cost=3900,
         act_school="Choir, Best Buddies.",
         act_comm="Babysits for two families.",
         goal="I want to be a medical assistant at a pediatrician's office.",
         other_aid="None.",
         letters=[L("Choir director", "Teacher", "West Aurora High School", "Warm, responsible, organized.")],
         flag="standard",
         reasons=[F("Specific role", "a medical assistant at a pediatrician's office")],
         recs={}, notes=[], transcript=False, cost_est=False, days=15),

    dict(first="Diego", last="Hernandez", city="Aurora", zip="60505", school="East Aurora",
         grad="May 2027", focus=BT, profession="HVAC technician",
         level="Community college", year="1st year", start="August 2027",
         inst="Waubonsee Community College, HVAC", cost=4700,
         act_school="Auto shop, wrestling.",
         act_comm="Helper at an HVAC company 20 hrs/week since junior year. Translates for his parents.",
         goal="I've been a helper on HVAC trucks for a year and a half. I carry the tools and now the techs let me do the simple calls with them. I want my certificate so I can be a tech, not a helper. The company says they'll pay for my EPA test.",
         other_aid="Company pays EPA 608 test.",
         letters=[L("Service manager", "Employment supervisor", "HVAC company, Aurora", "Customers like him. He listens."),
                  L("Mr. Ray Lopez", "Teacher", "East Aurora High School", "Best mechanical sense in the class.")],
         flag="read_first",
         reasons=[F("Held a job in the trade through school", "Helper at an HVAC company 20 hrs/week since junior year."),
                  F("Clear next step", "I want my certificate so I can be a tech, not a helper.")],
         recs={"s-trades": "tier1"}, notes=[], transcript=True, cost_est=True, days=33),

    dict(first="Grace", last="Kim", city="Aurora", zip="60504", school="Metea Valley",
         grad="May 2027", focus=HM, profession="Licensed practical nurse, then RN",
         level="Community college", year="1st year", start="August 2027",
         inst="Waubonsee Community College, Practical Nursing (LPN)", cost=5600,
         act_school="Took the CNA course at Fox Valley Career Center.",
         act_comm="CNA at a nursing home, weekends.",
         goal="I got my CNA through the career center and I work weekends at a nursing home. I want to be an LPN in a year and then bridge to RN.",
         other_aid="FAFSA.",
         letters=[L("Director of nursing", "Employment supervisor", "Nursing home, Aurora", "Residents ask for her."),
                  L("CNA instructor", "Teacher", "Fox Valley Career Center", "Top of her cohort.")],
         flag="read_first",
         reasons=[F("Working in the field", "CNA at a nursing home, weekends."),
                  F("Realistic ladder", "LPN in a year and then bridge to RN")],
         recs={}, notes=[], transcript=True, cost_est=True, days=20),

    dict(first="Logan", last="Meyer", city="Maple Park", zip="60151", school="Kaneland",
         grad="May 2027", focus=MF, profession="Industrial maintenance technician",
         level="Community college", year="1st year", start="August 2027",
         inst="Waubonsee Community College, Industrial Maintenance", cost=5100,
         act_school="Baseball.",
         act_comm="Works on the family farm.",
         goal="I fix most of the equipment on our farm and want to do maintenance at a plant.",
         other_aid="None.",
         letters=[L("Neighbor / farmer", "Other", "", "Can fix anything.")],
         flag="standard",
         reasons=[F("Mechanical experience", "I fix most of the equipment on our farm")],
         recs={}, notes=[], transcript=False, cost_est=False, days=10),

    dict(first="Riley", last="Adams", city="Geneva", zip="60134", school="Geneva",
         grad="May 2027", focus=HM, profession="Not sure yet: nursing or welding",
         level="Community college", year="1st year", start="Fall 2027",
         inst="Waubonsee or COD", cost=None,
         act_school="Art club.",
         act_comm="Works at a coffee shop.",
         goal="I don't really know yet. Maybe nursing because my aunt is a nurse, or maybe welding because I like making things. I just know I don't want a four-year school.",
         other_aid="",
         letters=[L("Coffee shop manager", "Employment supervisor", "Geneva", "Dependable, great with customers.")],
         flag="human_look",
         reasons=[F("No program chosen yet", "I don't really know yet."),
                  F("No cost estimate to work from", "")],
         recs={"s-edu": "reviewed"},
         notes=[("s-edu", "Worth a follow-up call. Bob's line: 'pick something.' Could reapply once a program is chosen.")],
         transcript=False, cost_est=False, days=8),

    dict(first="Marcus", last="Johnson", city="Yorkville", zip="60560", school="Oswego",
         grad="May 2027", focus=BT, profession="Operating engineer",
         level="Vocational training", year="1st year", start="June 2027",
         inst="Operating engineers apprenticeship, classroom", cost=2900,
         act_school="Football (lineman), shop.",
         act_comm="Summer job with an excavating company running a skid steer.",
         goal="I ran a skid steer for an excavating company last summer and I want to run the big equipment. The company will sponsor me into the apprenticeship.",
         other_aid="None.",
         letters=[L("Foreman", "Employment supervisor", "Excavating company", "Safe operator, good attitude.")],
         flag="standard",
         reasons=[F("Employer sponsorship", "The company will sponsor me into the apprenticeship."),
                  F("Experience", "I ran a skid steer for an excavating company last summer")],
         recs={"s-trades": "tier2"},
         notes=[("s-trades", "Good kid. Lives in Yorkville, which is edge-of-area on the placeholder ZIP list.")],
         transcript=True, cost_est=True, days=25),

    dict(first="Leah", last="Novak", city="Batavia", zip="60510", school="Rosary College Prep",
         grad="May 2027", focus=HM, profession="Surgical technologist",
         level="Community college", year="1st year", start="August 2027",
         inst="College of DuPage, Surgical Technology", cost=7600,
         act_school="Student council, lacrosse.",
         act_comm="Hostess at a restaurant.",
         goal="I want to be a surgical tech. I like anatomy and I stay calm under pressure.",
         other_aid="FAFSA.",
         letters=[L("Science teacher", "Teacher", "Rosary College Prep", "Excellent in anatomy.")],
         flag="standard",
         reasons=[F("Clear goal", "I want to be a surgical tech.")],
         recs={}, notes=[], transcript=False, cost_est=True, days=14),

    dict(first="Samantha", last="Cruz", city="Aurora", zip="60504", school="Waubonsie Valley",
         grad="May 2027", focus=BT, profession="Electrician",
         level="Community college", year="1st year", start="August 2027",
         inst="Waubonsee Community College, Electrical Construction", cost=4900,
         act_school="Girls in STEM club president, softball.",
         act_comm="Summer job with an electrical contractor pulling wire.",
         goal="Last summer I pulled wire on a new school build and the journeyman let me terminate devices by the end. I was the only girl on the site and I loved it. I want to be a licensed electrician.",
         other_aid="None.",
         letters=[L("Journeyman electrician", "Employment supervisor", "Electrical contractor", "Faster learner than most first-years."),
                  L("Ms. Jen Park", "Teacher", "Waubonsie Valley High School", "A natural leader.")],
         flag="read_first",
         reasons=[F("Worked in the trade", "Summer job with an electrical contractor pulling wire."),
                  F("Specific goal", "I want to be a licensed electrician.")],
         recs={}, notes=[], transcript=True, cost_est=True, days=3),

    dict(first="Omar", last="Haddad", city="Aurora", zip="60506", school="West Aurora",
         grad="May 2027", focus=HM, profession="Respiratory therapist",
         level="Community college", year="1st year", start="August 2027",
         inst="College of DuPage, Respiratory Care", cost=7200,
         act_school="Debate, Muslim Student Association.",
         act_comm="Helps care for his grandfather, who uses oxygen at home.",
         goal="(Uploaded as a file.)",
         goal_file=True,
         other_aid="FAFSA.",
         letters=[L("Debate coach", "Teacher", "West Aurora High School", "Thoughtful and persistent.")],
         flag="human_look",
         reasons=[F("Career goal was uploaded as a file the reader couldn't open", ""),
                  F("Relevant family caregiving", "Helps care for his grandfather, who uses oxygen at home.")],
         recs={}, notes=[], transcript=False, cost_est=True, days=2),

    dict(first="Nate", last="Sullivan", city="Batavia", zip="60510", school="Marmion Academy",
         grad="May 2027", focus=BT, profession="Pipefitter",
         level="Vocational training", year="1st year", start="June 2027",
         inst="Pipefitting apprenticeship, classroom hours", cost=3000,
         act_school="Hockey, ROTC.",
         act_comm="Landscaping crew summers.",
         goal="I want to be a pipefitter. I like working outside and with my hands, and I want a trade that pays well without debt.",
         other_aid="None.",
         letters=[L("Landscaping owner", "Employment supervisor", "Batavia", "Shows up, works hard, no complaints."),
                  L("ROTC instructor", "Teacher", "Marmion Academy", "Disciplined.")],
         flag="standard",
         reasons=[F("Clear goal", "I want to be a pipefitter."),
                  F("Work history", "Landscaping crew summers.")],
         recs={"s-trades": "tier2"}, notes=[], transcript=True, cost_est=False, days=31),

    dict(first="Lily", last="Chen", city="Sugar Grove", zip="60554", school="Kaneland",
         grad="May 2027", focus=MF, profession="Quality technician",
         level="Community college", year="1st year", start="August 2027",
         inst="Waubonsee Community College, Manufacturing Technology", cost=4900,
         act_school="Math team, yearbook.",
         act_comm="Part-time at a parts supplier's inspection lab, 10 hrs/week.",
         goal="I measure parts with calipers and a CMM at my part-time job and I want to become a quality technician. Waubonsee's program includes metrology.",
         other_aid="None.",
         letters=[L("Quality manager", "Employment supervisor", "Parts supplier", "Precise and reliable.")],
         flag="read_first",
         reasons=[F("Working in the field", "Part-time at a parts supplier's inspection lab"),
                  F("Specific role and program", "become a quality technician")],
         recs={}, notes=[], transcript=False, cost_est=True, days=9),
]


def app_id(i):
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "JCD-27-" + "".join(rng.choice(chars) for _ in range(6))


def main():
    # 1. Clear previous sample rows (cascades to letters, notes, recommendations, overrides).
    req("DELETE", "review_applications?is_sample=is.true")
    req("DELETE", "review_audit?is_sample=is.true")
    req("DELETE", "review_reviewers?is_sample=is.true")

    # 2. Reviewers (Bob and Gary are real and kept; sample reviewers are marked).
    req("POST", "review_reviewers?on_conflict=id", REVIEWERS,
        prefer="resolution=merge-duplicates,return=minimal")

    # 3. Placeholder distance-tier ZIPs (only if Bob hasn't set real ones).
    existing = req("GET", "review_settings?key=eq.zip_tiers&select=value", prefer="")
    if not existing or existing[0]["value"].get("placeholder"):
        req("POST", "review_settings?on_conflict=key", [{"key": "zip_tiers", "value": ZIP_TIERS}],
            prefer="resolution=merge-duplicates,return=minimal")

    # Sample dates run up to the moment the script is run, so anything a
    # tester does afterwards sorts after the sample history, not before it.
    now = datetime.now(timezone.utc).replace(microsecond=0) - timedelta(hours=1)
    apps, letters, recs, notes, overrides, audit = [], [], [], [], [], []
    first_tran = None

    for i, a in enumerate(APPS):
        aid = app_id(i)
        submitted = now - timedelta(days=a["days"], hours=rng.randint(0, 20), minutes=rng.randint(0, 59))
        email = f"{a['first'].lower()}.{a['last'].lower()}@example.com"
        if a["first"] == "Kevin" and a["last"] == "Tran":
            if first_tran is None:
                first_tran = aid
        data = {
            "app_id": aid, "first": a["first"], "last": a["last"], "email": email,
            "phone": f"(630) 555-{rng.randint(100, 999):04d}", "addr1": f"{rng.randint(100, 2999)} Sample St",
            "city": a["city"], "state": "IL", "zip": a["zip"], "school": a["school"],
            "homeschool_area": a.get("homeschool_area", ""), "grad_date": a["grad"],
            "activities_school": a["act_school"], "activities_community": a["act_comm"],
            "focus_area": a["focus"], "profession": a["profession"],
            "career_goal": "" if a.get("goal_file") else a["goal"],
            "career_goal_file": "career-goal.docx (sample: could not be opened)" if a.get("goal_file") else "",
            "study_level": a["level"], "study_year": a["year"], "start_date": a["start"],
            "institution": a["inst"], "annual_cost": a["cost"],
            "aid_contact": "Financial aid office", "aid_email": "finaid@example.edu",
            "other_aid": a["other_aid"],
            "letter1_name": a["letters"][0]["rec_name"] if a["letters"] else "",
            "letter2_name": a["letters"][1]["rec_name"] if len(a["letters"]) > 1 else "",
            "transcript_requested": (submitted - timedelta(days=1)).date().isoformat(),
            "certify": "yes", "signature": f"{a['first']} {a['last']}", "SAMPLE": True,
        }
        final = a.get("final")
        apps.append(dict(
            id=aid, submitted_at=submitted.isoformat(), first_name=a["first"], last_name=a["last"],
            email=email, phone=data["phone"], addr1=data["addr1"], city=a["city"], zip=a["zip"],
            school=a["school"], homeschool_area=a.get("homeschool_area") or None, grad_date=a["grad"],
            focus_area=a["focus"], profession=a["profession"], study_level=a["level"],
            institution=a["inst"], annual_cost=a["cost"], data=data,
            transcript_received=a["transcript"], cost_estimate_received=a["cost_est"],
            urgent=a.get("urgent", False), urgent_note=a.get("urgent_note"),
            ai_flag=a["flag"], ai_reasons=a["reasons"], ai_model=MODEL,
            final_decision=final[0] if final else None,
            award_amount=final[1] if final else None,
            payee=final[2] if final else None,
            decided_by="bob" if final else None,
            decided_at=(now - timedelta(days=1)).isoformat() if final else None,
            is_sample=True,
        ))
        for k, l in enumerate(a["letters"]):
            letters.append(dict(app_id=aid, received_at=min(now, submitted + timedelta(days=3 + k * 2)).isoformat(), **l))
        for who, rec in a["recs"].items():
            at = min(now, submitted + timedelta(days=rng.randint(1, max(1, a["days"] - 1))))
            recs.append(dict(app_id=aid, reviewer_id=who, recommendation=rec, updated_at=at.isoformat()))
            audit.append(dict(at=at.isoformat(), actor=who, app_id=aid, action="recommendation",
                              detail={"recommendation": rec}, is_sample=True))
        for k, (who, body) in enumerate(a["notes"]):
            at = min(now, submitted + timedelta(days=1 + k, hours=rng.randint(1, 9)))
            notes.append(dict(app_id=aid, reviewer_id=who, body=body, created_at=at.isoformat()))
            audit.append(dict(at=at.isoformat(), actor=who, app_id=aid, action="note",
                              detail={"length": len(body)}, is_sample=True))
        if final:
            audit.append(dict(at=(now - timedelta(days=1)).isoformat(), actor="bob", app_id=aid,
                              action="final_decision",
                              detail={"final_decision": final[0], "award_amount": final[1], "payee": final[2]},
                              is_sample=True))
        if a.get("urgent"):
            audit.append(dict(at=(submitted + timedelta(hours=5)).isoformat(), actor="gary", app_id=aid,
                              action="urgent", detail={"value": True, "note": a.get("urgent_note")}, is_sample=True))

    # One sample "I disagree with the flag": the short-answer plumber.
    mike = next(x for x in apps if x["first_name"] == "Mike")
    overrides.append(dict(app_id=mike["id"], reviewer_id="s-coach",
                          reason="Should be 'read first'. Two summers working in the trade outweighs a short answer.",
                          created_at=(now - timedelta(days=3)).isoformat()))
    audit.append(dict(at=(now - timedelta(days=3)).isoformat(), actor="s-coach", app_id=mike["id"],
                      action="flag_override", detail={"reason": overrides[0]["reason"]}, is_sample=True))

    req("POST", "review_applications", apps)
    req("POST", "review_letters", letters)
    req("POST", "review_recommendations", recs)
    req("POST", "review_notes", notes)
    req("POST", "review_flag_overrides", overrides)
    req("POST", "review_audit", audit)
    print(f"Loaded {len(apps)} sample applications, {len(letters)} letters, {len(recs)} recommendations, "
          f"{len(notes)} notes, {len(audit)} audit rows.")


if __name__ == "__main__":
    main()
