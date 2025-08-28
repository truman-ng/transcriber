# transcriber
P="$HOME/Downloads/transcriber"
cd "$P"

# 确认用的是 3.12 的 venv
"$P/.venv/bin/python" -V

# 强制安装 yt-dlp 最新 master（修 nsig 和一堆 web 客户端问题）
"$P/.venv/bin/python" -m pip install -U --force-reinstall \
  "yt-dlp @ https://github.com/yt-dlp/yt-dlp/archive/master.tar.gz"

# 确认版本命令（注意是 --version）
"$P/.venv/bin/yt-dlp" --version

# 导出 cookies.txt（用这个 profile）
cd ~/Downloads/transcriber
./.venv/bin/python export_youtube_cookies.py \
  --browser firefox \
  --cookie-file "/Users/nixonfaud/Library/Application Support/Firefox/Profiles/yxpahkkf.default-release/cookies.sqlite" \
  --outfile ./cookies.txt

# 验证这份 cookies 能否看该会员视频
URL='https://www.youtube.com/watch?v=XxoLgy5yo8o'
yt-dlp --cookies ./cookies.txt --extractor-args "youtube:player_client=web" -F "$URL"


## cookies.txt
/bin/zsh -c 'set -euo pipefail; P="$HOME/Downloads/transcriber"; cd "$P"; V="$P/.venv/bin/python"; mkdir -p "$P/data/out" "$P/data"; COOKIES="$P/cookies.txt" EXTRACTOR_ARGS="youtube:player_client=web" OUT_DIR="$P/data/out" ARCHIVE="$P/data/archive.txt" URLS_FILE="$P/urls.txt" "$V" app.py'

# cookies.slim.txt
P="$HOME/Downloads/transcriber"
cd "$P"
"$P/.venv/bin/yt-dlp" --version

/bin/zsh -c "set -e; P=\"$HOME/Downloads/transcriber\"; cd \"$P\"; PROF=\"$HOME/Library/Application Support/Firefox/Profiles/yxpahkkf.default-release/cookies.sqlite\"; \"$P/.venv/bin/python\" export_youtube_cookies.py --browser firefox --cookie-file \"$PROF\" --outfile cookies.txt; awk -F'\t' 'BEGIN{OFS=\"\t\"} /^#/||\$0==\"\"{print;next} \$1~/youtube\\.com\$/ && \$6~/^(__Secure-([13]P)?SID(TS|CC)?|SID(CC)?|SAPISID|APISID|HSID|SSID|LOGIN_INFO)\$/{print}' cookies.txt > cookies.slim.txt; echo \"Wrote \$P/cookies.slim.txt from \$PROF\""

URL='https://www.youtube.com/watch?v=XxoLgy5yo8o'
"$P/.venv/bin/yt-dlp" --cookies "$P/cookies.slim.txt" --extractor-args "youtube:player_client=web" -F "$URL"

/bin/zsh -c 'set -euo pipefail; P="$HOME/Downloads/transcriber"; cd "$P"; export PATH="$P/.venv/bin:$PATH"; Y="$P/.venv/bin/yt-dlp"; PY="$P/.venv/bin/python"; C="$P/cookies.slim.txt"; URL="https://www.youtube.com/watch?v=XxoLgy5yo8o"; mkdir -p "$P/data/out" "$P/data"; touch "$P/urls.txt"; grep -qxF "$URL" "$P/urls.txt" || echo "$URL" >> "$P/urls.txt"; CLIENT=web; "$Y" --cookies "$C" --extractor-args "youtube:player_client=$CLIENT" -F "$URL" >/dev/null 2>&1 || CLIENT=ios; echo "[use client] $CLIENT"; COOKIES="$C" EXTRACTOR_ARGS="youtube:player_client=$CLIENT" OUT_DIR="$P/data/out" ARCHIVE="$P/data/archive.txt" URLS_FILE="$P/urls.txt" "$PY" app.py'








# 把未提交的 .m4a 一次性加入（或用 PyCharm GUI 提交也行）
# 推荐用 find，支持子目录和带空格的文件名：
# git lfs
find . -type f -name '*.m4a' -print0 | xargs -0 git add

git commit -m "add audio files (.m4a) via LFS"
git push
