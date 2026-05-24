# ==============================
# IMPORTS — นำเข้า Library ที่ต้องใช้
# ==============================
import tkinter as tk          # สร้าง GUI window
from tkinter import ttk       # Widget สวยงามกว่า tk ธรรมดา
import time                   # ใช้ time.time() จับเวลา

# ==============================
# CLASS 1: Stopwatch (นาฬิกาจับเวลา)
# ==============================
class Stopwatch:
    """
    ทำหน้าที่เหมือนนาฬิกาจับเวลาจริงๆ
    แยก class ออกมาเพื่อ reuse ได้ใน PomodoroTimer
    """

    def __init__(self):
        # __init__ = constructor, รันตอนสร้าง object ครั้งแรก
        self.start_time = None   # เก็บเวลาที่กด Start
        self.elapsed = 0.0       # เวลาที่ผ่านไปแล้ว (วินาที)
        self.running = False     # สถานะ: กำลังทำงานอยู่ไหม?

    def start(self):
        """เริ่มหรือ resume นาฬิกา"""
        if not self.running:
            # บันทึกเวลา ณ ตอนนี้ แล้วหักด้วยที่เคยผ่านไปแล้ว
            # เทคนิค: ทำให้ resume ต่อได้โดยไม่ reset
            self.start_time = time.time() - self.elapsed
            self.running = True

    def stop(self):
        """หยุดนาฬิกาชั่วคราว (pause)"""
        if self.running:
            self.elapsed = time.time() - self.start_time
            self.running = False

    def reset(self):
        """รีเซ็ตทุกอย่างกลับเป็น 0"""
        self.start_time = None
        self.elapsed = 0.0
        self.running = False

    def get_elapsed(self):
        """คืนค่าเวลาที่ผ่านไป (วินาที) แบบ real-time"""
        if self.running:
            # ถ้ากำลังทำงาน: คำนวณแบบ live
            return time.time() - self.start_time
        return self.elapsed  # ถ้าหยุด: คืนค่าล่าสุด


# ==============================
# CLASS 2: PomodoroTimer (Logic หลัก)
# ==============================
class PomodoroTimer:
    """
    จัดการ session ทั้งหมดของ Pomodoro
    - work session (ทำงาน)
    - short break (พักสั้น)
    - long break (พักยาว)
    """

    def __init__(self,
                 work_minutes=25,
                 short_break=5,
                 long_break=15,
                 cycles=4):
        # รับค่า config ผ่าน parameter (default = มาตรฐาน Pomodoro)
        self.work_duration = work_minutes * 60    # แปลงเป็นวินาที
        self.short_break_duration = short_break * 60
        self.long_break_duration = long_break * 60
        self.cycles = cycles                       # กี่รอบก่อน long break

        # State ปัจจุบัน
        self.current_session = "work"      # "work" | "short_break" | "long_break"
        self.session_count = 0             # นับรอบ work ที่เสร็จแล้ว
        self.stopwatch = Stopwatch()       # ใช้ Stopwatch ที่สร้างไว้

    def get_total_duration(self):
        """คืนค่าเวลาทั้งหมดของ session ปัจจุบัน"""
        # Dictionary ใช้แทน if/elif ได้สั้นกว่า
        durations = {
            "work":        self.work_duration,
            "short_break": self.short_break_duration,
            "long_break":  self.long_break_duration,
        }
        return durations[self.current_session]

    def get_remaining(self):
        """คืนค่าเวลาที่เหลืออยู่ (วินาที)"""
        remaining = self.get_total_duration() - self.stopwatch.get_elapsed()
        return max(0, remaining)  # ไม่ให้ติดลบ

    def is_session_done(self):
        """เช็คว่า session นี้จบแล้วหรือยัง"""
        return self.get_remaining() == 0

    def next_session(self):
        """ข้ามไป session ถัดไป พร้อม reset นาฬิกา"""
        self.stopwatch.reset()

        if self.current_session == "work":
            self.session_count += 1
            # ทุกๆ N รอบ → long break, อื่นๆ → short break
            if self.session_count % self.cycles == 0:
                self.current_session = "long_break"
            else:
                self.current_session = "short_break"
        else:
            # หลัง break ทุกแบบ → กลับไป work
            self.current_session = "work"

    def get_session_label(self):
        """ข้อความแสดงชื่อ session ปัจจุบัน"""
        labels = {
            "work":        f"Work #{self.session_count + 1}",
            "short_break": "Short Break ☕",
            "long_break":  "Long Break 🎉",
        }
        return labels[self.current_session]


# ==============================
# CLASS 3: PomodoroApp (หน้าต่าง GUI)
# ==============================
class PomodoroApp:
    """
    สร้าง GUI และเชื่อมกับ PomodoroTimer
    แยก UI ออกจาก Logic → แก้ไขแต่ละส่วนได้อิสระ
    """

    def __init__(self, root):
        self.root = root
        self.root.title("Pomodoro Timer 🍅")
        self.root.geometry("320x400")

        # สร้าง timer object
        self.timer = PomodoroTimer()
        self.is_running = False

        # สร้าง UI
        self._build_ui()

        # เริ่ม update loop (รันทุก 100ms)
        self._update_display()

    def _build_ui(self):
        """สร้าง Widget ทั้งหมด"""
        # Label แสดงชื่อ session
        self.session_label = tk.Label(
            self.root,
            text="Work #1",
            font=("Arial", 16, "bold")
        )
        self.session_label.pack(pady=10)

        # Label แสดงเวลา (ใหญ่ๆ)
        self.time_label = tk.Label(
            self.root,
            text="25:00",
            font=("Arial", 64, "bold"),
            fg="#2196F3"  # สีน้ำเงิน
        )
        self.time_label.pack(pady=10)

        # Progress bar
        self.progress = ttk.Progressbar(
            self.root,
            length=280,
            mode='determinate'  # แสดง % ที่แน่นอน
        )
        self.progress.pack(pady=10)

        # Frame สำหรับปุ่ม
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=20)

        self.start_btn = tk.Button(
            btn_frame,
            text="▶ Start",
            width=10,
            command=self._toggle_timer,  # ชี้ไปที่ method
            bg="#4CAF50", fg="white",
            font=("Arial", 12)
        )
        self.start_btn.grid(row=0, column=0, padx=5)

        reset_btn = tk.Button(
            btn_frame,
            text="↺ Reset",
            width=10,
            command=self._reset,
            font=("Arial", 12)
        )
        reset_btn.grid(row=0, column=1, padx=5)

        skip_btn = tk.Button(
            btn_frame,
            text="⏭ Skip",
            width=10,
            command=self._skip,
            font=("Arial", 12)
        )
        skip_btn.grid(row=1, column=0, columnspan=2, pady=5)

        # Label นับจำนวน session
        self.count_label = tk.Label(
            self.root,
            text="Sessions completed: 0",
            font=("Arial", 11),
            fg="gray"
        )
        self.count_label.pack()

    def _toggle_timer(self):
        """Start / Pause สลับกัน"""
        if self.is_running:
            self.timer.stopwatch.stop()
            self.is_running = False
            self.start_btn.config(text="▶ Resume", bg="#FF9800")
        else:
            self.timer.stopwatch.start()
            self.is_running = True
            self.start_btn.config(text="⏸ Pause", bg="#F44336")

    def _reset(self):
        """รีเซ็ตทุกอย่าง"""
        self.timer = PomodoroTimer()  # สร้าง timer ใหม่
        self.is_running = False
        self.start_btn.config(text="▶ Start", bg="#4CAF50")

    def _skip(self):
        """ข้าม session ปัจจุบัน"""
        self.timer.stopwatch.stop()
        self.is_running = False
        self.timer.next_session()
        self.start_btn.config(text="▶ Start", bg="#4CAF50")

    def _format_time(self, seconds):
        """แปลงวินาที → MM:SS"""
        mins = int(seconds) // 60
        secs = int(seconds) % 60
        return f"{mins:02d}:{secs:02d}"  # :02d = เติม 0 ข้างหน้า

    def _update_display(self):
        """
        อัปเดตหน้าจอทุก 100ms
        เป็น "heart" ของโปรแกรม — วิ่งตลอดเวลา
        """
        # ดึงข้อมูลจาก timer
        remaining = self.timer.get_remaining()
        total = self.timer.get_total_duration()
        elapsed = total - remaining

        # อัปเดต Label
        self.time_label.config(text=self._format_time(remaining))
        self.session_label.config(text=self.timer.get_session_label())
        self.count_label.config(
            text=f"Sessions completed: {self.timer.session_count}"
        )

        # อัปเดต Progress bar (0-100)
        if total > 0:
            percent = (elapsed / total) * 100
            self.progress['value'] = percent

        # เปลี่ยนสีตาม session
        colors = {
            "work":        "#2196F3",   # น้ำเงิน = โฟกัส
            "short_break": "#4CAF50",   # เขียว = พัก
            "long_break":  "#9C27B0",   # ม่วง = พักยาว
        }
        self.time_label.config(fg=colors[self.timer.current_session])

        # เช็คว่า session จบหรือยัง
        if self.is_running and self.timer.is_session_done():
            self.timer.next_session()   # ข้ามไป session ถัดไป
            self.is_running = False
            self.start_btn.config(text="▶ Start", bg="#4CAF50")
            # แจ้งเตือน (เพิ่ม sound หรือ notification ได้ที่นี่)

        # ⭐ สำคัญมาก! เรียกตัวเองซ้ำทุก 100ms
        # after(ms, function) = tkinter's version ของ setTimeout
        self.root.after(100, self._update_display)


# ==============================
# MAIN: จุดเริ่มต้นของโปรแกรม
# ==============================
if __name__ == "__main__":
    root = tk.Tk()              # สร้าง window หลัก
    app = PomodoroApp(root)     # สร้าง App พร้อม root
    root.mainloop()             # เริ่ม event loop (รอรับ input)