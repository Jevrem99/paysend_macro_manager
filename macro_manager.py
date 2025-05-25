import os
import re
from tkinter import *
from PIL import Image, ImageTk
import pyperclip
from tkcalendar import DateEntry
from datetime import datetime
from tkinter import messagebox
from dateutil.relativedelta import relativedelta
from tkinter import font
import json

# Funkcija za proveru i kreiranje datoteke ako ne postoji
def load_macros(filename='macros.json'):
    if not os.path.exists(filename):
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump({}, file)  # Kreiraj praznu JSON datoteku
    with open(filename, 'r', encoding='utf-8') as file:
        return json.load(file)

# Učitaj makroe
macros = load_macros()

def callback(sv):
    searchMacros(sv.get())

def clear_macro_frame():
    for widget in macro_frame.winfo_children():
        widget.destroy()

def is_phone_number(term):
    pattern = re.compile(r'[+\d()\-./\s]{7,}')
    return bool(pattern.match(term))

def format_phone_number(term):
    return ''.join(filter(str.isdigit, term))

def searchMacros(term):
    clear_macro_frame()

    if term and len(term) > 1:
        if is_phone_number(term):
            formatted_number = format_phone_number(term)
            phone_frame = Frame(macro_frame, bg='lightgrey', bd=2, relief=RAISED)
            phone_frame.grid(row=0, column=0, pady=2, sticky="ew")
            phone_frame.bind("<Button-1>", lambda event, number=formatted_number: copy_text(number))

            label = Label(phone_frame, width=30, text=formatted_number, bg='lightgrey', anchor="w", justify=LEFT)
            label.pack(side=LEFT, padx=10, pady=10)
            label.bind("<Button-1>", lambda event, number=formatted_number: copy_text(number))
        else:
            row = 1
            for macro in macros:

                if term.lower() in macro.lower():
                    
                    tileColor = 'red' if delete_mode else 'black'
                    
                    macro_frame_inner = Frame(macro_frame, bg='lightgrey', bd=2, relief=RAISED)
                    macro_frame_inner.grid(row=row, column=0, pady=2, sticky="ew")
                    
                    action = confirm_delete if delete_mode else copy_macro
                    
                    macro_frame.bind("<Button-1>",lambda event,m=macro:action(m))
                    
                    label = Label(macro_frame_inner, width=30, text=macro, bg='lightgrey', anchor="w", justify=LEFT,fg=tileColor)
                    label.pack(side=LEFT, padx=10, pady=10)
                    label.bind("<Button-1>", lambda event, m=macro: action(m))
                    label.bind("<Button-3>",lambda event,m=macro:do_popup(event,m))
                    
                    view_icon = PhotoImage(file='assets/eye.png')
                    view_button = Button(macro_frame_inner, text="", image=view_icon, compound=LEFT, command=lambda m=macro: view_macro(m))
                    view_button.image = view_icon
                    view_button.pack(side=RIGHT, padx=10, pady=10)

                    if re.search(r'XXXXXXX|\[AMOUNT\]|\[DATE\]|\[SENT\]|\[REST\]|\[COUNTRY\]', macros[macro]):
                        edit_icon = PhotoImage(file='assets/edit.png')
                        edit_button = Button(macro_frame_inner, text="", image=edit_icon, compound=LEFT, command=lambda m=macro: edit_macro(m))
                        edit_button.image = edit_icon
                        edit_button.pack(side=RIGHT, padx=10, pady=10)
                    
                    row += 1

def copy_text(text):
    pyperclip.copy(text)
    search.delete(0, END)
    searchMacros("help")
    search.delete(0, END)
    window.after(1, clear_macro_frame)

def copy_macro(macro):
    pyperclip.copy(macros[macro])
    search.delete(0, END)
    searchMacros("help")
    window.after(2, lambda: search.delete(0, END))
    window.after(2, clear_macro_frame)
    
def confirm_delete(macro):
    answer = messagebox.askyesno("Confirm to delete",f"Are you sure you want to delete macro:\n\n{macro}?")
    if answer:
        delete_macro(macro)
    
def delete_macro(macro):
    global macros
    
    if macro in macros:
        del macros[macro]
        with open('macros.json','w',encoding='utf-8') as file:
            json.dump(macros,file,indent=4,ensure_ascii=False)
        searchMacros(searchTerm.get())
    
def view_macro(macro):
    view_window = Toplevel(window)
    view_window.title(macro)
    view_window.minsize(300, 200)
    view_window.wm_iconphoto(False, ImageTk.PhotoImage(Image.open('assets/psicon.png')))
    
    left_frame = Frame(view_window)
    left_frame.pack(side=LEFT,fill=BOTH,expand = True)

    text = Text(left_frame, wrap=WORD)
    text.insert(INSERT, macros[macro])
    text.config(state=DISABLED)
    text.pack(expand=True, fill=BOTH)
    
    right_frame = Frame(view_window)
    right_frame.pack(side=RIGHT,fill=BOTH,expand=True)
    
    edit_mode = 0
    
    def izmeni():
        nonlocal edit_mode
        nonlocal text
        global searchTerm
        
        edit_mode = 1 if edit_mode == 0 else 0
        titleColor = 'medium spring green' if edit_mode == 1 else 'black'
        edit_button.config(fg=titleColor)
        
        state = DISABLED if edit_mode == 0 else NORMAL
        
        if macros[macro] != text.get('1.0','end-1c'):
            macros[macro] = text.get('1.0','end-1c')
            with open('macros.json','w',encoding='utf-8') as file:
                json.dump(macros,file,indent=4,ensure_ascii=False)
            searchMacros(searchTerm.get())
            
        text.config(state=state)

        
    
    edit_button = Button(right_frame,text='Edit',font=("Arial bold",10),command=izmeni)
    edit_button.pack(side=BOTTOM,anchor='se', padx=10, pady=10)
    
def right_click_edit(macro):
    edit_window = Toplevel(window)
    edit_window.title(macro)
    edit_window.minsize(300, 200)
    edit_window.wm_iconphoto(False, ImageTk.PhotoImage(Image.open('assets/psicon.png')))
    
    left_frame = Frame(edit_window)
    left_frame.pack(side=LEFT,fill=BOTH,expand = True)

    text = Text(left_frame, wrap=WORD)
    text.insert(INSERT, macros[macro])
    text.pack(expand=True, fill=BOTH)
    
    right_frame = Frame(edit_window)
    right_frame.pack(side=RIGHT,fill=BOTH,expand=True)
    
    def done():
        
        if macros[macro] != text.get('1.0','end-1c'):
            macros[macro] = text.get('1.0','end-1c')
            with open('macros.json','w',encoding='utf-8') as file:
                json.dump(macros,file,indent=4,ensure_ascii=False)
            searchMacros(searchTerm.get())
        edit_window.destroy()

        
    done_button = Button(right_frame,text='Done',font=("Arial bold",10),command=done)
    done_button.pack(side=BOTTOM,anchor='se', padx=10, pady=10)

def edit_macro(macro):
    edit_window = Toplevel(window)
    edit_window.title(f"Edit {macro}")
    edit_window.minsize(600, 400)
    edit_window.wm_iconphoto(False, ImageTk.PhotoImage(Image.open('psicon.png')))

    macro_text = macros[macro]

    placeholders = re.findall(r'XXXXXXX|\[AMOUNT\]|\[DATE\]|\[SENT\]|\[REST\]|\[COUNTRY\]', macro_text)
    unique_placeholders = list(set(placeholders))
    entry_vars = {ph: StringVar() for ph in unique_placeholders}
    
    left_frame = Frame(edit_window)
    left_frame.pack(side=LEFT, fill=BOTH, expand=True)

    text = Text(left_frame, wrap=WORD)
    text.insert(INSERT, macro_text)
    text.config(state=DISABLED)
    text.pack(expand=True, fill=BOTH)

    right_frame = Frame(edit_window)
    right_frame.pack(side=RIGHT, fill=Y)

    ordered_placeholders = ['XXXXXXX', '[AMOUNT]', '[SENT]', '[DATE]', '[COUNTRY]']
    row = 0
    for placeholder in ordered_placeholders:
        if placeholder in unique_placeholders:
            label = Label(right_frame, text=placeholder)
            label.grid(row=row, column=0, padx=5, pady=5)
            if placeholder == '[DATE]':
                entry = DateEntry(right_frame, textvariable=entry_vars[placeholder], date_pattern='dd/MM/yyyy')
            else:
                entry = Entry(right_frame, textvariable=entry_vars[placeholder])
            entry.grid(row=row, column=1, padx=5, pady=5)
            entry.bind('<KeyRelease>', lambda e, ph=placeholder: update_macro(text, macro_text, entry_vars))
            if placeholder == '[DATE]':
                entry.bind('<<DateEntrySelected>>', lambda e, ph=placeholder: update_macro(text, macro_text, entry_vars))
            row += 1

    def apply_changes():
        updated_text = macro_text
        for placeholder, var in entry_vars.items():
            updated_text = updated_text.replace(placeholder, format_placeholder_value(placeholder, var.get(), entry_vars))
        pyperclip.copy(updated_text)
        edit_window.destroy()
        search.delete(0, END)
        searchMacros("help")
        search.delete(0, END)
        window.after(1, clear_macro_frame)

    done_button = Button(right_frame, text="Done", command=apply_changes)
    done_button.grid(row=row, columnspan=2, pady=10)

def update_macro(text_widget, macro_text, entry_vars):
    updated_text = macro_text
    for placeholder, var in entry_vars.items():
        updated_text = updated_text.replace(placeholder, format_placeholder_value(placeholder, var.get(), entry_vars))
    text_widget.config(state=NORMAL)
    text_widget.delete(1.0, END)
    text_widget.insert(INSERT, updated_text)
    text_widget.config(state=DISABLED)

def format_placeholder_value(placeholder, value, entry_vars):
    if placeholder == '[DATE]' and value:
        return format_date(value)
    elif placeholder == '[REST]':
        try:
            amount = extract_number(entry_vars.get('[AMOUNT]', StringVar()).get())
            sent = extract_number(entry_vars.get('[SENT]', StringVar()).get())
            rest = amount - sent
            return f"{rest:,.2f} {extract_currency(entry_vars.get('[AMOUNT]', StringVar()).get())}"
        except ValueError:
            return '[INVALID]'
    return value

def extract_number(value):
    match = re.search(r'[\d,]+(?:\.\d+)?', value)
    return float(match.group().replace(',', '')) if match else 0

def extract_currency(value):
    match = re.search(r'[^\d,]+$', value)
    return match.group().strip() if match else ''

def format_date(date_str):
    date = datetime.strptime(date_str, '%d/%m/%Y')
    day = date.day
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]
    return f"{day}{suffix} of {date.strftime('%B %Y')}"

# Funkcija za dodavanje novog makroa
def add_macro():
    add_window = Toplevel(window)
    add_window.title("Add New Macro")
    add_window.minsize(600, 200)

    macro_name_label = Label(add_window, text="Macro Name:")
    macro_name_label.grid(row=0, column=0, padx=10, pady=10)
    macro_name_entry = Entry(add_window)
    macro_name_entry.grid(row=0, column=1, padx=10, pady=10)

    macro_text_label = Label(add_window, text="Macro Text:")
    macro_text_label.grid(row=1, column=0, padx=10, pady=10)
    macro_text_entry = Text(add_window, wrap=WORD, height=10)
    macro_text_entry.grid(row=1, column=1, padx=10, pady=10)

    def save_macro():
        macro_name = macro_name_entry.get()
        macro_text = macro_text_entry.get("1.0", "end-1c")
        if macro_name and macro_text:
            macros[macro_name] = macro_text
            with open('macros.json', 'w', encoding='utf-8') as file:
                json.dump(macros, file, ensure_ascii=False, indent=4)
            add_window.destroy()
            search.delete(0, END)
            searchMacros("help")
            window.after(1, clear_macro_frame)

    save_button = Button(add_window, text="Save", command=save_macro)
    save_button.grid(row=2, columnspan=2, pady=10)

def delete_mode_change():
    global delete_mode
    
    if(delete_mode == 0):
        delete_button.config(fg='red')
        delete_mode = 1
    else:
        delete_button.config(fg='grey')
        delete_mode = 0
    searchMacros(searchTerm.get())
    
def do_popup(event,macro):
    global selected_macro
    selected_macro = macro
    try:
        right_click_menu.tk_popup(event.x_root, event.y_root)
    finally:
        right_click_menu.grab_release()


window = Tk()
window.title("Paysend macro manager")
window.minsize(274,50)
window.attributes("-topmost", True)

window.wm_iconphoto(False, ImageTk.PhotoImage(Image.open('assets/psicon.png')))

delete_mode = 0

searchTerm = StringVar()
searchTerm.trace("w", lambda name, index, mode, sv=searchTerm: callback(sv))
search = Entry(window, width=30, font=8, textvariable=searchTerm)
search.grid(row=0, column=0)

macro_frame = Frame(window)
macro_frame.grid(row=1, column=0)

right_click_menu = Menu(window,tearoff=0)
right_click_menu.add_command(label="View  👁️",command=lambda:view_macro(selected_macro))
right_click_menu.add_separator()
right_click_menu.add_command(label="Edit  ✎",command=lambda:right_click_edit(selected_macro))
right_click_menu.add_separator()
right_click_menu.add_command(label="Delete ⛔",command=lambda:confirm_delete(selected_macro))


# Dugme "+" u donjem desnom kutu
plus_button = Button(window, text="+", font=("Arial", 11), width=2, height=1, command=add_macro)
plus_button.grid(row=2, column=1, sticky="se", padx=1, pady=1)

delete_button = Button(window,text="del",font=("Arial",11),width=2,height=1,fg='grey',command=delete_mode_change)
delete_button.grid(row=2,column=0,sticky="se",padx=1,pady=1)

window.mainloop()
