import asyncio
import time

import flet as ft
from pathlib import Path

from main import do_init, do_analyse, do_check  # 你现有的逻辑

def main(page: ft.Page):
    page.title = "物料数据校验工具"
    page.window.width = 760
    page.window.height = 600
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 24

    state = {"mode": "analyse", "file": None, "out": None}

    file_picker = ft.FilePicker()
    out_picker = ft.FilePicker()
    page.services.extend([file_picker, out_picker])

    file_label = ft.Text("未选择文件", color=ft.Colors.GREY_600)
    out_label = ft.Text("未选择（执行时弹出保存对话框）", color=ft.Colors.GREY_600)
    log = ft.TextField(multiline=True, min_lines=9, read_only=True,
                       text_size=12, bgcolor=ft.Colors.GREY_50,
                       border=ft.OutlineInputBorder(
                           side=ft.BorderSide(color=ft.Colors.GREY_300)))

    hint = ft.Text(size=13, color=ft.Colors.GREY_600)
    hints = {
        "init": "初始化基础数据：必须选择基础数据 Excel，不支持输出路径",
        "analyse": "统计校验：文件可选，不选则查现有数据；执行时选择保存地址",
        "check": "文件校验：必须选择待校验 Excel；执行时选择保存地址",
    }

    def reset_io():
        state["file"] = None
        state["out"] = None
        file_label.value = "未选择文件"
        out_label.value = "未选择（执行时弹出保存对话框）"

    def set_mode(mode):
        state["mode"] = mode
        hint.value = hints[mode]
        reset_io()
        page.update()

    async def pick_file(e):
        files = await file_picker.pick_files(
            allowed_extensions=["xlsx", "xls"],
            file_type=ft.FilePickerFileType.CUSTOM,
        )
        if files and files[0].path:
            state["file"] = files[0].path
            file_label.value = Path(files[0].path).name
            page.update()

    def default_out_name(mode):
        stamp = time.strftime("%Y%m%d%H%M%S")
        if mode == "analyse":
            return f"物料名称-规格型号-品牌一致，但有多个物料编号-{stamp}.xlsx"
        return f"物理名称+规格+品牌，物料主数据已存在的数据-{stamp}.xlsx"

    async def ask_out(mode):
        path = await out_picker.save_file(
            allowed_extensions=["xlsx"],
            file_type=ft.FilePickerFileType.CUSTOM,
            file_name=default_out_name(mode),
        )
        if path:
            state["out"] = path
            out_label.value = Path(path).name
        return path

    async def pick_out(e):
        if state["mode"] == "init":
            log.value = "初始化模式不输出文件"
            page.update()
            return
        await ask_out(state["mode"])
        page.update()

    async def run(e):
        log.value = ""
        mode = state["mode"]
        try:
            if mode in ("init", "check") and not state["file"]:
                log.value = "请先选择文件"
                page.update()
                return
            out = None
            if mode != "init":
                if not state["out"]:
                    await ask_out(mode)
                if not state["out"]:
                    log.value = "已取消：未选择保存地址"
                    page.update()
                    return
                out = state["out"]
            log.value = "执行中…"
            page.update()
            if mode == "init":
                await asyncio.to_thread(do_init, state["file"])
                log.value = "初始化完成"
            elif mode == "analyse":
                await asyncio.to_thread(do_analyse, state["file"], out)
                log.value = f"统计完成，已保存到：{out}"
            else:
                await asyncio.to_thread(do_check, state["file"], out)
                log.value = f"校验完成，已保存到：{out}"
        except Exception as ex:
            log.value = f"出错：{ex}"
        page.update()

    set_mode("analyse")
    page.add(
        ft.Text("物料数据校验工具", size=22, weight=ft.FontWeight.BOLD),
        ft.Divider(height=1),
        ft.SegmentedButton(
            selected=["analyse"],
            allow_multiple_selection=False,
            allow_empty_selection=False,
            on_change=lambda e: set_mode(e.control.selected[0]),
            segments=[
                ft.Segment(value="init", label=ft.Text("初始化")),
                ft.Segment(value="analyse", label=ft.Text("统计校验")),
                ft.Segment(value="check", label=ft.Text("文件校验")),
            ],
        ),
        hint,
        ft.Row([
            ft.OutlinedButton("选择文件", icon=ft.Icons.UPLOAD_FILE,
                              on_click=pick_file),
            file_label,
        ]),
        ft.Row([
            ft.OutlinedButton("选择保存地址", icon=ft.Icons.SAVE,
                              on_click=pick_out),
            out_label,
        ]),
        ft.FilledButton("开始执行", icon=ft.Icons.PLAY_ARROW, on_click=run),
        ft.Divider(height=1),
        ft.Text("运行日志", size=13, weight=ft.FontWeight.BOLD),
        log,
    )


ft.run(main)