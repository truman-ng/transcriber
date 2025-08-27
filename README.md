# transcriber
/bin/zsh -c 'set -euo pipefail; P="$HOME/Downloads/transcriber"; cd "$P"; V="$P/.venv/bin/python"; mkdir -p "$P/data/out" "$P/data"; touch "$P/urls.txt"; URL="https://www.youtube.com/watch?v=5lWLLD3fTM4"; grep -qxF "$URL" "$P/urls.txt" || echo "$URL" >> "$P/urls.txt"; COOKIES="$P/cookies.txt" EXTRACTOR_ARGS="youtube:player_client=web" OUT_DIR="$P/data/out" ARCHIVE="$P/data/archive.txt" URLS_FILE="$P/urls.txt" "$V" app.py'

导出 cookies.txt（用这个 profile）
cd ~/Downloads/transcriber
./.venv/bin/python export_youtube_cookies.py \
  --browser firefox \
  --cookie-file "/Users/nixonfaud/Library/Application Support/Firefox/Profiles/yxpahkkf.default-release/cookies.sqlite" \
  --outfile ./cookies.txt

验证这份 cookies 能否看该会员视频
URL='https://www.youtube.com/watch?v=mnNhQVKCT2M'
yt-dlp --cookies ./cookies.txt --extractor-args "youtube:player_client=web" -F "$URL"

/bin/zsh -c 'set -euo pipefail; P="$HOME/Downloads/transcriber"; cd "$P"; V="$P/.venv/bin/python"; mkdir -p "$P/data/out" "$P/data"; COOKIES="$P/cookies.txt" EXTRACTOR_ARGS="youtube:player_client=web" OUT_DIR="$P/data/out" ARCHIVE="$P/data/archive.txt" URLS_FILE="$P/urls.txt" "$V" app.py'


