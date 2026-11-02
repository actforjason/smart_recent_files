# GPL-2.0-or-later
# Copyright (c) 2026 Jason. All rights reserved.

bl_info = {
    "name": "Smart Recent Files",
    "author": "Jason",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "File > Open Recent / Shift+Ctrl+O",
    "description": "Automatically saves modified projects when opening recent files; Shift+click or submenu to discard changes",
    "category": "User Interface",
}

import os
import bpy
from bpy.props import StringProperty, BoolProperty, IntProperty
from bpy.types import Operator, Menu, AddonPreferences


# ---------------------------------------------------------------------------
# 多语言国际化 (i18n Translations)
# ---------------------------------------------------------------------------

translations_dict = {
    "zh_HANS": {
        ("*", "Replace Native 'Open Recent' in File Menu"): "替换原生文件菜单中的“最近打开”",
        ("*", "Seamlessly replace File > Open Recent with Smart Recent Files"): "勾选后，File 菜单中的 Open Recent 将无缝替换为智能最近菜单",
        ("*", "Override Shortcut Shift + Ctrl + O"): "接管快捷键 Shift + Ctrl + O",
        ("*", "Pop up the Smart Recent Files menu directly when pressing Shift+Ctrl+O"): "按 Shift+Ctrl+O 时直接弹出智能最近文件菜单",
        ("*", "Auto-save Modified on Click"): "默认点击自动保存改动",
        ("*", "Automatically save and switch if current project has unsaved changes and is saved to disk"): "普通点击时，若当前工程已修改且已存盘，自动保存并切换",
        ("*", "Main Menu File Limit"): "主菜单显示数量",
        ("*", "Number of recent files displayed in the main menu; excess files go to 'More...'. Keeps menus compact to prevent flip-up"): "主菜单直接展示的最近文件数，超出部分收纳进“更多...”子菜单。设小可避免弹窗/快捷收藏夹向上翻转",
        ("*", "Usage Instructions:"): "操作说明：",
        ("*", "• Normal click: Automatically save modified project and open selected file."): "• 普通点击：当前工程有修改时自动保存并打开新文件。",
        ("*", "• Shift + click: Discard current changes without saving and open selected file."): "• Shift + 点击：不保存直接丢弃当前修改，立即打开新文件。",
        ("*", "• Submenu: Use 'Open Without Saving...' to discard changes directly."): "• 亦可在子菜单【不保存直接打开...】中直接点击对应文件。",
        ("*", "• Untitled files: Safety prompt warns you if current file has never been saved."): "• 若当前文件从未存过盘（未命名），会弹出安全保护提示，避免误丢失。",
        ("*", "Unsaved Project Warning"): "未保存的新建工程警告",
        ("*", "Current project has never been saved and has unsaved changes!"): "当前工程从未存盘，且存在未保存的修改！",
        ("*", "Opening another file will cause current unsaved changes to be lost."): "若继续打开新文件，当前内容将彻底丢失。",
        ("*", "Save As Current Project First..."): "先另存为保存当前文件...",
        ("*", "Clicking OK below will discard current changes and open:"): "点击下方【确定】将放弃当前未命名修改并打开：",
        ("*", "Discarded untitled project changes, opened: {}"): "已丢弃未命名工程改动，打开: {}",
        ("*", "Smart Open Recent"): "智能打开最近文件",
        ("*", "File Path"): "文件路径",
        ("*", "Discard Changes"): "不保存改动",
        ("*", "[Open Without Saving] Discard current project changes and open file immediately."): "[不保存打开] 丢弃当前工程所有改动，立即载入目标文件。",
        ("*", "[Smart Open]\n• Click: Auto-save current changes and open target file.\n• Shift+Click: Discard changes and open immediately."): "[智能打开]\n• 点击：自动保存当前工程改动，无缝打开目标文件。\n• Shift+点击：不保存当前改动，直接强制打开。",
        ("*", "File does not exist: {}"): "文件不存在: {}",
        ("*", "Auto-saved: {}"): "已自动保存: {}",
        ("*", "Failed to auto-save current project: {}"): "自动保存当前工程失败: {}",
        ("*", "Failed to open file: {}"): "打开文件失败: {}",
        ("*", "More Recent Files (Discard Changes)"): "更多最近文件 (丢弃改动)",
        ("*", "Open Without Saving (Discard Changes)"): "不保存直接打开 (丢弃改动)",
        ("*", "More Recent Files"): "更多最近文件",
        ("*", "More Recent Files..."): "更多最近文件...",
        ("*", "No recent files"): "无最近文件",
        ("*", "No more files"): "无更多文件",
        ("*", "Open Recent"): "打开最近文件",
        ("*", "Open Without Saving (Discard Changes)..."): "不保存直接打开 (丢弃改动)...",
        ("*", "Clear Recent Files List..."): "清除最近文件列表...",
    }
}
translations_dict["zh_CN"] = translations_dict["zh_HANS"]


def _t(msg):
    """翻译动态格式化文本"""
    return bpy.app.translations.pgettext(msg)


def get_recent_files():
    """读取 Blender 的 recent-files.txt 获取有效最近文件列表"""
    config_dir = bpy.utils.user_resource('CONFIG')
    recent_path = os.path.join(config_dir, "recent-files.txt")
    if not os.path.exists(recent_path):
        return []

    files = []
    try:
        with open(recent_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                path = line.strip()
                if path and os.path.exists(path) and path not in files:
                    files.append(path)
    except Exception as e:
        print(f"[Smart Recent Files] error reading recent-files.txt: {e}")

    return files


class SmartRecentFilesPreferences(AddonPreferences):
    bl_idname = __name__

    replace_native_menu: BoolProperty(
        name="Replace Native 'Open Recent' in File Menu",
        description="Seamlessly replace File > Open Recent with Smart Recent Files",
        default=True,
        update=lambda self, context: update_menu_hook(self, context),
    )
    override_shortcut: BoolProperty(
        name="Override Shortcut Shift + Ctrl + O",
        description="Pop up the Smart Recent Files menu directly when pressing Shift+Ctrl+O",
        default=True,
        update=lambda self, context: update_keymaps(self, context),
    )
    auto_save_modified: BoolProperty(
        name="Auto-save Modified on Click",
        description="Automatically save and switch if current project has unsaved changes and is saved to disk",
        default=True,
    )
    main_menu_limit: IntProperty(
        name="Main Menu File Limit",
        description="Number of recent files displayed in the main menu; excess files go to 'More...'. Keeps menus compact to prevent flip-up",
        default=8,
        min=1,
        max=50,
    )

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.prop(self, "replace_native_menu")
        col.prop(self, "override_shortcut")
        col.prop(self, "auto_save_modified")
        col.prop(self, "main_menu_limit")

        box = layout.box()
        box.label(text="Usage Instructions:", icon='INFO')
        box.label(text="• Normal click: Automatically save modified project and open selected file.")
        box.label(text="• Shift + click: Discard current changes without saving and open selected file.")
        box.label(text="• Submenu: Use 'Open Without Saving...' to discard changes directly.")
        box.label(text="• Untitled files: Safety prompt warns you if current file has never been saved.")


class WM_OT_smart_open_untitled_dialog(Operator):
    """Safety confirmation dialog when current untitled project has unsaved changes"""
    bl_idname = "wm.smart_open_untitled_dialog"
    bl_label = "Unsaved Project Warning"
    bl_options = {'INTERNAL'}

    filepath: StringProperty()

    def execute(self, context):
        try:
            bpy.ops.wm.open_mainfile('EXEC_DEFAULT', filepath=self.filepath)
            self.report({'INFO'}, _t("Discarded untitled project changes, opened: {}").format(os.path.basename(self.filepath)))
        except Exception as e:
            self.report({'ERROR'}, _t("Failed to open file: {}").format(e))
            return {'CANCELLED'}
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=380)

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.label(text="Current project has never been saved and has unsaved changes!", icon='ERROR')
        col.label(text="Opening another file will cause current unsaved changes to be lost.")
        col.separator()
        row = col.row()
        row.scale_y = 1.2
        row.operator("wm.save_as_mainfile", text="Save As Current Project First...", icon='FILE_TICK')
        col.separator()
        col.label(text="Clicking OK below will discard current changes and open:")
        col.label(text=f"  {os.path.basename(self.filepath)}", icon='FILE_BLEND')


class WM_OT_smart_open_recent(Operator):
    """Smart Open Recent: click to auto-save and open; Shift+click to open without saving"""
    bl_idname = "wm.smart_open_recent"
    bl_label = "Smart Open Recent"
    bl_options = {'INTERNAL'}

    filepath: StringProperty(name="File Path")
    discard_changes: BoolProperty(name="Discard Changes", default=False)

    @classmethod
    def description(cls, context, properties):
        fp = properties.filepath if properties else ""
        if properties and properties.discard_changes:
            desc = _t("[Open Without Saving] Discard current project changes and open file immediately.")
            return f"{fp}\n\n{desc}" if fp else desc
        desc = _t("[Smart Open]\n• Click: Auto-save current changes and open target file.\n• Shift+Click: Discard changes and open immediately.")
        return f"{fp}\n\n{desc}" if fp else desc

    def invoke(self, context, event):
        # 监听 Shift 修饰键
        if event.shift:
            self.discard_changes = True
        return self.execute(context)

    def execute(self, context):
        if not self.filepath or not os.path.exists(self.filepath):
            self.report({'ERROR'}, _t("File does not exist: {}").format(self.filepath))
            return {'CANCELLED'}

        # 获取首选项设置
        prefs = context.preferences.addons.get(__name__)
        should_auto_save = getattr(prefs.preferences, "auto_save_modified", True) if prefs else True

        # 若不丢弃且需要保存
        if not self.discard_changes and should_auto_save and bpy.data.is_dirty:
            if bpy.data.is_saved and bpy.data.filepath:
                try:
                    bpy.ops.wm.save_mainfile('EXEC_DEFAULT')
                    self.report({'INFO'}, _t("Auto-saved: {}").format(os.path.basename(bpy.data.filepath)))
                except Exception as e:
                    self.report({'ERROR'}, _t("Failed to auto-save current project: {}").format(e))
                    return {'CANCELLED'}
            else:
                # 未命名文件安全拦截
                bpy.ops.wm.smart_open_untitled_dialog('INVOKE_DEFAULT', filepath=self.filepath)
                return {'FINISHED'}

        # 直接打开目标文件（EXEC_DEFAULT 规避保存确认弹窗）
        try:
            bpy.ops.wm.open_mainfile('EXEC_DEFAULT', filepath=self.filepath)
        except Exception as e:
            self.report({'ERROR'}, _t("Failed to open file: {}").format(e))
            return {'CANCELLED'}

        return {'FINISHED'}


class TOPBAR_MT_smart_open_recent_discard_more(Menu):
    bl_idname = "TOPBAR_MT_smart_open_recent_discard_more"
    bl_label = "More Recent Files (Discard Changes)"

    def draw(self, context):
        layout = self.layout
        recent_files = get_recent_files()

        prefs = context.preferences.addons.get(__name__)
        main_limit = getattr(prefs.preferences, "main_menu_limit", 8) if prefs else 8
        limit = context.preferences.filepaths.recent_files

        more_files = recent_files[main_limit:limit]
        if not more_files:
            layout.label(text="No more files", icon='INFO')
            return

        for filepath in more_files:
            filename = os.path.basename(filepath)
            icon = 'FILE_BACKUP' if filename.endswith(('.blend1', '.blend2')) else 'FILE_BLEND'
            op = layout.operator(
                "wm.smart_open_recent",
                text=filename,
                icon=icon,
            )
            op.filepath = filepath
            op.discard_changes = True


class TOPBAR_MT_smart_open_recent_discard(Menu):
    bl_idname = "TOPBAR_MT_smart_open_recent_discard"
    bl_label = "Open Without Saving (Discard Changes)"

    def draw(self, context):
        layout = self.layout
        recent_files = get_recent_files()

        if not recent_files:
            layout.label(text="No recent files", icon='INFO')
            return

        prefs = context.preferences.addons.get(__name__)
        main_limit = getattr(prefs.preferences, "main_menu_limit", 8) if prefs else 8
        limit = context.preferences.filepaths.recent_files
        all_recent = recent_files[:limit]

        main_files = all_recent[:main_limit]
        has_more = len(all_recent) > main_limit

        for filepath in main_files:
            filename = os.path.basename(filepath)
            icon = 'FILE_BACKUP' if filename.endswith(('.blend1', '.blend2')) else 'FILE_BLEND'
            op = layout.operator(
                "wm.smart_open_recent",
                text=filename,
                icon=icon,
            )
            op.filepath = filepath
            op.discard_changes = True

        if has_more:
            layout.menu("TOPBAR_MT_smart_open_recent_discard_more", text="More Recent Files...", icon='COLLAPSEMENU')


class TOPBAR_MT_smart_open_recent_more(Menu):
    bl_idname = "TOPBAR_MT_smart_open_recent_more"
    bl_label = "More Recent Files"

    def draw(self, context):
        layout = self.layout
        recent_files = get_recent_files()

        prefs = context.preferences.addons.get(__name__)
        main_limit = getattr(prefs.preferences, "main_menu_limit", 8) if prefs else 8
        limit = context.preferences.filepaths.recent_files

        more_files = recent_files[main_limit:limit]
        if not more_files:
            layout.label(text="No more files", icon='INFO')
            return

        for filepath in more_files:
            filename = os.path.basename(filepath)
            icon = 'FILE_BACKUP' if filename.endswith(('.blend1', '.blend2')) else 'FILE_BLEND'

            op = layout.operator(
                "wm.smart_open_recent",
                text=filename,
                icon=icon,
            )
            op.filepath = filepath
            op.discard_changes = False


class TOPBAR_MT_smart_open_recent(Menu):
    bl_idname = "TOPBAR_MT_smart_open_recent"
    bl_label = "Open Recent"

    def draw(self, context):
        layout = self.layout
        recent_files = get_recent_files()

        if not recent_files:
            layout.label(text="No recent files", icon='INFO')
            return

        prefs = context.preferences.addons.get(__name__)
        main_limit = getattr(prefs.preferences, "main_menu_limit", 8) if prefs else 8
        limit = context.preferences.filepaths.recent_files
        all_recent = recent_files[:limit]

        main_files = all_recent[:main_limit]
        has_more = len(all_recent) > main_limit

        for filepath in main_files:
            filename = os.path.basename(filepath)
            icon = 'FILE_BACKUP' if filename.endswith(('.blend1', '.blend2')) else 'FILE_BLEND'

            op = layout.operator(
                "wm.smart_open_recent",
                text=filename,
                icon=icon,
            )
            op.filepath = filepath
            op.discard_changes = False

        if has_more:
            layout.menu("TOPBAR_MT_smart_open_recent_more", text="More Recent Files...", icon='COLLAPSEMENU')

        layout.separator()

        # 辅助子菜单：给不方便按 Shift 的用户备用
        layout.menu("TOPBAR_MT_smart_open_recent_discard", text="Open Without Saving (Discard Changes)...", icon='CANCEL')

        layout.separator()
        layout.operator("wm.clear_recent_files", text="Clear Recent Files List...", icon='TRASH')


# ---------------------------------------------------------------------------
# 菜单 Hook 机制：无缝接管 File 菜单中的 Open Recent
# ---------------------------------------------------------------------------

_orig_draw_func = None
_orig_draw_index = -1


def draw_smart_topbar_file(self, context):
    layout = self.layout

    layout.operator_context = 'INVOKE_AREA'
    layout.menu("TOPBAR_MT_file_new", text="New", icon='FILE_NEW')
    layout.operator("wm.open_mainfile", text="Open...", icon='FILE_FOLDER')

    # 用智能最近菜单替换原生菜单
    layout.menu("TOPBAR_MT_smart_open_recent", text="Open Recent", icon='FILE_BLEND')

    layout.operator("wm.revert_mainfile")
    layout.menu("TOPBAR_MT_file_recover")

    layout.separator()

    layout.operator_context = 'EXEC_AREA' if context.blend_data.is_saved else 'INVOKE_AREA'
    op_save = layout.operator("wm.save_mainfile", text="Save", icon='FILE_TICK')
    if hasattr(op_save, "show_save_modified_images_dialog"):
        op_save.show_save_modified_images_dialog = True

    layout.operator_context = 'INVOKE_AREA'
    op_saveas = layout.operator("wm.save_as_mainfile", text="Save As...")
    if hasattr(op_saveas, "show_save_modified_images_dialog"):
        op_saveas.show_save_modified_images_dialog = True

    layout.operator_context = 'INVOKE_AREA'
    save_copy = layout.operator("wm.save_as_mainfile", text="Save Copy...")
    save_copy.copy = True
    if hasattr(save_copy, "show_save_modified_images_dialog"):
        save_copy.show_save_modified_images_dialog = True

    sub = layout.row()
    sub.enabled = context.blend_data.is_saved
    sub.operator_context = 'EXEC_AREA'
    save_incremental = sub.operator("wm.save_mainfile", text="Save Incremental")
    save_incremental.incremental = True
    if hasattr(save_incremental, "show_save_modified_images_dialog"):
        save_incremental.show_save_modified_images_dialog = True

    layout.separator()

    layout.operator_context = 'INVOKE_AREA'
    layout.operator("wm.link", text="Link...", icon='LINK_BLEND')
    layout.operator("wm.append", text="Append...", icon='APPEND_BLEND')
    layout.menu("TOPBAR_MT_file_previews")

    layout.separator()

    layout.menu("TOPBAR_MT_file_import")
    layout.menu("TOPBAR_MT_file_export")

    layout.separator()

    layout.menu("TOPBAR_MT_file_external_data")
    layout.menu("TOPBAR_MT_file_cleanup")

    layout.separator()

    layout.operator_context = 'EXEC_AREA'
    layout.operator("wm.save_homefile", text="Save Startup File")
    layout.operator("wm.read_homefile", text="Load Factory Settings")

    layout.separator()

    layout.operator_context = 'INVOKE_AREA'
    layout.operator("wm.quit_blender", text="Quit", icon='QUIT')


def draw_appended_menu(self, context):
    self.layout.separator()
    self.layout.menu("TOPBAR_MT_smart_open_recent", text="Smart Open Recent", icon='FILE_REFRESH')


def update_menu_hook(prefs, context):
    if prefs.replace_native_menu:
        # 取消 append（如果之前追加过）
        try:
            bpy.types.TOPBAR_MT_file.remove(draw_appended_menu)
        except Exception:
            pass
        hook_topbar_menu()
    else:
        unhook_topbar_menu()
        if draw_appended_menu not in bpy.types.TOPBAR_MT_file.draw._draw_funcs:
            bpy.types.TOPBAR_MT_file.append(draw_appended_menu)


def hook_topbar_menu():
    global _orig_draw_func, _orig_draw_index
    if not hasattr(bpy.types, "TOPBAR_MT_file"):
        return
    draw_funcs = bpy.types.TOPBAR_MT_file.draw._draw_funcs
    for i, func in enumerate(draw_funcs):
        if func.__name__ == 'draw' and 'space_topbar' in getattr(func, '__module__', ''):
            _orig_draw_func = func
            _orig_draw_index = i
            draw_funcs[i] = draw_smart_topbar_file
            break


def unhook_topbar_menu():
    global _orig_draw_func, _orig_draw_index
    if not hasattr(bpy.types, "TOPBAR_MT_file"):
        return
    draw_funcs = bpy.types.TOPBAR_MT_file.draw._draw_funcs
    if _orig_draw_func is not None:
        for i, func in enumerate(draw_funcs):
            if func == draw_smart_topbar_file:
                draw_funcs[i] = _orig_draw_func
                break
        _orig_draw_func = None
        _orig_draw_index = -1


# ---------------------------------------------------------------------------
# 快捷键管理
# ---------------------------------------------------------------------------

addon_keymaps = []


def register_keymaps():
    wm = bpy.context.window_manager
    kc = getattr(wm, "keyconfigs", None)
    if not kc or not kc.addon:
        return
    km = kc.addon.keymaps.new(name="Window", space_type='EMPTY')
    kmi = km.keymap_items.new(
        "wm.call_menu",
        type='O',
        value='PRESS',
        shift=True,
        ctrl=True,
    )
    kmi.properties.name = "TOPBAR_MT_smart_open_recent"
    addon_keymaps.append((km, kmi))


def unregister_keymaps():
    for km, kmi in addon_keymaps:
        try:
            km.keymap_items.remove(kmi)
        except Exception:
            pass
    addon_keymaps.clear()


def update_keymaps(prefs, context):
    unregister_keymaps()
    if prefs.override_shortcut:
        register_keymaps()


# ---------------------------------------------------------------------------
# 注册 / 注销
# ---------------------------------------------------------------------------

classes = (
    SmartRecentFilesPreferences,
    WM_OT_smart_open_untitled_dialog,
    WM_OT_smart_open_recent,
    TOPBAR_MT_smart_open_recent_discard_more,
    TOPBAR_MT_smart_open_recent_discard,
    TOPBAR_MT_smart_open_recent_more,
    TOPBAR_MT_smart_open_recent,
)


def register():
    try:
        bpy.app.translations.register(__name__, translations_dict)
    except Exception as e:
        print(f"[Smart Recent Files] Translation register error: {e}")

    for cls in classes:
        bpy.utils.register_class(cls)

    hook_topbar_menu()
    register_keymaps()


def unregister():
    unhook_topbar_menu()
    try:
        bpy.types.TOPBAR_MT_file.remove(draw_appended_menu)
    except Exception:
        pass

    unregister_keymaps()

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    try:
        bpy.app.translations.unregister(__name__)
    except Exception:
        pass


if __name__ == "__main__":
    register()
