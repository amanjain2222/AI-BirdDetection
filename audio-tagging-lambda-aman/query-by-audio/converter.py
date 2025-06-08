import base64

def wav_to_base64(wav_file_path):
    with open(wav_file_path, 'rb') as wav_file:
        wav_bytes = wav_file.read()
        base64_bytes = base64.b64encode(wav_bytes)
        base64_string = base64_bytes.decode('utf-8')
        return base64_string

# Example usage:
wav_path = 'test2.wav'
base64_str = wav_to_base64(wav_path)
print(base64_str)


## IGNORE: (USED FOR LOCAL TESTING AND BUILDING A TEST AUDIO FILE)

# import subprocess
# import base64
# import os

# # Config
# INPUT_WAV = "test2.wav"  # Your starting audio file
# TRIMMED_WAV = "trimmed.wav"
# FINAL_CLIP_WAV = "clip.wav"
# BASE64_OUTPUT = "audio_base64.txt"

# # 1️⃣ Trim silence (leading and trailing)
# print("👉 Removing silence...")
# subprocess.run([
#     "ffmpeg",
#     "-y",
#     "-i", INPUT_WAV,
#     "-af", "silenceremove=start_periods=1:start_threshold=-50dB:detection=peak,areverse,silenceremove=start_periods=1:start_threshold=-50dB:detection=peak,areverse",
#     TRIMMED_WAV
# ], check=True)

# # 2️⃣ Optionally cut clip (skip first second, take 3 seconds)
# print("👉 Cutting clean clip (optional)...")
# subprocess.run([
#     "ffmpeg",
#     "-y",
#     "-i", TRIMMED_WAV,
#     "-ss", "00:00:01",    # skip 1 sec at start
#     "-t", "3",            # take 3 sec
#     FINAL_CLIP_WAV
# ], check=True)

# # 3️⃣ Encode to Base64
# print("👉 Encoding to Base64...")
# with open(FINAL_CLIP_WAV, "rb") as f:
#     encoded = base64.b64encode(f.read()).decode("utf-8")

# # 4️⃣ Save Base64 string to txt
# with open(BASE64_OUTPUT, "w") as f:
#     f.write(encoded)

# print(f"✅ Done! Base64 saved to {BASE64_OUTPUT}")
# print(f"👉 Length of Base64 string: {len(encoded)} chars")
