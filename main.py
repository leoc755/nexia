#       Nexia Project
#  GitHub.com/leoc755/nexia

import socket
import ssl
import platform
import certifi
import sys
import urllib.request
import html
import re
from tkinter import *


from urllib.parse import urljoin
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLineEdit, QPushButton, QScrollArea, 
                             QStatusBar, QStyle, QTextEdit, QDialog, QTabWidget, QMessageBox)
from PyQt6.QtGui import (QPainter, QColor, QFont, QImage, QFontMetrics, QPen)
from PyQt6.QtCore import Qt, QRect

# --- AURELIUS INTEGRATION ---
from aur import Aurelius
from npl import NyxPlayer

class CelesteEngine:
    def __init__(self):
        self.version = "1.16.7.1"
        self.shell_ver = "1.2"
        self.cssver = "1.1"
        self.home_url = "http://192.168.12.154/"
        self.bookmarks = [
            ("XAMPP", "http://192.168.12.154/"),
            ("Acid1", "https://www.w3.org/Style/CSS/Test/Acid1/test.html"),
            ("Acid2", "https://acid2.acidtests.org/"),
            ("Acid3", "http://acid3.acidtests.org/")
        ]
        self.image_cache = {}

    def get_ua(self):
        try:
            full_ver = platform.version()
            build_num = full_ver.split('.')[-1] if '.' in full_ver else "0"
            # 1. Detect the raw release (e.g., '7', '10', '11')
            rel = platform.release()
            
            # 2. Map to the NT version strings servers expect
            # Note: Windows 10 and 11 both use NT 10.0 in UAs
            nt_map = {"7": "6.1", "8": "6.2", "8.1": "6.3", "10": "10.0", "11": "10.0"}
            nt_ver = nt_map.get(rel, "10.0") 
            
            # 3. Architecture check
            # platform.machine() returns things like 'AMD64' or 'x86_64'
            arch = "Win64; x64" if "64" in platform.machine() else "Win32; x86"
            
            os_info = f"Windows NT {nt_ver} [{build_num}]; {arch}"
        except:
            # Safety fallback for the Exp branch
            os_info = "Windows NT 10.0 [UNK]; Win64; x64"

        return f"Mozilla/5.0 ({os_info}) Nyxora/1.14 Nex/{self.shell_ver} (Luna, rv:{self.version})"
    
    def nexia_request(self, url, redirects_left=20, ignore_security=False):
        """Luna 1.16 Core: Handles TLS 1.3, PHP Redirects, and SSL Warnings"""
        if redirects_left < 0:
            return "<h1>Engine Error</h1><p>Too many redirects.</p>", url

        try:
            is_https = url.startswith("https://")
            protocol = "https" if is_https else "http"
            clean_url = url.replace("https://", "").replace("http://", "")
            parts = clean_url.split("/", 1)
            host = parts[0]
            path = "/" + parts[1] if len(parts) > 1 else "/"
            port = 443 if is_https else 80

            with socket.create_connection((socket.gethostbyname(host), port), timeout=5) as sock:
                if is_https:
                    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
                    context.set_alpn_protocols(['http/1.1'])
                    context.load_verify_locations(certifi.where())
                    
                    # Apply user bypass for self-signed or weak keys
                    if ignore_security:
                        context.check_hostname = False
                        context.verify_mode = ssl.CERT_NONE
                        context.set_ciphers('DEFAULT@SECLEVEL=1')
                    
                    try:
                        conn = context.wrap_socket(sock, server_hostname=host)
                    except ssl.SSLError as e:
                        err = str(e).lower()
                        if "key too weak" in err or "verify failed" in err:
                            return "LUNA_SECURITY_ERROR", url
                        raise e
                else:
                    conn = sock

                request = (f"GET {path} HTTP/1.1\r\nHost: {host}\r\n"
                           f"User-Agent: {self.get_ua()}\r\n"
                           f"Connection: close\r\n\r\n")
                conn.sendall(request.encode('utf-8'))

                response_data = b""
                while True:
                    chunk = conn.recv(8192)
                    if not chunk: break
                    response_data += chunk

                if b"\r\n\r\n" in response_data:
                    header_bytes, body = response_data.split(b"\r\n\r\n", 1)
                    header_text = header_bytes.decode('utf-8', errors='ignore')
                    
                    # Handle 301/302 Redirects for PHP/XAMPP
                    if "HTTP/1.1 30" in header_text:
                        for line in header_text.splitlines():
                            if line.lower().startswith("location:"):
                                new_loc = line.split(":", 1)[1].strip()
                                if new_loc.startswith("http"): final_url = new_loc
                                elif new_loc.startswith("/"): final_url = f"{protocol}://{host}{new_loc}"
                                else:
                                    base_path = path.rsplit('/', 1)[0]
                                    if not base_path.endswith('/'): base_path += '/'
                                    final_url = f"{protocol}://{host}{base_path}{new_loc}"
                                return self.nexia_request(final_url, redirects_left - 1, ignore_security)

                    return body.decode('utf-8', errors='replace'), url
                return "", url
        except Exception as e:
            return f"<h1>Engine Alert</h1><p>{str(e)}</p>", url

class SourceViewer(QDialog):
    def __init__(self, title, content, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(800, 600)
        layout = QVBoxLayout(self)
        self.text_area = QTextEdit()
        self.text_area.setPlainText(content)
        self.text_area.setReadOnly(True)
        self.text_area.setFont(QFont("Courier New", 10))
        layout.addWidget(self.text_area)

class BrowserTab(QWidget):
    def __init__(self, shell):
        super().__init__()
        self.shell = shell
        self.history, self.forward_stack = [], []
        self.base_url, self.raw_source = "", ""
        self.elements, self.hitboxes = [], []
        
        # Initialize Aurelius Engine for this tab
        self.aurelius = Aurelius() 
        
        self.bg_color = QColor("#ffffff")
        
        layout = QVBoxLayout(self)
        self.scroll = QScrollArea()
        self.view = PyHTML_Canvas(self)
        self.scroll.setWidget(self.view)
        self.scroll.setWidgetResizable(True)
        layout.addWidget(self.scroll)
        layout.setContentsMargins(0,0,0,0)

    def load_url(self, url, save_history=True, clear_forward=True, ignore_security=False):
        self.shell.update_loading_state(True, url)
        if not url.startswith(("http://", "https://")): 
            url = "http://" + url
            
        try:
            # Unpack the content and the final URL from the engine
            source, final_url = self.shell.engine.nexia_request(url, ignore_security=ignore_security)
            
            # Intercept security errors to show the Luna Warning Screen
            if source == "LUNA_SECURITY_ERROR":
                self.base_url = url
                self.shell.address_bar.setText(url)
                self.raw_source = f"""
                <h1 style="color: #ff0000;">Security Warning</h1>
                <span><b>Warning!</b> The connection to {url} is not secure.</span><br>
                <span>[ This could be due to a <b>self-signed certificate</b> or an <b>outdated security key</b>]</span><br>
                <span>Are you sure you want to proceed?</span><br>
                <a href="luna://proceed?url={url}">[ Proceed Anyway (Unsafe) ]</a>
                """
                self.view.parse_and_format(self.raw_source)
                return

            if save_history and self.base_url and self.base_url != final_url:
                self.history.append(self.base_url)
            if clear_forward: self.forward_stack.clear()
            
            self.base_url = final_url 
            self.raw_source = source
            
            # Re-sync Address Bar and Title
            title_search = re.search(r'<title>(.*?)</title>', self.raw_source, re.I | re.S)
            title = title_search.group(1) if title_search else "New Tab"
            self.raw_source = re.sub(r'<title>.*?</title>', '', self.raw_source, flags=re.I | re.S)
            
            idx = self.shell.tabs.indexOf(self)
            self.shell.tabs.setTabText(idx, title[:15] + "..." if len(title) > 15 else title)
            self.shell.address_bar.setText(self.base_url)
            self.view.parse_and_format(self.raw_source)
            
        except Exception as e:
            self.elements = [{"tag": "p", "text": f"Engine Alert: {e}", "css": {}, "id": None, "classes": []}]
        finally:
            self.shell.update_loading_state(False)
            self.view.update()

class PyHTML_Canvas(QWidget):
    def __init__(self, tab):
        super().__init__(); self.tab = tab; self.setMouseTracking(True)
        self.active_players = {}

    def decode_entities(self, text):
        """v2912 Core: Converts HTML entities into renderable symbols."""
        return html.unescape(text)

    def parse_and_format(self, raw_html):
        self.tab.elements = []
        self.tab.aurelius.reset() 
        
        try:
            style_blocks = re.findall(r'<style.*?>(.*?)</style>', raw_html, re.I | re.S)
            for block in style_blocks:
                self.tab.aurelius.parse(block)

            bg_m = self.tab.aurelius.get_prop("body", [], "", "background-color")
            self.tab.bg_color = QColor(bg_m) if bg_m != "undefined" else QColor("#ffffff")
            
            clean_html = re.sub(r'<(script|style|head).*?>.*?</\1>', '', raw_html, flags=re.I | re.S)
            parts = re.split(r'(<[^>]+>)', clean_html, flags=re.S)
            curr_tag, curr_url, is_bold, is_italic = "p", None, False, False
            curr_id, curr_classes = None, []

            for p in parts:
                p = p.strip()
                if not p: continue
                if p.startswith('<'):
                    tag_inner = p[1:-1].lower().strip()
                    tag_name = tag_inner.split()[0] if tag_inner else ""
                    
                    id_match = re.search(r'id=["\'](.*?)["\']', tag_inner)
                    class_match = re.search(r'class=["\'](.*?)["\']', tag_inner)
                    curr_id = id_match.group(1) if id_match else None
                    curr_classes = class_match.group(1).split() if class_match else []

                    inline_css = {}
                    style_match = re.search(r'style=["\'](.*?)["\']', tag_inner, re.I)
                    if style_match:
                        inline_css = {k.strip().lower(): v.strip() for k, v in (item.split(':', 1) for item in style_match.group(1).split(';') if ':' in item)}
                    
                    if tag_name in ["b", "strong"]: is_bold = True
                    elif tag_name in ["i", "em"]: is_italic = True
                    elif tag_name in ["/b", "/strong"]: is_bold = False
                    elif tag_name in ["/i", "/em"]: is_italic = False
                    elif tag_name == "hr": self.tab.elements.append({"tag": "hr", "css": inline_css, "id": curr_id, "classes": curr_classes})
                    elif tag_name == "br": self.tab.elements.append({"tag": "br", "css": {}, "id": None, "classes": []})
                    elif tag_name == "img":
                        src_m = re.search(r'src=["\']?([^"\'>\s]+)["\']?', tag_inner)
                        if src_m: self.tab.elements.append({"tag": "img", "url": urljoin(self.tab.base_url, src_m.group(1)), "css": inline_css, "id": curr_id, "classes": curr_classes})
                    elif tag_name == "video":
                        # v2913: Extracting source for NyxPlayer v26.0.x
                        src_m = re.search(r'src=["\']?([^"\'>\s]+)["\']?', tag_inner)
                        if src_m:
                            video_url = urljoin(self.tab.base_url, src_m.group(1))
                            # Store for the renderer to instantiate the widget
                            self.tab.elements.append({
                                "tag": "video", 
                                "url": video_url, 
                                "css": inline_css
                            })
                    elif tag_name == "a":
                        curr_tag, href_m = "a", re.search(r'href=["\']?([^"\'>\s]+)["\']?', tag_inner)
                        curr_url = href_m.group(1) if href_m else None
                    elif tag_name in ["h1", "h2", "h3", "h4", "h5", "h6", "address", "p", "li", "small", "span"]: curr_tag = tag_name
                    elif tag_name.startswith('/'):
                        if tag_name == "/a": curr_url = None
                        # Only reset to 'p' if we aren't mid-inline sequence
                        if tag_name not in ["/span", "/b", "/i", "/strong", "/em"]:
                            curr_tag = "p"
                        curr_id = None
                        curr_classes = []
                else:
                    # v2912 Fix: Apply decoding to the text content before storage
                    self.tab.elements.append({
                        "tag": curr_tag, "text": self.decode_entities(p), "url": curr_url, 
                        "bold": is_bold, "italic": is_italic, "css": inline_css,
                        "id": curr_id, "classes": curr_classes
                    })
        except: pass
        
    def clear_media(self):
        """Call this before parsing a new page!"""
        for player in self.active_players.values():
            player.player.stop()
            player.setParent(None)
            player.deleteLater()
        self.active_players = {}
        
    def paintEvent(self, event):
        painter = QPainter(self); painter.fillRect(self.rect(), self.tab.bg_color)
        self.tab.hitboxes = []
        y_off, margin = 40, 30
        current_x = margin  # Horizontal cursor
        line_height = 0     # Tracking the tallest element in the current row

        for el in self.tab.elements:
            try:
                # 1. Handle explicit line breaks/rules
                if el["tag"] == "br":
                    y_off += line_height if line_height > 0 else 20
                    current_x = margin
                    line_height = 0
                    continue
                if el["tag"] == "hr":
                    y_off += line_height + 5
                    painter.setPen(QPen(QColor("#CCCCCC"), 1))
                    painter.drawLine(margin, y_off + 10, self.width() - margin, y_off + 10)
                    y_off += 25
                    current_x = margin
                    line_height = 0
                    continue

                # 2. Setup Font and Styles
                font = QFont("Times New Roman", 16)
                if el.get("bold"): font.setBold(True)
                if el.get("italic"): font.setItalic(True)
                
                if el["tag"] == "h1": font.setPointSize(32); font.setBold(True)
                elif el["tag"] == "h2": font.setPointSize(24); font.setBold(True)
                elif el["tag"] == "h3": font.setPointSize(19); font.setBold(True)
                elif el["tag"] == "h4": font.setPointSize(16); font.setBold(True)
                elif el["tag"] == "h5": font.setPointSize(13); font.setBold(True)
                elif el["tag"] == "h6": font.setPointSize(11); font.setBold(True)
                elif el["tag"] == "address": font.setPointSize(12); font.setItalic(True)
                
                painter.setFont(font)
                metrics = QFontMetrics(font)
                
                # 3. Handle Block vs Inline Logic
                # If it's a block-level tag, force a newline before rendering
                block_tags = ["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "address", "video", "img"]
                if el["tag"] in block_tags:
                    if current_x != margin: # Only jump if we aren't already at the start
                        y_off += line_height + 5
                    current_x = margin
                    line_height = 0

                # 4. Calculate Dimensions
                text_str = el.get("text", "")
                # Word wrap within the remaining width of the current line
                available_width = self.width() - margin - current_x
                
                # Get the bounding rect for the text
                rect = metrics.boundingRect(current_x, y_off, available_width, 5000, Qt.TextFlag.TextWordWrap, text_str)
                
                # 5. Apply Stellae Colors
                style_color = self.tab.aurelius.get_prop(el["tag"], el.get("classes", []), el.get("id", ""), "color")
                alignment = self.tab.aurelius.get_prop(el["tag"], el.get("classes", []), el.get("id", ""), "text-align")
                
                painter.setPen(QColor(style_color) if style_color != "undefined" else QColor("#000000"))
                
                if el["tag"] == "a":
                    font.setUnderline(True)
                    painter.setFont(font)
                    # Nexia Red link fallback
                    painter.setPen(QColor(style_color) if style_color != "undefined" else QColor("#0000ff"))

                # 6. Draw the Text
                qt_align = Qt.AlignmentFlag.AlignLeft
                if alignment == "center": qt_align = Qt.AlignmentFlag.AlignCenter
                elif alignment == "right": qt_align = Qt.AlignmentFlag.AlignRight
                
                painter.drawText(rect, Qt.TextFlag.TextWordWrap | qt_align, text_str)
                
                # 7. Update Hitboxes and Offsets
                if el["tag"] == "a" and el.get("url"):
                    self.tab.hitboxes.append((rect, el["url"]))

                # If it's an inline element, move X. If block, move Y.
                if el["tag"] in ["span", "a", "b", "i", "strong", "em"]:
                    current_x += rect.width() + 4 # Add a small tracking space
                    line_height = max(line_height, rect.height())
                else:
                    y_off += rect.height() + 10
                    current_x = margin
                    line_height = 0

            except: continue
        self.setMinimumHeight(y_off + 100)

    def mouseMoveEvent(self, event):
        for rect, url in self.tab.hitboxes:
            if rect.contains(event.pos()):
                self.tab.shell.statusBar().showMessage(f"Link: {urljoin(self.tab.base_url, url)}")
                self.setCursor(Qt.CursorShape.PointingHandCursor); return
        self.tab.shell.statusBar().clearMessage(); self.setCursor(Qt.CursorShape.ArrowCursor)

    def mousePressEvent(self, event):
        for rect, url in self.tab.hitboxes:
            if rect.contains(event.pos()):
                # Handle Luna Security Bypass Link
                if url.startswith("luna://proceed?url="):
                    target_url = url.split("url=")[1]
                    self.tab.load_url(target_url, ignore_security=True)
                else:
                    self.tab.load_url(urljoin(self.tab.base_url, url))

class PyBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.engine = CelesteEngine()
        self.setWindowTitle(f"Nexia {self.engine.shell_ver} (Luna {self.engine.version})"); self.resize(1100, 800); self.setup_ui()
        self.setStyleSheet("""
            QMainWindow { background-color: #140b0b; }
            QTabWidget::pane { border: 1px solid #3b0101; background: #140b0b; }
            
            QLineEdit {
                background-color: #231a1a;
                color: #fff;
                border: 1px solid #3b0101; /* Solid Neon Border */
                padding: 5px 15px;
                border-radius: 15px;
            }
            
            QPushButton { 
                background-color: #3b0101; 
                color: #ffffff; 
                border: none; 
                padding: 5px 12px; 
                border-radius: 8px; 
            }
            QPushButton:hover { background-color: #ff0000; }

            /* Simplified Rendered Page Border */
            QWebEngineView {
                border: 1px solid #3b0101;
                background-color: #000;
            }

            /* Simple Scrollbar (No Gradients) */
            QScrollBar:vertical { border: none; background: #140b0b; width: 10px; }
            QScrollBar::handle:vertical { 
                background: #3b0101; 
                border-radius: 5px; 
            }
            QScrollBar::handle:vertical:hover { background: #ff0000; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)

        self.tabs.setStyleSheet("""
            QTabBar::tab { 
                background: #231a1a; 
                color: #f0f0f0; 
                padding: 8px 12px; 
                border-top-left-radius: 4px; 
                border-top-right-radius: 4px; 
                margin-right: 2px;
            }
            /* Use a solid neon line instead of a gradient */
            QTabBar::tab:selected { 
                background: #140b0b; 
                border-top: 2px solid #ff0000; /* Solid accent is faster than gradient */
                color: #ffffff;
            }
            /* Remove custom close-button styling to let the system draw the X */
            QTabBar::close-button {
                subcontrol-position: right;
            }
        """)
        


    def setup_ui(self):
        central = QWidget(); self.setCentralWidget(central); self.layout = QVBoxLayout(central)
        nav = QHBoxLayout()
        self.btn_back = QPushButton("←"); self.btn_back.clicked.connect(self.go_back)
        self.btn_fwd = QPushButton("→"); self.btn_fwd.clicked.connect(self.go_forward)
        self.btn_refresh = QPushButton(); self.btn_refresh.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload)); self.btn_refresh.clicked.connect(self.refresh)
        self.address_bar = QLineEdit(); self.address_bar.returnPressed.connect(self.go_to_url)
        self.btn_new_tab = QPushButton("+"); self.btn_new_tab.clicked.connect(lambda: self.add_new_tab())
        self.btn_src = QPushButton("Source"); self.btn_src.clicked.connect(self.view_source)
        self.btn_stats = QPushButton("Style Stats"); self.btn_stats.clicked.connect(self.view_stats)
        self.btn_info = QPushButton("Info"); self.btn_info.clicked.connect(self.show_info)
        
        nav.addWidget(self.btn_back); nav.addWidget(self.btn_fwd); nav.addWidget(self.btn_refresh)
        nav.addWidget(self.address_bar); nav.addWidget(self.btn_new_tab); nav.addWidget(self.btn_src); nav.addWidget(self.btn_stats); nav.addWidget(self.btn_info)
        self.layout.addLayout(nav)
        self.tabs = QTabWidget(); self.tabs.setTabsClosable(True); self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab); self.tabs.currentChanged.connect(self.tab_changed)
        self.layout.addWidget(self.tabs); self.setStatusBar(QStatusBar(self)); self.add_new_tab(self.engine.home_url)

    def view_source(self):
        tab = self.current_tab()
        if tab: SourceViewer("Nexia Source Viewer", tab.raw_source, self).exec()

    def view_stats(self):
        tab = self.current_tab()
        if not tab: return
        inline_count = sum(1 for el in tab.elements if el.get("css"))
        report = f"--- Stellae v{self.engine.cssver} Diagnostics ---\n\n"
        report += f"Global Selectors Found: {len(tab.aurelius.styles)}\n"
        for sel in tab.aurelius.styles: report += f"  [{sel}] -> {list(tab.aurelius.styles[sel].keys())}\n"
        report += f"\nElements with Inline Styles: {inline_count}\n"
        SourceViewer("Nexia Style Diagnostics", report, self).exec()

    def add_new_tab(self, url=None):
        new_tab = BrowserTab(self); idx = self.tabs.addTab(new_tab, "New Tab"); self.tabs.setCurrentIndex(idx)
        if url: new_tab.load_url(url)
        else: new_tab.load_url(self.engine.home_url)

    def close_tab(self, index):
        if self.tabs.count() > 1: widget = self.tabs.widget(index); widget.deleteLater(); self.tabs.removeTab(index)
        else: self.current_tab().load_url(self.engine.home_url)

    def tab_changed(self, index):
        tab = self.tabs.widget(index)
        if tab: self.address_bar.setText(tab.base_url)

    def current_tab(self): return self.tabs.currentWidget()
    def go_back(self):
        tab = self.current_tab()
        if tab and tab.history: tab.forward_stack.append(tab.base_url); tab.load_url(tab.history.pop(), save_history=False, clear_forward=False)
    def go_forward(self):
        tab = self.current_tab()
        if tab and tab.forward_stack: tab.load_url(tab.forward_stack.pop(), clear_forward=False)
    def refresh(self): self.current_tab().load_url(self.current_tab().base_url, save_history=False)
    def update_loading_state(self, is_l, url=""):
        self.statusBar().setStyleSheet("color: #f0f0f0; background-color: #140b0b;")
        self.statusBar().showMessage(f"Loading {url}..." if is_l else "Ready.")
    def go_to_url(self):
        url = self.address_bar.text()
        if url: self.current_tab().load_url(url)
    def show_info(self):
        root = Tk()

        # root window title and dimension
        root.title("version Info")
        # Set geometry(widthxheight)
        root.geometry('350x200')
        lbl = Label(root, text = f"-- version info --\nNexia {self.engine.shell_ver}\nLuna {self.engine.version}\nStellae {self.engine.cssver}")
        lbl.grid()
        root.mainloop()

if __name__ == "__main__":
    app = QApplication(sys.argv); b = PyBrowser(); b.show(); sys.exit(app.exec())
