import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os


class ModernJSONViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("ArtVision - Enhanced JSON Viewer")
        self.root.geometry("1280x960")  # 显著增大窗口尺寸
        self.root.minsize(1024, 768)  # 设置更大的最小尺寸

        # 初始化样式和变量
        self.setup_styles()

        # 数据变量
        self.json_data = []
        self.current_item = 0
        self.current_section = 1
        self.photo = None
        self.base_dir = r"E:\EmoArt"

        # 创建界面
        self.create_widgets()

        # 绑定键盘事件
        self.root.bind("<Left>", lambda e: self.navigate("prev"))
        self.root.bind("<Right>", lambda e: self.navigate("next"))
        self.root.bind("<Control-o>", lambda e: self.load_json())

    def setup_styles(self):
        """配置增强的样式"""
        style = ttk.Style()
        style.theme_use("clam")

        # 增强的颜色方案
        self.colors = {
            "primary": "#2c3e50",
            "secondary": "#3498db",
            "background": "#f5f7fa",
            "text": "#34495e",
            "highlight": "#e74c3c",
            "accent": "#1abc9c"
        }

        # 基础样式
        style.configure("TFrame", background=self.colors["background"])

        # 增强的按钮样式
        style.configure("TButton",
                        font=("Segoe UI", 13, "bold"),
                        borderwidth=2,
                        relief="raised",
                        background=self.colors["secondary"],
                        foreground="white",
                        padding=(15, 10))
        style.map("TButton",
                  background=[("active", self.colors["primary"]), ("disabled", "#bdc3c7")],
                  relief=[("pressed", "sunken"), ("!pressed", "raised")])

        # 增强的标签样式
        style.configure("Header.TLabel",
                        font=("Segoe UI", 15, "bold"),
                        foreground=self.colors["primary"],
                        background=self.colors["background"],
                        padding=5)

        style.configure("Section.TLabel",
                        font=("Segoe UI", 17, "bold"),
                        foreground=self.colors["accent"],
                        background=self.colors["background"],
                        padding=5)

        # 增强的文本样式
        style.configure("Content.TText",
                        font=("Segoe UI", 13),
                        wrap="word",
                        background="white",
                        relief="flat",
                        padding=10)

    def create_widgets(self):
        """创建增强的界面组件"""
        # 主容器 - 使用更大的内边距
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=40, pady=40)

        # 配置网格权重
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # 创建标题区域
        self.create_header(main_frame)

        # 内容区域 - 使用更大的间距
        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 30))
        content_frame.grid_rowconfigure(3, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)

        # 请求ID显示 - 更大的字体和间距
        self.req_id = ttk.Label(
            content_frame,
            text="",
            style="Section.TLabel"
        )
        self.req_id.grid(row=0, column=0, sticky="w", pady=(0, 20))

        # 章节指示器 - 更大的元素
        indicator_frame = ttk.Frame(content_frame)
        indicator_frame.grid(row=1, column=0, sticky="w", pady=(0, 25))

        self.indicators = []
        for i in range(3):
            indicator_label = ttk.Label(
                indicator_frame,
                text="⬤" if i == 0 else "○",  # 使用更明显的符号
                font=("Segoe UI", 20),
                foreground=self.colors["accent"] if i == 0 else "#bdc3c7",
                background=self.colors["background"]
            )
            indicator_label.pack(side="left", padx=15)
            self.indicators.append(indicator_label)

        ttk.Label(
            indicator_frame,
            text="CURRENT SECTION",
            style="Header.TLabel"
        ).pack(side="left", padx=30)

        # 图片预览区域 - 更大的尺寸
        self.image_frame = ttk.Frame(content_frame, height=450)  # 更大的高度
        self.image_frame.grid(row=2, column=0, sticky="nsew", pady=25)
        self.image_preview = ttk.Label(self.image_frame,
                                       background="white",
                                       anchor="center")
        self.image_preview.pack(fill="both", expand=True, padx=15, pady=15)

        # 文本内容区域 - 更大的字体和内边距
        text_container = ttk.Frame(content_frame)
        text_container.grid(row=3, column=0, sticky="nsew")

        self.content = tk.Text(
            text_container,
            font=("Segoe UI", 13),
            wrap="word",
            bg="white",
            padx=25,
            pady=25,
            height=15
        )
        scroll = ttk.Scrollbar(text_container, command=self.content.yview)
        self.content.configure(yscrollcommand=scroll.set)

        self.content.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")

        text_container.grid_rowconfigure(0, weight=1)
        text_container.grid_columnconfigure(0, weight=1)

        # 配置文本标签样式
        self.content.tag_configure("header",
                                   font=("Segoe UI", 15, "bold"),
                                   foreground=self.colors["primary"],
                                   spacing3=10)
        self.content.tag_configure("key",
                                   font=("Segoe UI", 13, "bold"),
                                   foreground=self.colors["accent"])

        # 导航区域 - 更大的按钮
        nav_frame = ttk.Frame(main_frame)
        nav_frame.grid(row=2, column=0, sticky="ew", pady=(30, 0))

        self.prev_btn = ttk.Button(
            nav_frame,
            text="◀ PREVIOUS SECTION",
            command=lambda: self.navigate("prev"),
            state="disabled"
        )
        self.prev_btn.pack(side="left", padx=20)

        self.next_btn = ttk.Button(
            nav_frame,
            text="NEXT SECTION ▶",
            command=lambda: self.navigate("next"),
            state="disabled"
        )
        self.next_btn.pack(side="right", padx=20)

    def create_header(self, parent):
        """创建增强的标题区域"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 30))

        # 更大的加载按钮
        self.load_btn = ttk.Button(
            header_frame,
            text="📁 OPEN JSON FILE",
            command=self.load_json,
            style="TButton"
        )
        self.load_btn.pack(side="left", padx=(0, 20))

        # 文件信息标签
        self.file_info = ttk.Label(
            header_frame,
            text="No file loaded",
            style="Header.TLabel"
        )
        self.file_info.pack(side="left", fill="x", expand=True)

        # 进度显示
        self.progress = ttk.Label(
            header_frame,
            style="Header.TLabel"
        )
        self.progress.pack(side="right")

    def load_json(self):
        """加载JSON文件"""
        path = filedialog.askopenfilename(
            title="Select JSON File",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )

        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.json_data = data if isinstance(data, list) else [data]
                    self.current_item = 0
                    self.current_section = 1
                    self.file_info.config(text=f"Loaded: {os.path.basename(path)}")
                    self.update_display()
            except Exception as e:
                messagebox.showerror("Loading Error",
                                     f"Failed to load file:\n{str(e)}",
                                     parent=self.root)

    def update_display(self):
        """更新增强的显示内容"""
        if not self.json_data:
            return

        # 更新进度显示
        self.progress.config(
            text=f"ITEM {self.current_item + 1} OF {len(self.json_data)}"
        )

        # 更新章节指示器
        for i, indicator in enumerate(self.indicators):
            indicator.config(
                text="⬤" if i + 1 == self.current_section else "○",
                foreground=self.colors["accent"] if i + 1 == self.current_section else "#bdc3c7"
            )

        item = self.json_data[self.current_item]

        # 显示请求ID
        self.req_id.config(text=f"REQUEST ID: {item.get('request_id', 'UNKNOWN')}")

        # 显示图片
        if "image_path" in item:
            img_path = item.get("image_path", "")
            full_path = os.path.join(self.base_dir, img_path)
            self.show_image(full_path)
        else:
            self.clear_image()

        # 更新内容
        self.content.config(state="normal")
        self.content.delete(1.0, "end")

        section_keys = ["first_section", "second_section", "third_section"]
        if self.current_section <= len(section_keys):
            section_key = section_keys[self.current_section - 1]
            if "description" in item and section_key in item["description"]:
                section = item["description"].get(section_key, {})
                {
                    1: self.render_first_section,
                    2: self.render_second_section,
                    3: self.render_third_section
                }[self.current_section](section)
            else:
                self.content.insert("end", f"No data available for {section_key}\n", "header")
        else:
            self.content.insert("end", "Invalid section\n", "header")

        self.content.config(state="disabled")
        self.update_buttons()

    def show_image(self, path):
        """显示更大尺寸的图片预览"""
        try:
            if os.path.exists(path):
                img = Image.open(path)

                # 计算基于容器尺寸的最大大小
                container_width = self.image_frame.winfo_width() - 30
                container_height = 450  # 固定高度

                # 如果容器尚未渲染，使用回退尺寸
                if container_width < 10:
                    container_width = 1000

                # 保持宽高比调整大小
                img.thumbnail((container_width, container_height))

                self.photo = ImageTk.PhotoImage(img)
                self.image_preview.config(image=self.photo)
                self.image_preview.image = self.photo
            else:
                self.clear_image()
                if path:
                    self.image_preview.config(
                        text=f"Image not found: {os.path.basename(path)}",
                        font=("Segoe UI", 12)
                    )
        except Exception as e:
            self.clear_image()
            self.image_preview.config(
                text=f"Error loading image: {str(e)}",
                font=("Segoe UI", 12),
                foreground="red"
            )

    def clear_image(self):
        """清除图片显示"""
        self.photo = None
        self.image_preview.config(
            image="",
            text="No Image Preview Available",
            font=("Segoe UI", 12, "italic"),
            foreground="#7f8c8d"
        )

    def render_first_section(self, data):
        """渲染第一部分内容"""
        self.content.insert("end", "ARTWORK DESCRIPTION\n", "header")
        description = data.get("description", "No description available")
        self.content.insert("end", f"\n{description}\n\n")

    def render_second_section(self, data):
        """渲染第二部分内容"""
        self.content.insert("end", "VISUAL ATTRIBUTES\n", "header")
        attributes = data.get("visual_attributes", {})

        if attributes:
            for key, value in attributes.items():
                self.content.insert("end", f"\n• {key.replace('_', ' ').title()}: ", "key")
                self.content.insert("end", f"{value}")
        else:
            self.content.insert("end", "\nNo visual attributes available")

        self.content.insert("end", "\n\nEMOTIONAL IMPACT\n", "header")
        impact = data.get("emotional_impact", "No emotional impact information available")
        self.content.insert("end", f"\n{impact}")

    def render_third_section(self, data):
        """渲染第三部分内容"""
        self.content.insert("end", "EMOTIONAL ANALYSIS\n", "header")

        # 情感分析指标
        metrics = [
            ("Emotional Arousal Level", "emotional_arousal_level"),
            ("Emotional Valence", "emotional_valence"),
            ("Dominant Emotion", "dominant_emotion")
        ]

        for display_name, field in metrics:
            self.content.insert("end", f"\n• {display_name}: ", "key")
            self.content.insert("end", f"{data.get(field, 'N/A')}")

        # 治疗效果
        self.content.insert("end", "\n\nHEALING EFFECTS\n", "header")
        effects = data.get("healing_effects", [])

        if effects:
            for effect in effects:
                self.content.insert("end", f"\n• {effect}")
        else:
            self.content.insert("end", "\nNo healing effects listed")

    def navigate(self, direction):
        """处理导航"""
        if not self.json_data:
            return

        if direction == "next":
            if self.current_section < 3:
                self.current_section += 1
            else:
                if self.current_item < len(self.json_data) - 1:
                    self.current_item += 1
                    self.current_section = 1
                else:
                    messagebox.showinfo("Navigation", "You've reached the last item", parent=self.root)
                    return
        else:  # previous
            if self.current_section > 1:
                self.current_section -= 1
            else:
                if self.current_item > 0:
                    self.current_item -= 1
                    self.current_section = 3
                else:
                    messagebox.showinfo("Navigation", "You've reached the first item", parent=self.root)
                    return

        self.update_display()

    def update_buttons(self):
        """更新按钮状态"""
        if not self.json_data:
            self.prev_btn.config(state="disabled")
            self.next_btn.config(state="disabled")
            return

        self.prev_btn.config(state="normal")
        self.next_btn.config(state="normal")


if __name__ == "__main__":
    root = tk.Tk()

    # 在Windows上设置更好的DPI感知
    if os.name == "nt":
        from ctypes import windll

        windll.shcore.SetProcessDpiAwareness(1)

    app = ModernJSONViewer(root)
    root.mainloop()