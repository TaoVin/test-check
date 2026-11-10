"""打包 gui.py：onedir 形态 + 可随目录移动的 .desktop，并压缩成 zip。

本地用法：python package.py
CI 用法：  uv run python package.py
"""
import shutil
import subprocess
import sys
from pathlib import Path

NAME = "物料校验工具"
ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
APP_DIR = DIST / NAME
ENTRY = APP_DIR / f"{NAME}.desktop"

SUFFIX = {"win32": "windows", "darwin": "macos"}.get(sys.platform, "linux")


def flet_exe() -> str:
    """优先用当前解释器所在虚拟环境里的 flet，避免 PATH 里装的是别的版本。"""
    candidate = Path(sys.executable).with_name("flet.exe" if sys.platform == "win32" else "flet")
    return str(candidate) if candidate.exists() else "flet"


def patch_flet_cli_windows() -> None:
    """修掉 flet-cli 1.1.2 在 Windows 上必崩的一行。

    win_utils.update_flet_view_version_info() 往 PE 里回写 overlay 时写的是
    open(exe_path, "ab", encoding="utf-8")，二进制模式带 encoding 会抛 ValueError，
    这段代码只在 Windows 且 flet.exe 带 overlay 时才走到。flet-cli 暂无修复版本。
    """
    if sys.platform != "win32":
        return
    import flet_cli

    # flet_cli 是命名空间包（没有 __init__.py），__file__ 为 None，只能走 __path__
    base = next(iter(flet_cli.__path__), None)
    if not base:
        return
    path = Path(base) / "__pyinstaller" / "win_utils.py"
    if not path.exists():
        return
    source = path.read_text(encoding="utf-8")
    broken = 'open(exe_path, "ab", encoding="utf-8")'
    if broken not in source:
        return
    path.write_text(source.replace(broken, 'open(exe_path, "ab")'), encoding="utf-8")
    print(f"已修补 flet-cli 的 Windows overlay bug：{path}")


def main(argv: list[str]) -> None:
    patch_flet_cli_windows()
    subprocess.run(
        [flet_exe(), "pack", "gui.py", "--onedir", "--name", NAME, "-y", *argv],
        cwd=ROOT,
        check=True,
    )

    if sys.platform.startswith("linux"):
        # flet 把 .desktop 写在 dist/ 根下、Exec= 用绝对路径，换个目录就失效。
        legacy = DIST / f"{NAME}.desktop"
        if legacy.exists():
            shutil.move(str(legacy), str(ENTRY))
        subprocess.run(
            [sys.executable, str(ROOT / "patch_desktop.py"), str(ENTRY), NAME],
            cwd=ROOT,
            check=True,
        )
        ENTRY.chmod(0o755)

    archive = shutil.make_archive(str(ROOT / f"material-check-{SUFFIX}"), "zip", str(DIST), NAME)
    print(f"打包完成：{archive}")


if __name__ == "__main__":
    main(sys.argv[1:])