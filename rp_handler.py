import runpod
import demucs.separate
import os
import requests
import shutil

def handler(event):
    input_audio = event['input'].get('audio')

    if not input_audio:
        return {"error": "Audio URL is missing."}

    job_id = event.get("id", "unknown_job")
    local_audio_path = f"/tmp/{job_id}.mp3"

    # Dosyayı indir
    try:
        response = requests.get(input_audio, stream=True)
        if response.status_code == 200:
            with open(local_audio_path, "wb") as audio_file:
                for chunk in response.iter_content(chunk_size=8192):
                    audio_file.write(chunk)
        else:
            return {"error": "Failed to download audio file."}
    except Exception as e:
        return {"error": f"Error downloading file: {str(e)}"}

    # Demucs işlemi
    output_folder = "/app/separated"
    os.system(f"demucs -o {output_folder} {local_audio_path}")

    # Yeni çıkış dizinini kontrol et
    expected_path = f"{output_folder}/htdemucs/{job_id}"
    old_expected_path = f"{output_folder}/mdx_extra/{job_id}"  # Eski model olabilir

    # Hangi dizinde dosyalar var, onu kontrol et
    if os.path.exists(expected_path):
        vocal_path = f"{expected_path}/vocals.wav"
        no_vocal_path = f"{expected_path}/no_vocals.wav"
    elif os.path.exists(old_expected_path):
        vocal_path = f"{old_expected_path}/vocals.wav"
        no_vocal_path = f"{old_expected_path}/no_vocals.wav"
    else:
        return {"error": "Demucs output files not found."}

    # Çıktıları yeni bir dizine taşıyalım
    output_path = f"/app/musics/{job_id}"
    os.makedirs(output_path, exist_ok=True)

    try:
        shutil.move(vocal_path, f"{output_path}/vocals.mp3")
        shutil.move(no_vocal_path, f"{output_path}/no_vocals.mp3")
    except FileNotFoundError:
        return {"error": "Expected output files are missing after separation."}

    return {
        "vocal": f"{output_path}/vocals.mp3",
        "no_vocal": f"{output_path}/no_vocals.mp3"
    }

if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
