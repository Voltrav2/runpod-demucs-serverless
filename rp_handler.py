import runpod
import subprocess
import shutil
import os
import torch

def handler(event):
    """ RunPod Serverless API için Demucs işleyici fonksiyonu """
    job_id = event['id']
    audio_url = event['input']['audio_url']

    # Müzik dosyasını indir
    os.system(f"wget -O musics/{job_id}.mp3 {audio_url}")

    # Demucs ile ayrıştırma işlemi
    subprocess.run([
        "demucs",
        "--mp3",
        "--two-stems",
        "vocals",
        "-n",
        "mdx_extra",
        f"musics/{job_id}.mp3",
        "-o",
        "musics"
    ])

    # Çıktıları taşı
    output_path = f"musics/{job_id}"
    os.makedirs(output_path, exist_ok=True)
    
    shutil.move(f"musics/mdx_extra/{job_id}/vocals.mp3", f"{output_path}/vocals.mp3")
    shutil.move(f"musics/mdx_extra/{job_id}/no_vocals.mp3", f"{output_path}/no_vocals.mp3")
    shutil.rmtree(f"musics/mdx_extra")

    torch.cuda.empty_cache()

    return {
        "vocal_path": f"{output_path}/vocals.mp3",
        "no_vocal_path": f"{output_path}/no_vocals.mp3"
    }

if __name__ == '__main__':
    runpod.serverless.start({'handler': handler})
