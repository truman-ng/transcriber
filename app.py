import os, sys, subprocess, glob, shlex, json, time, pathlib

BASE = os.path.abspath(os.getenv("BASE_DIR", os.getcwd()))
OUT_DIR   = os.getenv("OUT_DIR",   os.path.join(BASE, "data", "out"))
ARCHIVE   = os.getenv("ARCHIVE",   os.path.join(BASE, "data", "archive.txt"))
EXTRACTOR_ARGS = os.getenv("EXTRACTOR_ARGS", "youtube:player_client=web")
COOKIES       = os.getenv("COOKIES", os.path.join(BASE, "cookies.txt"))

# 正确的 urls.txt 路径（在项目根目录）
URLS_FILE = os.getenv("URLS_FILE", os.path.join(BASE, "urls.txt"))

MODEL     = os.getenv("MODEL",     "large-v3")
LANG      = os.getenv("LANG",      "")
FORMATS   = os.getenv("FORMATS",   "txt,srt")
KEEP_WAV  = os.getenv("KEEP_WAV",  "0") == "1"

def run(cmd:list, cwd=None):
    print(">>", " ".join(shlex.quote(c) for c in cmd), flush=True)
    p = subprocess.Popen(cmd, cwd=cwd)
    p.communicate()
    if p.returncode != 0:
        raise SystemExit(f"command failed: {' '.join(cmd)}")

def ensure_dirs():
    pathlib.Path(OUT_DIR).mkdir(parents=True, exist_ok=True)
    pathlib.Path(os.path.dirname(ARCHIVE)).mkdir(parents=True, exist_ok=True)

def read_urls():
    if not os.path.exists(URLS_FILE):
        print(f"[WARN] URLs file not found: {URLS_FILE}")
        return []
    urls=[]
    for line in open(URLS_FILE, "r", encoding="utf-8"):
        s=line.strip()
        if not s or s.startswith("#"): continue
        urls.append(s)
    return urls

def list_new_media(before_paths:set):
    now=set(pathlib.Path(p).resolve() for p in glob.glob(f"{OUT_DIR}/**/*.m4a", recursive=True))
    return list(now - before_paths)

def convert_and_transcribe(m4a_path:str):
    base = os.path.splitext(m4a_path)[0]
    wav  = base + ".wav"

    # 1) 转 wav（16k/1ch）
    run(["ffmpeg", "-y", "-i", m4a_path, "-ar", "16000", "-ac", "1", wav])

    # 2) faster-whisper 转写
    #    pip 包自带 CLI: from faster_whisper import transcribe 也可，但用 ffw CLI 简洁
    #    这里直接调用 Python 小段实现，输出 txt 与 srt（必要时也可 vtt）
    from faster_whisper import WhisperModel
    model = WhisperModel(MODEL, device="cpu", compute_type="int8")  # 服务器无GPU用 int8/float16
    segments, info = model.transcribe(wav, vad_filter=True, language=(LANG or None))

    def write_txt(path):
        with open(path, "w", encoding="utf-8") as f:
            for s in segments:
                f.write(f"[{s.start:.2f}-{s.end:.2f}] {s.text}\n")

    def write_srt(path):
        def srt_ts(t):
            h=int(t//3600); m=int((t%3600)//60); s=int(t%60); ms=int((t-int(t))*1000)
            return f"{h:02}:{m:02}:{s:02},{ms:03}"
        with open(path, "w", encoding="utf-8") as f:
            i=1
            # segments 被消费一次后需要重跑，故转换为列表
            segs = list(segments)
            for s in segs:
                f.write(str(i) + "\n")
                f.write(srt_ts(s.start)+" --> "+srt_ts(s.end)+"\n")
                f.write(s.text.strip()+"\n\n")
                i+=1

    exts = [x.strip().lower() for x in FORMATS.split(",") if x.strip()]
    if "txt" in exts: write_txt(base+".txt")
    if "srt" in exts: write_srt(base+".srt")
    if "vtt" in exts:  # 简单 VTT
        with open(base+".vtt", "w", encoding="utf-8") as f:
            f.write("WEBVTT\n\n")
            def vtt_ts(t):
                h=int(t//3600); m=int((t%3600)//60); s=t%60
                return f"{h:02}:{m:02}:{s:06.3f}"
            for s in list(segments):
                f.write(f"{vtt_ts(s.start)} --> {vtt_ts(s.end)}\n{s.text.strip()}\n\n")

    if not KEEP_WAV:
        try: os.remove(wav)
        except: pass

def main():
    ensure_dirs()
    urls = read_urls()
    if not urls:
        print("[INFO] no URLs to process, exit.")
        return

    before=set(pathlib.Path(p).resolve() for p in glob.glob(f"{OUT_DIR}/**/*.m4a", recursive=True))

    ytdlp_common = [
        "yt-dlp",
        "--cookies", COOKIES,
        "--no-color",
        "--ignore-errors",
        "--no-part",
        "--download-archive", ARCHIVE,
        "-f", "bestaudio/best",
        "-x", "--audio-format", "m4a",
        "-o", f"{OUT_DIR}/%(uploader)s/%(upload_date)s - %(title)s-%(id)s.%(ext)s",
    ]

    for url in urls:
        run(ytdlp_common + [url])

    new_files = list_new_media(before)
    print(f"[INFO] new audio files: {len(new_files)}")
    for p in sorted(new_files):
        print(f"[INFO] transcribing: {p}")
        convert_and_transcribe(str(p))

if __name__ == "__main__":
    main()
