import re, requests, speech_recognition as sr

SERVER = 'http://127.0.0.1:3000'

# Map words→digits for numbers one–four
word_to_digit = {'one':'1','two':'2','three':'3','four':'4','to':'2'}
def normalize(text):
    for w,d in word_to_digit.items():
        text = re.sub(rf'\b{w}\b', d, text, flags=re.IGNORECASE)
    return text

# Patterns
onoff_re    = re.compile(r'relay\s*(1|2|3|4)\s*(on|off)', re.IGNORECASE)
bright_re   = re.compile(r'relay\s*(1|2|3|4)\s*brightness\s*(\d{1,3})', re.IGNORECASE)

r = sr.Recognizer()
mic = sr.Microphone()

print("Say commands like “relay 2 on”, “relay 3 brightness 50”, or “state”")

while True:
    with mic as src:
        r.adjust_for_ambient_noise(src, duration=1)
        print("Listening…")
        audio = r.listen(src)
    try:
        heard = r.recognize_google(audio).lower()
        print("Heard:", heard)
    except sr.UnknownValueError:
        print("⚠️ Could not understand. Try again.")
        continue
    except sr.RequestError as e:
        print("⚠️ API error:", e)
        break

    cmd = normalize(heard)

    # 1) STATE command
    if 'state' in cmd:
        try:
            resp = requests.get(f"{SERVER}/status")
            states = resp.json()
            print("Current States:")
            for id,st in states.items():
                onoff = "ON" if st['on'] else "OFF"
                print(f" Relay {id}: {onoff}, Brightness {st['brightness']}%")
        except Exception as e:
            print("⚠️ Failed to fetch status:", e)
        continue

    # 2) ON/OFF command
    m = onoff_re.search(cmd)
    if m:
        id, action = m.groups()
        try:
            resp = requests.get(f"{SERVER}/relay/{id}/{action}")
            data = resp.json()
            print(f"✅ Relay {id} → {'ON' if data['on'] else 'OFF'}, Brightness {data['brightness']}%")
        except Exception as e:
            print("⚠️ Command failed:", e)
        continue

    # 3) BRIGHTNESS command
    m = bright_re.search(cmd)
    if m:
        id, val = m.groups()
        val = max(0, min(100, int(val)))  # clamp 0–100
        try:
            resp = requests.get(f"{SERVER}/relay/{id}/brightness/{val}")
            data = resp.json()
            print(f"✅ Relay {id} brightness set to {data['brightness']}% → {'ON' if data['on'] else 'OFF'}")
        except Exception as e:
            print("⚠️ Command failed:", e)
        continue

    print("⚠️ Unrecognized command format.")
