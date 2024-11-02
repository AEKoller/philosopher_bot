import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
from datetime import datetime
import config
from main import PhilosopherBot
from queue import Queue

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class ChatMessage(tk.Frame):
    def __init__(self, master, message, is_user=True, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(bg='#f0f0f0')
        
        # Message container with no border
        msg_frame = tk.Frame(
            self,
            bg='#007AFF' if is_user else '#ffffff',
            padx=15,
            pady=10,
        )
        msg_frame.pack(
            fill=tk.X, 
            padx=10, 
            pady=5, 
            anchor='e' if is_user else 'w'
        )
        
        # Remove border and relief
        msg_frame.configure(relief='flat', borderwidth=0)
        
        # Use Text widget instead of Label to allow text selection
        msg_text = tk.Text(
            msg_frame,
            wrap=tk.WORD,
            height=0,  # Height will adjust to content
            width=50,
            font=('Helvetica', 11),
            bg=msg_frame['bg'],
            fg='white' if is_user else 'black',
            relief='flat',  # Remove border from text widget
            padx=0,
            pady=0,
        )
        msg_text.pack(anchor='e' if is_user else 'w', fill=tk.X)
        
        # Insert the message and disable editing
        msg_text.insert('1.0', message)
        msg_text.configure(state='disabled')
        
        # Calculate required height based on content
        line_height = msg_text.dlineinfo('1.0')[3]  # Height of one line
        content_height = float(msg_text.index('end-1c').split('.')[0])  # Number of lines
        total_height = int(line_height * content_height)
        msg_text.configure(height=content_height)

        # Remove highlight color when text is selected
        msg_text.configure(
            selectbackground='#0078D7',  # Windows-style selection color
            selectforeground='white' if is_user else 'white',  # Text color when selected
            cursor="arrow"  # Use default cursor instead of text cursor
        )
        
        # Make background highlight work properly
        if is_user:
            msg_text.configure(insertbackground='white', insertwidth=0)

class PhilosopherBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Philosopher Chat")
        self.root.geometry("800x800")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize bot and message queue
        self.bot = PhilosopherBot(config.ANTHROPIC_API_KEY)
        self.message_queue = Queue()
        
        # Initialize philosopher info
        self.philosopher_name = None
        self.philosopher_text = None
        
        self.setup_styles()
        self.create_widgets()
        self.start_message_processor()

    def setup_styles(self):
        # Configure ttk styles
        style = ttk.Style()
        style.configure('Modern.TButton',
                       padding=10,
                       font=('Helvetica', 11))
        
        style.configure('Header.TLabel',
                       font=('Helvetica', 14, 'bold'),
                       padding=10)

    def create_widgets(self):
        # Main container
        self.main_container = tk.Frame(self.root, bg='#f0f0f0')
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Create header
        self.header = ttk.Label(
            self.main_container,
            text="Philosopher Chat",
            style='Header.TLabel'
        )
        self.header.pack(fill=tk.X)

        # Create chat display area with custom background
        self.chat_frame = tk.Frame(self.main_container, bg='#f0f0f0')
        self.chat_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create scrollable canvas for chat messages
        self.canvas = tk.Canvas(self.chat_frame, bg='#f0f0f0', highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.chat_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='#f0f0f0')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=760)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel to scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Create input area
        self.input_frame = tk.Frame(self.main_container, bg='#f0f0f0')
        self.input_frame.pack(fill=tk.X, pady=10)
        
        self.input_field = tk.Text(
            self.input_frame,
            height=3,
            font=('Helvetica', 11),
            wrap=tk.WORD
        )
        self.input_field.pack(fill=tk.X, pady=(0, 10))
        
        # Bind Enter key to send message
        self.input_field.bind("<Return>", self.handle_return)
        self.input_field.bind("<Shift-Return>", lambda e: self.input_field.insert(tk.END, "\n"))
        
        # Create button frame
        self.button_frame = tk.Frame(self.input_frame, bg='#f0f0f0')
        self.button_frame.pack(fill=tk.X)
        
        self.send_button = ttk.Button(
            self.button_frame,
            text="Send",
            command=self.send_message,
            style='Modern.TButton'
        )
        self.send_button.pack(side=tk.RIGHT)
        
        self.setup_button = ttk.Button(
            self.button_frame,
            text="Setup Philosopher",
            command=self.show_setup_dialog,
            style='Modern.TButton'
        )
        self.setup_button.pack(side=tk.LEFT)
        
        # Show setup dialog on start
        self.root.after(100, self.show_setup_dialog)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def show_setup_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Setup Philosopher")
        dialog.geometry("600x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Create and pack widgets
        tk.Label(dialog, text="Philosopher's Name:", font=('Helvetica', 11)).pack(anchor='w', padx=10, pady=5)
        name_entry = tk.Entry(dialog, font=('Helvetica', 11))
        name_entry.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(dialog, text="Philosopher's Text:", font=('Helvetica', 11)).pack(anchor='w', padx=10, pady=5)
        text_entry = tk.Text(dialog, height=10, font=('Helvetica', 11))
        text_entry.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        def save_setup():
            self.philosopher_name = name_entry.get().strip()
            self.philosopher_text = text_entry.get("1.0", tk.END).strip()
            if self.philosopher_name and self.philosopher_text:
                self.add_system_message(f"Now chatting as {self.philosopher_name}")
                dialog.destroy()
            else:
                tk.messagebox.showwarning("Input Error", "Please fill in all fields")
        
        ttk.Button(dialog, text="Start Chat", command=save_setup, style='Modern.TButton').pack(pady=10)

    def handle_return(self, event):
        if not event.state & 0x1:  # Shift not pressed
            self.send_message()
            return 'break'

    def send_message(self):
        message = self.input_field.get("1.0", tk.END).strip()
        if not message:
            return
        
        if not self.philosopher_name or not self.philosopher_text:
            tk.messagebox.showwarning("Setup Required", "Please set up the philosopher first")
            self.show_setup_dialog()
            return
            
        # Add user message to chat
        self.add_message(message, True)
        
        # Clear input field
        self.input_field.delete("1.0", tk.END)
        
        # Disable input while processing
        self.input_field.config(state='disabled')
        self.send_button.config(state='disabled')
        
        # Start processing thread
        threading.Thread(
            target=self.process_message,
            args=(message,),
            daemon=True
        ).start()

    def process_message(self, message):
        try:
            response = self.bot.get_response(
                self.philosopher_name,
                self.philosopher_text,
                message
            )
            self.message_queue.put(("response", response))
        except Exception as e:
            self.message_queue.put(("error", str(e)))

    def start_message_processor(self):
        """Process messages from the queue and update the GUI"""
        try:
            while True:
                msg_type, content = self.message_queue.get_nowait()
                if msg_type == "response":
                    self.add_message(content, False)
                elif msg_type == "error":
                    self.add_system_message(f"Error: {content}")
                self.input_field.config(state='normal')
                self.send_button.config(state='normal')
        except:
            pass
        finally:
            self.root.after(100, self.start_message_processor)

    def add_message(self, message, is_user=True):
        message_widget = ChatMessage(self.scrollable_frame, message, is_user)
        message_widget.pack(fill=tk.X)
        self.scroll_to_bottom()

    def add_system_message(self, message):
        frame = tk.Frame(self.scrollable_frame, bg='#f0f0f0')
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        label = tk.Label(
            frame,
            text=message,
            fg='#666666',
            bg='#f0f0f0',
            font=('Helvetica', 10, 'italic')
        )
        label.pack()
        self.scroll_to_bottom()

    def scroll_to_bottom(self):
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1)

def main():
    root = tk.Tk()
    app = PhilosopherBotGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()