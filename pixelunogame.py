import tkinter as tk
from tkinter import messagebox
import random

# DATA STRUCTURES
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None
        self.prev = None

class ActionQueue:
    def __init__(self, capacity=8):
        self.items = []
        self.capacity = capacity

    def enqueue(self, item):
        if len(self.items) >= self.capacity:
            self.items.pop(0) 
        self.items.append(item)

    def get_all(self):
        return self.items

class CardStack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if not self.is_empty():
            return self.items.pop()
        return None

    def peek(self):
        if not self.is_empty():
            return self.items[-1]
        return None

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)

    def shuffle(self):
        random.shuffle(self.items)

class CircularDoublyLinkedList:
    def __init__(self):
        self.head = None
        self.current = None
        self.size = 0

    def add_player(self, player):
        new_node = Node(player)
        if not self.head:
            self.head = new_node
            self.head.next = self.head
            self.head.prev = self.head
            self.current = self.head
        else:
            tail = self.head.prev
            tail.next = new_node
            new_node.prev = tail
            new_node.next = self.head
            self.head.prev = new_node
        self.size += 1

    def get_current_player(self):
        return self.current.data

    def move_next(self):
        self.current = self.current.next

    def move_prev(self):
        self.current = self.current.prev

# SORTING
def merge_sort_hand(hand, sort_key='color'):
    if len(hand) <= 1:
        return hand

    mid = len(hand) // 2
    left_half = merge_sort_hand(hand[:mid], sort_key)
    right_half = merge_sort_hand(hand[mid:], sort_key)

    return merge(left_half, right_half, sort_key)

def merge(left, right, sort_key):
    sorted_list = []
    i = j = 0

    def get_val_weight(card):
        if card.value.isdigit(): return int(card.value)
        mapping = {'Skip': 10, 'Reverse': 11, 'Draw2': 12, 'Wild': 13, 'Wild4': 14}
        return mapping.get(card.value, 0)

    while i < len(left) and j < len(right):
        condition = False
        if sort_key == 'color':
            if left[i].color < right[j].color:
                condition = True
            elif left[i].color == right[j].color:
                if get_val_weight(left[i]) < get_val_weight(right[j]):
                    condition = True
        else:
             if get_val_weight(left[i]) < get_val_weight(right[j]):
                 condition = True
        
        if condition:
            sorted_list.append(left[i])
            i += 1
        else:
            sorted_list.append(right[j])
            j += 1

    sorted_list.extend(left[i:])
    sorted_list.extend(right[j:])
    return sorted_list

# GAME LOGIC
class Card:
    def __init__(self, color, value):
        self.color = color 
        self.value = value
    
    def __repr__(self):
        return f"{self.color} {self.value}"

class Player:
    def __init__(self, name, is_ai=False):
        self.name = name
        self.hand = [] 
        self.is_ai = is_ai

class UnoEngine:
    def __init__(self):
        self.deck = CardStack()
        self.discard = CardStack()
        self.players = CircularDoublyLinkedList()
        self.logs = ActionQueue()
        self.direction = 1 
        self.game_over = False
        self.winner = None
        self.status_msg = "Game Started"

    def log(self, msg):
        self.logs.enqueue(msg)

    def initialize_game(self):
        colors = ['Red', 'Blue', 'Green', 'Yellow']
        values = [str(i) for i in range(10)] + ['Skip', 'Reverse', 'Draw2'] * 2
        
        all_cards = []
        for c in colors:
            for v in values:
                all_cards.append(Card(c, v))
        
        for _ in range(4): all_cards.append(Card('Black', 'Wild'))
        for _ in range(4): all_cards.append(Card('Black', 'Wild4'))
        
        self.deck.items = all_cards 
        self.deck.shuffle()

        self.players.add_player(Player("You"))
        self.players.add_player(Player("Bot 1", is_ai=True))
        self.players.add_player(Player("Bot 2", is_ai=True))

        curr = self.players.head
        for _ in range(3): 
            for _ in range(7): 
                curr.data.hand.append(self.deck.pop())
            curr = curr.next

        first_card = self.deck.pop()
        while first_card.color == 'Black': 
            self.deck.push(first_card)
            self.deck.shuffle()
            first_card = self.deck.pop()
        self.discard.push(first_card)
        self.log(f"Start Card: {first_card.color} {first_card.value}")

    def get_current_player(self):
        return self.players.get_current_player()

    def check_playable(self, card):
        top = self.discard.peek()
        return (card.color == top.color or 
                card.value == top.value or 
                card.color == 'Black')

    def next_turn(self):
        if self.direction == 1:
            self.players.move_next()
        else:
            self.players.move_prev()

    def handle_special_card(self, card):
        if card.value == 'Reverse':
            self.direction *= -1
            self.log("Direction Reversed!")
        elif card.value == 'Skip':
            self.log("Next player skipped!")
            self.next_turn()
        elif card.value == 'Draw2':
            temp_node = self.players.current.next if self.direction == 1 else self.players.current.prev
            victim = temp_node.data
            victim.hand.append(self.deck.pop())
            victim.hand.append(self.deck.pop())
            self.log(f"{victim.name} drew 2 and skipped!")
            self.next_turn()
        elif card.value == 'Wild4':
            temp_node = self.players.current.next if self.direction == 1 else self.players.current.prev
            victim = temp_node.data
            for _ in range(4): victim.hand.append(self.deck.pop())
            self.log(f"{victim.name} drew 4 and skipped!")
            self.next_turn()

    def play_card(self, player, card_index, chosen_color=None):
        card = player.hand.pop(card_index)
        
        if card.color == 'Black':
            if chosen_color:
                card.color = chosen_color
                self.log(f"{player.name} changed color to {chosen_color}")
            else:
                colors = ['Red', 'Blue', 'Green', 'Yellow']
                card.color = random.choice(colors)
                self.log(f"{player.name} (AI) chose {card.color}")

        self.discard.push(card)
        self.log(f"{player.name} played {card.value}")
        
        self.handle_special_card(card)
        
        if len(player.hand) == 0:
            self.game_over = True
            self.winner = player
            self.status_msg = f"{player.name} WINS!"
            return True 
        
        self.next_turn()
        return False

    def draw_card(self, player):
        if self.deck.is_empty():
            if self.discard.size() > 1:
                # Reshuffle Logic
                top = self.discard.pop()
                self.deck.items = self.discard.items[:] 
                self.discard.items = [top] 
                self.deck.shuffle()
                self.log("Deck Reshuffled")
            else:
                # True Empty Logic
                self.log("Deck Empty!")
                self.next_turn()
                return False # Return False to signal failure

        card = self.deck.pop()
        player.hand.append(card)
        self.log(f"{player.name} drew a card")
        self.next_turn()
        return True # Return True for success

    def get_ai_move(self):
        p = self.get_current_player()
        if not p.is_ai: return None

        playable = []
        for i, card in enumerate(p.hand):
            if self.check_playable(card):
                playable.append(i)
        
        if playable:
            chosen_idx = playable[0]
            card = p.hand[chosen_idx]
            chosen_color = None
            if card.color == 'Black':
                counts = {'Red':0, 'Blue':0, 'Green':0, 'Yellow':0}
                for c in p.hand:
                    if c.color != 'Black': counts[c.color] += 1
                if not counts: counts = {'Red': 1} 
                chosen_color = max(counts, key=counts.get)
            
            return {'type': 'play', 'idx': chosen_idx, 'color': chosen_color, 'card_obj': card}
        else:
            return {'type': 'draw'}

# TKINTER UI

COLORS = {
    'Red': '#FF5555', 'Blue': '#5555FF', 'Green': '#55AA55', 'Yellow': '#FFAA00',
    'Black': '#333333', 'White': '#FFFFFF', 
    'BG': '#2E8B57', 'Sidebar': '#1E1E1E',
    'MenuBG': '#6495ED' 
}

class ModernCard(tk.Canvas):
    def __init__(self, master, card, width=80, height=120, command=None, state="normal"):
        super().__init__(master, width=width, height=height, bg=COLORS['BG'], highlightthickness=0)
        self.card = card
        self.command = command
        self.state = state
        self.width = width
        self.height = height
        self.fill_color = COLORS.get(card.color, '#333')
        if card.color == "Black" and card.value in ["Wild", "Wild4"]:
             self.fill_color = "#222"
        self.draw_card()
        if state == "normal":
            self.bind("<Button-1>", self.on_click)
            self.bind("<Enter>", self.on_hover)
            self.bind("<Leave>", self.on_leave)

    def draw_card(self):
        pad = 2
        self.create_rectangle(pad+3, pad+3, self.width-pad, self.height-pad, fill="white", outline="black", width=1)
        self.create_rectangle(pad+6, pad+6, self.width-pad-3, self.height-pad-3, fill=self.fill_color, outline="")
        oval_pad_x, oval_pad_y = 10, 25
        self.create_oval(oval_pad_x, oval_pad_y, self.width-oval_pad_x, self.height-oval_pad_y, fill="white", outline=self.fill_color)
        symbols = {'Skip': '⊘', 'Reverse': '⇄', 'Draw2': '+2', 'Wild': '🌈', 'Wild4': '+4'}
        text = symbols.get(self.card.value, self.card.value)
        txt_col = self.fill_color
        if self.card.value in ['Wild', 'Wild4']: txt_col = "black"
        font_size = 24 if len(text) < 3 else 18
        self.create_text(self.width/2, self.height/2, text=text, fill=txt_col, font=("Arial Black", font_size))
        corner_font = ("Arial", 10, "bold")
        self.create_text(12, 12, text=text, fill="white", font=corner_font)
        self.create_text(self.width-12, self.height-12, text=text, fill="white", font=corner_font)

    def on_click(self, event):
        if self.command and self.state == "normal": self.command()
    def on_hover(self, event):
        if self.state == "normal": self.move(tk.ALL, 0, -5)
    def on_leave(self, event):
        if self.state == "normal": self.move(tk.ALL, 0, 5)

class ColorChooser(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Select Color")
        self.geometry("300x120")
        self.configure(bg="#333")
        self.chosen_color = None
        tk.Label(self, text="Choose a Wild Color:", fg="white", bg="#333", font=("Arial", 12)).pack(pady=10)
        btn_frame = tk.Frame(self, bg="#333")
        btn_frame.pack()
        for col in ['Red', 'Blue', 'Green', 'Yellow']:
            tk.Button(btn_frame, bg=COLORS[col], width=6, height=2, command=lambda c=col: self.set_color(c)).pack(side="left", padx=5)
        self.transient(parent)
        self.grab_set()
        parent.wait_window(self)
    def set_color(self, color):
        self.chosen_color = color
        self.destroy()

class UnoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("UNO - DSA Edition")
        self.root.geometry("1200x800")
        
        self.state = "MENU"
        self.animating = False
        self.player_card_widgets = []
        self.opponent_widgets = {} 
        
        self.root.bind("<Configure>", self.on_window_resize)
        self.show_start_menu()

    def on_window_resize(self, event):
        if self.state == "MENU":
            self.draw_menu_content(event.width, event.height)
        elif self.state == "WIN":
            self.draw_win_screen_content(event.width, event.height)

    # START MENU (WITH HOVER)
    def show_start_menu(self):
        self.state = "MENU"
        self.root.update_idletasks() 
        for widget in self.root.winfo_children(): widget.destroy()
        
        self.root.configure(bg=COLORS['MenuBG']) 
        self.menu_canvas = tk.Canvas(self.root, bg=COLORS['MenuBG'], highlightthickness=0)
        self.menu_canvas.pack(fill="both", expand=True)
        
        self.draw_menu_content(self.root.winfo_width(), self.root.winfo_height())
        
        # Bind hover and click for the Play Button
        self.menu_canvas.tag_bind("play_btn", "<Button-1>", self.check_menu_click)
        self.menu_canvas.tag_bind("play_btn", "<Enter>", self.on_play_hover)
        self.menu_canvas.tag_bind("play_btn", "<Leave>", self.on_play_leave)

    def draw_menu_content(self, w, h):
        if w < 100 or h < 100: return
        self.menu_canvas.delete("all")
        cx, cy = w / 2, h / 2

        # Clouds
        for i in range(6):
            x = (i * 200) % w
            y = (i * 70 + 50) % (h // 2)
            self.menu_canvas.create_oval(x, y, x+150, y+60, fill="white", outline="")
            self.menu_canvas.create_oval(x+50, y-20, x+200, y+50, fill="white", outline="")

        # Decoration Cards
        self.draw_pixel_card(self.menu_canvas, cx - 350, cy, COLORS['Red'], "1")
        self.draw_pixel_card(self.menu_canvas, cx - 250, cy - 100, COLORS['Yellow'], "⇄", small=True)
        self.draw_pixel_card(self.menu_canvas, cx + 250, cy, COLORS['Blue'], "+2")
        self.draw_pixel_card(self.menu_canvas, cx + 180, cy - 120, COLORS['Green'], "⊘", small=True)

        # Title
        title_text = "PIXEL UNO"
        self.menu_canvas.create_text(cx+5, cy - 150, text=title_text, font=("Courier New", 60, "bold"), fill="#C0C0C0")
        self.menu_canvas.create_text(cx, cy - 155, text=title_text, font=("Courier New", 60, "bold"), fill="#FFD700")

        # Stone Play Button 
        btn_w, btn_h = 240, 80
        self.btn_x1, self.btn_y1 = cx - btn_w/2, cy + 50
        self.btn_x2, self.btn_y2 = cx + btn_w/2, cy + 50 + btn_h

        # Shadow
        self.menu_canvas.create_rectangle(self.btn_x1+6, self.btn_y1+6, self.btn_x2+6, self.btn_y2+6, fill="#222", outline="")
        # Border
        self.menu_canvas.create_rectangle(self.btn_x1, self.btn_y1, self.btn_x2, self.btn_y2, fill="#EEE", outline="#555", width=4)
        
        # Inner Body (Tagged for hover)
        self.menu_canvas.create_rectangle(self.btn_x1+6, self.btn_y1+6, self.btn_x2-6, self.btn_y2-6, fill="#DDD", outline="", tags=("play_btn", "play_body"))
        
        # Bolts
        for bx, by in [(self.btn_x1+10, self.btn_y1+10), (self.btn_x2-10, self.btn_y1+10), 
                       (self.btn_x1+10, self.btn_y2-10), (self.btn_x2-10, self.btn_y2-10)]:
             self.menu_canvas.create_oval(bx-3, by-3, bx+3, by+3, fill="#888", outline="#555")
        
        # Text (Tagged for hover)
        self.menu_canvas.create_text(cx, cy + 50 + btn_h/2, text="PLAY", font=("Impact", 32), fill="#333", tags=("play_btn", "play_text"))

    def on_play_hover(self, event):
        # Light up the button
        self.menu_canvas.itemconfigure("play_body", fill="#FFF") # Brighter white
        self.menu_canvas.itemconfigure("play_text", fill="#000") # Darker text

    def on_play_leave(self, event):
        # Reset color
        self.menu_canvas.itemconfigure("play_body", fill="#DDD") 
        self.menu_canvas.itemconfigure("play_text", fill="#333")

    def draw_pixel_card(self, canvas, x, y, color, text, small=False):
        w, h = (60, 90) if small else (100, 150)
        x1, y1 = x - w/2, y - h/2
        x2, y2 = x + w/2, y + h/2
        canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="black", width=2)
        canvas.create_rectangle(x1+5, y1+5, x2-5, y2-5, fill=color, outline="")
        canvas.create_oval(x1+10, y1+h/4, x2-10, y1+h*3/4, fill="white", outline=color)
        font_size = 20 if small else 40
        canvas.create_text(x, y, text=text, fill=color, font=("Courier New", font_size, "bold"))

    def check_menu_click(self, event):
        # We can just start game because the tag_bind handles collision detection for us
        self.start_game()

    # GAME SETUP & SIDEBAR MENU
    def start_game(self):
        self.state = "GAME"
        for widget in self.root.winfo_children(): widget.destroy()
        self.root.configure(bg=COLORS['BG'])
        self.engine = UnoEngine()
        self.engine.initialize_game()
        self.setup_game_layout()
        self.update_ui()

    def setup_game_layout(self):
        self.sidebar = tk.Frame(self.root, bg=COLORS['Sidebar'], width=250)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        tk.Label(self.sidebar, text="GAME LOG", fg="white", bg=COLORS['Sidebar'], font=("Segoe UI", 14, "bold")).pack(pady=20)
        self.log_container = tk.Frame(self.sidebar, bg=COLORS['Sidebar'])
        self.log_container.pack(fill="both", expand=True, padx=10)
        self.log_labels = []
        for _ in range(8):
            lbl = tk.Label(self.log_container, text="", fg="#aaa", bg=COLORS['Sidebar'], font=("Consolas", 10), anchor="w")
            lbl.pack(fill="x", pady=2)
            self.log_labels.append(lbl)
        
        # Controls Section
        tk.Label(self.sidebar, text="CONTROLS", fg="white", bg=COLORS['Sidebar'], font=("Segoe UI", 12, "bold")).pack(pady=10)
        btn_style = {"bg": "#444", "fg": "white", "relief": "flat", "font": ("Segoe UI", 10)}
        tk.Button(self.sidebar, text="Sort by Color", command=lambda: self.sort_hand('color'), **btn_style).pack(fill="x", padx=20, pady=5)
        tk.Button(self.sidebar, text="Sort by Value", command=lambda: self.sort_hand('value'), **btn_style).pack(fill="x", padx=20, pady=5)

        # SYSTEM SECTION (New)
        tk.Label(self.sidebar, text="\nSYSTEM", fg="#888", bg=COLORS['Sidebar'], font=("Segoe UI", 10, "bold")).pack(pady=5)
        tk.Button(self.sidebar, text="Main Menu", command=self.show_start_menu, bg="#663333", fg="white", relief="flat", font=("Segoe UI", 10)).pack(fill="x", padx=20, pady=5)
        tk.Button(self.sidebar, text="Quit Game", command=self.root.quit, bg="#800000", fg="white", relief="flat", font=("Segoe UI", 10)).pack(fill="x", padx=20, pady=5)

        self.game_area = tk.Frame(self.root, bg=COLORS['BG'])
        self.game_area.pack(side="right", fill="both", expand=True)

        self.opponents_frame = tk.Frame(self.game_area, bg=COLORS['BG'])
        self.opponents_frame.place(relx=0.5, rely=0.15, anchor="center")

        self.center_frame = tk.Frame(self.game_area, bg=COLORS['BG'])
        self.center_frame.place(relx=0.5, rely=0.45, anchor="center")

        # Draw Pile
        self.draw_pile_frame = tk.Frame(self.center_frame, bg=COLORS['BG'])
        self.draw_pile_frame.pack(side="left", padx=20)
        self.draw_pile = tk.Canvas(self.draw_pile_frame, width=120, height=160, bg=COLORS['BG'], highlightthickness=0)
        self.draw_pile.pack()
        self.render_deck_visual(False)

        self.draw_pile.bind("<Enter>", lambda e: self.render_deck_visual(True))
        self.draw_pile.bind("<Leave>", lambda e: self.render_deck_visual(False))
        self.draw_pile.bind("<Button-1>", lambda e: self.on_draw())
        
        self.deck_count_lbl = tk.Label(self.draw_pile_frame, text="Cards: 0", font=("Arial", 10, "bold"), bg=COLORS['BG'], fg="white")
        self.deck_count_lbl.pack(pady=5)

        self.discard_container = tk.Frame(self.center_frame, bg=COLORS['BG'])
        self.discard_container.pack(side="left", padx=20)

        self.info_lbl = tk.Label(self.game_area, text="", font=("Impact", 24), bg=COLORS['BG'], fg="white")
        self.info_lbl.place(relx=0.5, rely=0.65, anchor="center")

        self.hand_area = tk.Frame(self.game_area, bg="#206030", height=220)
        self.hand_area.pack(side="bottom", fill="x")
        self.hand_area.pack_propagate(False)
        tk.Label(self.hand_area, text="YOUR HAND", bg="#206030", fg="#ddd", font=("Segoe UI", 10)).pack(pady=5)
        self.cards_frame = tk.Frame(self.hand_area, bg="#206030")
        self.cards_frame.pack(expand=True)

    def render_deck_visual(self, is_hovered):
        self.draw_pile.delete("all")
        base_x, base_y = 15, 20
        w, h = 90, 130
        layers = 6 if is_hovered else 1
        
        for i in range(layers):
            offset = i * 2 if is_hovered else 0
            x = base_x - offset
            y = base_y - offset
            
            self.draw_pile.create_rectangle(x, y, x+w, y+h, fill="#e74c3c", outline="white", width=2)
            
            if i < layers - 1 and is_hovered:
                 self.draw_pile.create_line(x+w, y+h-5, x+w, y+h-15, fill="#444", width=1)
                 self.draw_pile.create_line(x+w-5, y+h, x+w-15, y+h, fill="#444", width=1)

            if i == layers - 1:
                self.draw_pile.create_oval(x+15, y+30, x+75, y+100, outline="yellow", width=2)
                self.draw_pile.create_text(x+45, y+65, text="UNO", fill="yellow", font=("Arial Black", 14, "italic"))

    def update_ui(self):
        logs = self.engine.logs.get_all()
        for i, lbl in enumerate(self.log_labels):
            lbl.config(text=f"> {logs[i]}" if i < len(logs) else "")

        curr_p = self.engine.get_current_player()
        arrow = "➜" if self.engine.direction == 1 else "⬅"
        if curr_p.name == "You":
            self.info_lbl.config(text=f"YOUR TURN {arrow}", fg="#88FF88")
        else:
            self.info_lbl.config(text=f"{curr_p.name.upper()}'S TURN {arrow}", fg="white")

        self.deck_count_lbl.config(text=f"Cards: {self.engine.deck.size()}")

        for widget in self.opponents_frame.winfo_children(): widget.destroy()
        self.opponent_widgets = {}
        temp = self.engine.players.head
        for _ in range(self.engine.players.size):
            p = temp.data
            if p.name != "You":
                f = tk.Frame(self.opponents_frame, bg=COLORS['BG'], padx=30)
                f.pack(side="left")
                self.opponent_widgets[p.name] = f
                canv = tk.Canvas(f, width=40, height=50, bg=COLORS['BG'], highlightthickness=0)
                canv.pack()
                for i in range(3):
                    o = i * 2
                    canv.create_rectangle(5+o, 5-o, 35+o, 45-o, fill="#333", outline="white")
                tk.Label(f, text=p.name, font=("Arial", 11, "bold"), bg=COLORS['BG'], fg="yellow" if p == curr_p else "white").pack()
                tk.Label(f, text=f"{len(p.hand)} Cards", font=("Arial", 9), bg=COLORS['BG'], fg="#ddd").pack()
            temp = temp.next

        for widget in self.discard_container.winfo_children(): widget.destroy()
        if not self.engine.discard.is_empty():
            ModernCard(self.discard_container, self.engine.discard.peek(), width=100, height=140, state="disabled").pack()

        for widget in self.cards_frame.winfo_children(): widget.destroy()
        self.player_card_widgets = []
        human = None
        t = self.engine.players.head
        for _ in range(3): 
            if t.data.name == "You": human = t.data
            t = t.next
        if human:
            is_turn = (curr_p == human)
            for i, card in enumerate(human.hand):
                state = "normal" if is_turn and self.engine.check_playable(card) and not self.animating else "disabled"
                mc = ModernCard(self.cards_frame, card, command=lambda idx=i: self.on_card_click(idx), state=state)
                mc.pack(side="left", padx=5)
                self.player_card_widgets.append(mc)
                if state == "disabled": mc.config(bg="#154020")

        if self.engine.game_over:
            self.show_win_screen()
        elif curr_p.is_ai and not self.animating:
            self.root.after(1200, self.run_ai)

    # WIN SCREEN (PIXELATED FONT)
    def show_win_screen(self):
        self.state = "WIN"
        self.root.update_idletasks()
        self.win_canvas = tk.Canvas(self.root, highlightthickness=0)
        self.win_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.draw_win_screen_content(self.root.winfo_width(), self.root.winfo_height())
        self.win_canvas.bind("<Button-1>", self.check_win_click)
        self.animate_win_particles()

    def draw_win_screen_content(self, w, h):
        self.win_canvas.delete("content")
        winner_name = self.engine.winner.name
        is_me = (winner_name == "You")
        
        sky_color = "#1a0b2e" if is_me else "#2c0505"
        self.win_canvas.configure(bg=sky_color)
        
        # Mountains
        self.draw_mountains(self.win_canvas, w, h, base_height=h-100, peak_height=200, color="#111", jaggedness=50)
        mid_col = "#4b2e83" if is_me else "#500"
        self.draw_mountains(self.win_canvas, w, h, base_height=h-50, peak_height=120, color=mid_col, jaggedness=30)
        self.draw_mountains(self.win_canvas, w, h, base_height=h, peak_height=40, color="#222", jaggedness=10)

        cx, cy = w / 2, h / 2 - 50
        text_main = "YOU WIN!" if is_me else "ELIMINATED"
        text_sub = f"{winner_name} won the game!" if not is_me else "Victory is yours!"
        
        # PIXELATED FONT: Courier New
        self.win_canvas.create_text(cx+5, cy, text=text_main, font=("Courier New", 70, "bold"), fill="black", tags="content")
        self.win_canvas.create_text(cx, cy, text=text_main, font=("Courier New", 70, "bold"), fill="white", tags="content")
        self.win_canvas.create_text(cx, cy+120, text=text_sub, font=("Courier New", 20, "bold"), fill="white", tags="content")

        btn_w, btn_h = 250, 60
        self.ret_x1, self.ret_y1 = cx - btn_w/2, cy + 200
        self.ret_x2, self.ret_y2 = cx + btn_w/2, cy + 200 + btn_h
        
        self.win_canvas.create_rectangle(self.ret_x1+5, self.ret_y1+5, self.ret_x2+5, self.ret_y2+5, fill="black", outline="", tags="content")
        self.win_canvas.create_rectangle(self.ret_x1, self.ret_y1, self.ret_x2, self.ret_y2, fill="#333", outline="white", width=3, tags="content")
        self.win_canvas.create_text(cx, self.ret_y1 + btn_h/2, text="RETURN TO MENU", font=("Courier New", 18, "bold"), fill="white", tags="content")

    def draw_mountains(self, canvas, w, h, base_height, peak_height, color, jaggedness):
        points = [0, h, 0, base_height]
        curr_x = 0
        while curr_x < w:
            step = random.randint(30, 100)
            curr_x += step
            y_var = random.randint(-peak_height, 0)
            points.append(curr_x)
            points.append(base_height + y_var)
        points.extend([w, h, 0, h])
        canvas.create_polygon(points, fill=color, outline="", tags="mountain")

    def animate_win_particles(self):
        if self.state != "WIN": return
        w, h = self.root.winfo_width(), self.root.winfo_height()
        x = random.randint(0, w)
        y = h + 10
        size = random.randint(5, 15)
        color = random.choice(["white", "yellow", "cyan"])
        pid = self.win_canvas.create_rectangle(x, y, x+size, y+size, fill=color, outline="", tags="particle")
        self.move_particle(pid)
        self.root.after(100, self.animate_win_particles)

    def move_particle(self, pid):
        if self.state != "WIN": return
        self.win_canvas.move(pid, 0, -5)
        coords = self.win_canvas.coords(pid)
        if coords and coords[1] > -20:
            self.root.after(50, lambda: self.move_particle(pid))
        else:
            self.win_canvas.delete(pid)

    def check_win_click(self, event):
        if self.ret_x1 <= event.x <= self.ret_x2 and self.ret_y1 <= event.y <= self.ret_y2:
            self.show_start_menu()

    # INPUT & ANIMATIONS
    def on_card_click(self, idx):
        if self.animating: return
        human = self.engine.get_current_player()
        if human.name != "You": return
        card = human.hand[idx]
        chosen_color = None
        if card.color == 'Black':
            chooser = ColorChooser(self.root)
            if not chooser.chosen_color: return 
            chosen_color = chooser.chosen_color
        
        self.animating = True
        try:
            start_widget = self.player_card_widgets[idx]
            self.animate_fly(start_widget, self.discard_container, lambda: self.finish_play(human, idx, chosen_color))
        except:
             self.finish_play(human, idx, chosen_color)

    def finish_play(self, player, idx, color):
        self.engine.play_card(player, idx, color)
        self.animating = False
        self.update_ui()

    def on_draw(self):
        if self.animating: return
        human = self.engine.get_current_player()
        if human.name != "You": return
        
        success = self.engine.draw_card(human)
        if not success:
            messagebox.showinfo("Uno", "Deck is empty and cannot be replenished. Turn skipped.")
            self.update_ui()
            return

        self.animating = True
        self.animate_fly(self.draw_pile, self.hand_area, lambda: self.finish_draw())

    def finish_draw(self):
        self.animating = False
        self.update_ui()

    def run_ai(self):
        if self.animating: return
        move = self.engine.get_ai_move()
        if not move: return

        self.animating = True
        p = self.engine.get_current_player()
        bot_widget = self.opponent_widgets.get(p.name, self.opponents_frame)

        if move['type'] == 'play':
            dummy = ModernCard(self.root, move['card_obj'])
            self.animate_ai_fly(bot_widget, self.discard_container, dummy, 
                                lambda: self.finish_play(p, move['idx'], move['color']))
        else:
            success = self.engine.draw_card(p) 
            if not success:
                self.animating = False
                self.update_ui()
                return
            self.animate_fly(self.draw_pile, bot_widget, lambda: self.finish_draw())

    def animate_fly(self, start_widget, end_widget, on_complete):
        flyer = tk.Canvas(self.root, width=80, height=120, highlightthickness=0, bg=COLORS['BG'])
        flyer.create_rectangle(2, 2, 78, 118, fill="#e74c3c", outline="white", width=2)
        flyer.create_oval(15, 35, 65, 85, outline="yellow", width=2)
        flyer.create_text(40, 60, text="UNO", fill="yellow", font=("Arial Black", 12, "italic"))
        self._do_fly(flyer, start_widget, end_widget, on_complete)

    def animate_ai_fly(self, start_widget, end_widget, custom_flyer, on_complete):
        self._do_fly(custom_flyer, start_widget, end_widget, on_complete)

    def _do_fly(self, flyer, start_widget, end_widget, on_complete):
        try:
            sx = start_widget.winfo_rootx() - self.root.winfo_rootx()
            sy = start_widget.winfo_rooty() - self.root.winfo_rooty()
            ex = end_widget.winfo_rootx() - self.root.winfo_rootx()
            ey = end_widget.winfo_rooty() - self.root.winfo_rooty()
            sx += start_widget.winfo_width()//2 - 40
            sy += start_widget.winfo_height()//2 - 60
            ex += end_widget.winfo_width()//2 - 40
            ey += end_widget.winfo_height()//2 - 60
        except:
            flyer.destroy()
            on_complete()
            return

        flyer.place(x=sx, y=sy)
        steps = 15
        dx = (ex - sx) / steps
        dy = (ey - sy) / steps

        def step(i):
            if i < steps:
                flyer.place(x=sx + dx*i, y=sy + dy*i)
                self.root.after(20, lambda: step(i+1))
            else:
                flyer.destroy()
                on_complete()
        step(0)

    def sort_hand(self, key):
        if self.animating: return
        t = self.engine.players.head
        human = None
        for _ in range(3):
            if t.data.name == "You": human = t.data
            t = t.next
        if human:
            human.hand = merge_sort_hand(human.hand, key)
            self.update_ui()

if __name__ == "__main__":
    root = tk.Tk()
    app = UnoGUI(root)
    root.mainloop()
