# Smart Recent Files (智能最近文件)

[English](#english) | [中文说明](#chinese)

---

<a name="english"></a>
## English

A Blender extension/add-on that provides a frictionless "save-on-switch" workflow when opening recent files, along with intuitive modifier shortcuts to discard modifications or open projects in independent new windows.

### Key Features

1. **Auto-Save & Open (Default Behavior)**:
   - Clicking any item in the recent files list will automatically and silently save the current project if it has unsaved changes (`is_dirty`), then open the target file seamlessly.
2. **Discard Changes & Open (`Shift + Click`)**:
   - Hold `Shift` while clicking any recent file to instantly discard all current unsaved modifications and load the target file.
3. **Open in New Window (`Ctrl + Click`)**:
   - Hold `Ctrl` while clicking any recent file to launch an independent Blender instance/window with that file. The current project remains completely untouched.
4. **Safety Protection for Untitled Projects**:
   - If the current project has never been saved to disk (untitled), a safety confirmation dialog pops up to prevent accidental data loss, offering options to "Save As" first or explicitly confirm discarding.
5. **Compact Menu & "More..." Submenu**:
   - The main menu displays a configurable number of files (default: 8) to keep the popup compact, preventing menu flip-up in viewport popups (Quick Favorites `Q`). Remaining files are tucked into `More Recent Files...`.
6. **Seamless Native Integration**:
   - Seamlessly replaces `File > Open Recent` in the top bar.
   - Binds `Shift + Ctrl + O` to pop up the menu at the cursor anywhere in Blender.
   - Built-in internationalization (i18n) supporting both English and Simplified Chinese interface environments.

### Controls & Interactions

| Action | Result |
| :--- | :--- |
| **Click file** | Auto-saves current project if modified, then opens target file |
| **Shift + Click file** | Discards current modifications without saving, opens target file |
| **Ctrl + Click file** | Launches target file in an **independent new window** (current project stays open) |
| **Submenu "More Recent Files..."** | Browse and open older recent files |
| **`Shift + Ctrl + O`** | Pops up the Smart Recent Files menu at mouse cursor |

### Add-on Preferences

- **Replace Native 'Open Recent' in File Menu**: Integrates directly into the native File menu.
- **Override Shortcut Shift + Ctrl + O**: Assigns the floating popup shortcut.
- **Auto-save Modified on Click**: Toggle automatic saving when clicking files.
- **Main Menu File Limit**: Number of files shown in the main list before tucking into "More...".

### Installation

1. Copy or link the `smart_recent_files` folder into Blender's `extensions` or `addons` directory.
2. In Blender, go to **Edit > Preferences > Add-ons / Extensions**, search for and enable `Smart Recent Files`.

---

<a name="chinese"></a>
## 中文说明

Blender 插件：打开最近文件时实现“修改即自动存盘并打开”的高效流，同时提供便捷的快捷修饰键支持丢弃改动或在新窗口中独立开启工程。

### 核心特性

1. **自动保存并打开（默认行为）**：
   - 点击最近文件列表项：若当前工程有改动（`is_dirty`），先自动静默保存当前文件，随后打开目标工程，省去手动反复保存。
2. **强制丢弃改动打开（`Shift + 点击`）**：
   - 按住 `Shift` 键点击任意最近文件，直接放弃当前改动并载入目标工程。
3. **在新窗口中打开（`Ctrl + 点击`）**：
   - 按住 `Ctrl` 键点击任意最近文件，启动全新独立的 Blender 窗口打开目标工程，当前工程保持原样，不关闭也不保存。
4. **未命名工程防丢保护**：
   - 若当前工程从未存过盘（新建未命名状态），切换文件时会自动弹出保护对话框，引导用户“先另存为”或“明确确认放弃”，防止误丢失。
5. **精简主菜单与“更多...”收纳**：
   - 主菜单默认展示前 8 个最近文件，保持菜单紧凑。在 3D 视口通过快捷收藏夹（`Q` 键）或快捷键呼出时**不会因高度过大而向上翻转**，最新文件始终紧贴光标。超出项收纳进“更多最近文件...”子菜单中。
6. **无缝系统集成与多语言支持**：
   - 自动无缝接管顶栏 `File > Open Recent`（文件 > 打开最近文件）菜单。
   - 快捷键 `Shift + Ctrl + O` 随时随地呼出浮动菜单。
   - 悬停在任意文件项上均有详细的快捷键操作说明 Tooltip。
   - 原生支持中英文双语界面（根据 Blender 语言设置自动切换）。

### 交互方式一览

| 操作 | 对应行为 |
| :--- | :--- |
| **直接点击文件** | 当前工程有改动时**自动存盘**，然后打开目标工程 |
| **Shift + 点击文件** | **丢弃当前改动**，不保存直接打开目标工程 |
| **Ctrl + 点击文件** | **在新窗口中打开**（启动新 Blender 实例，当前工程保持打开） |
| **展开“更多最近文件...”子菜单** | 浏览并打开超出主菜单显示限制的历史工程 |
| **快捷键 `Shift + Ctrl + O`** | 在鼠标指针处快速弹出智能最近文件菜单 |

### 偏好设置选项

- **替换原生文件菜单中的“最近打开”**：勾选后接管 File 菜单中的原生 Open Recent 项。
- **接管快捷键 Shift + Ctrl + O**：按快捷键时直接弹出智能最近菜单。
- **默认点击自动保存改动**：普通点击已修改工程时是否自动保存。
- **主菜单显示数量**：主菜单直接显示的文件数（默认 8 项），超出部分收纳进“更多...”。

### 安装方法

1. 将 `smart_recent_files` 文件夹放入 Blender 的 `addons` 或 `extensions` 目录。
2. 在 Blender **编辑 -> 偏好设置 -> 插件 / 扩展** 中搜索并启用 `Smart Recent Files`。
