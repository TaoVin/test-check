import pathlib
import sys

entry = pathlib.Path(sys.argv[1])
name = sys.argv[2]

# %k 是桌面文件自身路径（个别文件管理器给的是 file:// URI，先剥掉）；
# 由它推出程序所在目录，再启动同目录下的可执行文件。
inner = 'p="${1#file://}"; cd "$(dirname "$p")" && exec "./' + name + '"'

lines = entry.read_text(encoding="utf-8").splitlines()
found = False
for i, line in enumerate(lines):
    if line.startswith("Exec="):
        lines[i] = "Exec=sh -c '" + inner + "' sh %k"
        found = True
if not found:
    sys.exit(f"{entry} 里没有 Exec= 行，打包结果可能不是 onedir 形态")

entry.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"Patched {entry}")
