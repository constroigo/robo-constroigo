"""Transforma um card (post.jpg) em Reel 9:16 com a vinheta padrão."""
import os
import subprocess
from pathlib import Path

MUSICA = Path("assets/musica/vinheta.mp3")
DURACAO = 12  # segundos
FUNDO = "0x0f2240"  # azul-marinho da marca


def ativo() -> bool:
    """Alterna: um post de card único sai como Reel, o seguinte como imagem, e assim por diante.
    REELS_COM_MUSICA=sempre força todos; =nao desliga."""
    modo = os.environ.get("REELS_COM_MUSICA", "alternar").lower()
    if modo == "nao" or not MUSICA.exists():
        return False
    if modo == "sempre":
        return True
    def quando(p: Path) -> str:  # pasta = AAAA-MM-DD-horario-HHMMSS
        partes = p.name.split("-")
        return "-".join(partes[:3]) + partes[-1]
    pastas = sorted((p for p in Path("posts").glob("*") if p.is_dir() and (p / "post.json").exists()
                     and not list(p.glob("post-*.jpg"))), key=quando)
    ultimo_foi_reel = bool(pastas) and (pastas[-1] / "video.mp4").exists()
    return not ultimo_foi_reel


def _ffmpeg() -> str:
    import shutil
    if shutil.which("ffmpeg"):
        return "ffmpeg"
    import imageio_ffmpeg  # binário estático, para o runner do GitHub
    return imageio_ffmpeg.get_ffmpeg_exe()


def gerar(imagem: Path, destino: Path) -> Path | None:
    """Card 1080x1350 centralizado num quadro 1080x1920, zoom leve e música com fade."""
    filtro = (
        f"[0:v]scale=1080:1350,zoompan=z='min(zoom+0.0006,1.06)':d={DURACAO * 30}"
        f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1350:fps=30[card];"
        f"color=c={FUNDO}:s=1080x1920:d={DURACAO}[bg];"
        f"[bg][card]overlay=0:285,format=yuv420p[v];"
        f"[1:a]atrim=0:{DURACAO},afade=t=out:st={DURACAO - 1.5}:d=1.5[a]"
    )
    cmd = [_ffmpeg(), "-y", "-loglevel", "error", "-loop", "1", "-i", str(imagem), "-i", str(MUSICA),
           "-filter_complex", filtro, "-map", "[v]", "-map", "[a]", "-t", str(DURACAO),
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-c:a", "aac", "-b:a", "160k",
           "-movflags", "+faststart", str(destino)]
    try:
        subprocess.run(cmd, check=True, timeout=300)
        return destino
    except Exception as erro:  # sem vídeo, o post sai como imagem normal
        print(f"Vídeo não gerado ({erro}); segue como imagem.")
        return None
