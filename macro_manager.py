import os
import re
from tkinter import *
from PIL import Image, ImageTk
import pyperclip
import threading
import time
import requests
from tkcalendar import DateEntry
from datetime import datetime
from datetime import timedelta
from tkinter import messagebox
from dateutil.relativedelta import relativedelta
from tkinter import filedialog
from ttkwidgets.autocomplete import AutocompleteCombobox
import keyboard
import shutil
import json

#------------------------UTILS----------------------------#

SEARCH_DELAY = 200

def load_macros(filename='macros.json'):
    if not os.path.exists(filename):
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump({}, file) 
    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)
        return {k: normalize_macro_text(v) for k, v in data.items()}
    
def load_keyboard_macros(filename='config/keyboard_macros.json'):
    if not os.path.exists(filename):
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump({}, file) 
    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)
        return data

def is_phone_number(term):
    pattern = re.compile(r'[+\d()\-./\s]{7,}')
    return bool(pattern.match(term))

def format_phone_number(term):
    return ''.join(filter(str.isdigit, term))

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

def is_transaction_number(term):
    pattern = re.compile(r'1[0-9]{8}00')
    return bool(pattern.match(term))

def normalize_macro_text(text):
    return re.sub(r'X{3,10}','XXXXXXX',text)

def is_bin(term):
    pattern = re.compile(r"^/bin\d+$")
    return bool(pattern.match(term))

def is_country_code(term):
    pattern = re.compile(r"^/(?:cc|country_code|countrycode|country)(\+?\d+)$")
    return bool(pattern.match(term))

def extract_country_code(term):
    match = re.search(r"^/(?:cc|country_code|countrycode|country)(\+?\d+)$",term)
    if match:
        return match.group(1)
    
def extract_bin(term):
    match = re.search(r"(\d+)", term)
    if match:
        return match.group(1)

#--------------------------SEARCH--------------------------------------#

def copy_text(text):
    pyperclip.copy(text)
    search.delete(0, END)
    reset_macro_frame()
    window.update_idletasks()
    window.geometry('')

def copy_macro(macro):
    pyperclip.copy(macros[macro])
    search.delete(0, END)
    reset_macro_frame()
    window.update_idletasks()
    window.geometry('')


def searchMacros(term):
    reset_macro_frame()

    if term and len(term) > 1:
        if is_phone_number(term):
            formatted_number = format_phone_number(term)
            phone_frame = Frame(macro_frame, bg='lightgrey', bd=2, relief=GROOVE)
            phone_frame.grid(row=0, column=0, pady=2, sticky="ew")
            phone_frame.bind("<Button-1>", lambda event, number=formatted_number: copy_text(number))

            label = Label(phone_frame, width=30, text=formatted_number, bg='lightgrey', anchor="w", justify=LEFT)
            label.pack(side=LEFT, padx=10, pady=10)
            label.bind("<Button-1>", lambda event, number=formatted_number: copy_text(number))
        elif is_bin(term):
            bin = extract_bin(term)
            bin_frame = Frame(macro_frame, bg='lightgrey', bd=2, relief=GROOVE)
            bin_frame.grid(row=0, column=0, pady=2, sticky="ew")
            bin_frame.bind("<Button-1>", lambda event, bin=bin: checkBin(bin))

            label = Label(bin_frame, width=30, text="Check bin", bg='lightgrey', anchor="w", justify=LEFT)
            label.pack(side=LEFT, padx=10, pady=10)
            label.bind("<Button-1>", lambda event, bin=bin: checkBin(bin))
        elif is_country_code(term):
            country_code = extract_country_code(term)
            country = findCountry(country_code)
            country_code_frame = Frame(macro_frame, bg='lightgrey', bd=2, relief=GROOVE)
            country_code_frame.grid(row=0, column=0, pady=2, sticky="ew")
            country_code_frame.bind("<Button-1>", lambda event:copy_text(country))

            label = Label(country_code_frame, width=30, text=country, bg='lightgrey', anchor="w", justify=LEFT)
            label.pack(side=LEFT, padx=10, pady=10)
            label.bind("<Button-1>", lambda event:copy_text(country))
        else:
            row = 1
            for macro in macros:

                if term.lower() in macro.lower():
                    
                    tileColor = 'red' if delete_mode else 'black'
                    
                    macro_frame_inner = Frame(macro_frame, bg='gray85', bd=2, relief=GROOVE)
                    macro_frame_inner.grid(row=row, column=0, pady=2, sticky="ew")
                    
                    action = confirm_delete if delete_mode else copy_macro
                    
                    macro_frame_inner.bind("<Button-1>",lambda event,m=macro:action(m))
                    macro_frame_inner.bind("<Button-3>",lambda event,m=macro:do_popup(event,m))
                    
                    label = Label(macro_frame_inner, width=30, text=macro, bg='gray85', anchor="w", justify=LEFT,fg=tileColor)
                    label.pack(side=LEFT, padx=10, pady=10)
                    label.bind("<Button-1>", lambda event, m=macro: action(m))
                    label.bind("<Button-3>",lambda event,m=macro:do_popup(event,m))
                    
                    view_icon = PhotoImage(file='assets/eye.png')
                    view_button = Button(macro_frame_inner, image=view_icon, relief=GROOVE, command=lambda m=macro: view_macro(m))
                    view_button.image = view_icon
                    view_button.pack(side=RIGHT, padx=10, pady=10)

                    if re.search(r'XXXXXXX|\[AMOUNT\]|\[DATE\]|\[SENT\]|\[REST\]|\[COUNTRY\]|\[DATE1\]|\[DATE2\]', macros[macro]):
                        edit_icon = ImageTk.PhotoImage(Image.open("assets/edit.png").resize((32,32), Image.LANCZOS))
                        edit_button = Button(macro_frame_inner, image=edit_icon,relief=GROOVE, command=lambda m=macro: edit_macro(m))
                        edit_button.image = edit_icon
                        edit_button.pack(side=RIGHT, padx=10, pady=10)
                    
                    row += 1
    elif len(term) < 1:
        reset_macro_frame()
        window.update_idletasks()  
        window.geometry('')
        
    window.update_idletasks()  
    window.geometry('')

def on_search_key(event):

    global search_after_id

    if search_after_id is not None:
        try:
            window.after_cancel(search_after_id)
        except Exception:
            pass

    search_after_id = window.after(SEARCH_DELAY, lambda: searchMacros(searchTerm.get()))

def reset_macro_frame():
    global macro_frame
    if macro_frame is not None:
        macro_frame.destroy()

    macro_frame = Frame(window)
    macro_frame.grid(row=1, column=0, sticky="ew")

#--------------------------CRUD------------------------------------#

def add_macro():
    
    global add_window_ref
    
    if add_window_ref is not None and add_window_ref.winfo_exists():
        add_window_ref.lift()
        return
    
    add_window = Toplevel(window)
    add_window.attributes("-topmost",True)
    add_window.title("Add New Macro")
    add_window.minsize(600, 200)
    add_window_ref = add_window
    
    def on_close():
        global add_window_ref
        add_window_ref = None
        add_window.destroy()
        
    add_window.protocol("WM_DELETE_WINDOW", on_close)

    macro_name_label = Label(add_window, text="Macro Name:",font=('Arial',10))
    macro_name_label.grid(row=0, column=0, padx=10, pady=10, sticky='e')

    macro_name_entry = Entry(add_window,width=25,font=('Arial',12))
    macro_name_entry.grid(row=0, column=1, padx=10, pady=10, sticky='w')

    macro_text_label = Label(add_window, text="Macro Text:",font=('Arial',10))
    macro_text_label.grid(row=1, column=0, padx=10, pady=10)
    macro_text_entry = Text(add_window, wrap=WORD, height=10)
    macro_text_entry.grid(row=1, column=1, padx=10, pady=10)
    
    info_icon = PhotoImage(file='assets/info.png')
    info_label = Label(add_window, image=info_icon)
    info_label.image = info_icon
    info_label.grid(row=2,column=0,padx=10,pady=10)
    
    info_label.bind("<Enter>",displayInfo)
    info_label.bind("<Leave>",hideInfo)

    def save_macro():
        macro_name = macro_name_entry.get()
        macro_text = macro_text_entry.get("1.0", "end-1c")
        if macro_name and macro_text:
            macros[macro_name] = normalize_macro_text(macro_text)
            with open('macros.json', 'w', encoding='utf-8') as file:
                json.dump(macros, file, ensure_ascii=False, indent=4)
            add_window.destroy()
            search.delete(0, END)
            reset_macro_frame()
            window.update_idletasks()
            window.geometry('')
            
    save_button = Button(add_window, text="Save", relief=GROOVE,command=save_macro)
    save_button.grid(row=2, columnspan=2, pady=10)

infoWindow = None

def displayInfo(event):
    global infoWindow
    
    infoText = (
        "Available placeholders:\n\n"
        "• XXXXXXX,            — free text inputs\n"
        "• [COUNTRY]           — list of countries\n"
        "• [DATE]              — date picker\n"
        "• [DATE1], [DATE2]    — 2 date pickers (with 3BD option)\n"
        "• [AMOUNT], [REST]    — numeric inputs\n"
        "• [SENT]              — auto-calculated as [AMOUNT] - [REST]\n\n"
        "*Note: [SENT] is automatically calculated and does not require input."
    )
    infoWindow = Toplevel(event.widget)
    infoWindow.wm_overrideredirect(True)
    infoWindow.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
    Label(infoWindow, text=infoText, bg="lightgrey", relief="solid",justify="left" ,borderwidth=1).pack()
    
def hideInfo(event):
    global infoWindow
    if infoWindow:
        infoWindow.destroy()
        infoWindow = None

def confirm_delete(macro):
    answer = messagebox.askyesno("Confirm to delete",f"Are you sure you want to delete macro:\n\n{macro}?",default='no')
    if answer:
        delete_macro(macro)
    
def delete_macro(macro):
    global macros
    
    if macro in macros:
        del macros[macro]
        with open('macros.json','w',encoding='utf-8') as file:
            json.dump(macros,file,indent=4,ensure_ascii=False)
        searchMacros(searchTerm.get())
        
def delete_mode_change():
    global delete_mode,del_img,del_active_img
    
    if(not delete_mode):
        delete_button.config(image=del_active_img)
        delete_mode = True
    else:
        delete_button.config(image=del_img)
        delete_mode = False
    searchMacros(searchTerm.get())
    
def view_macro(macro):
    view_window = Toplevel(window)
    view_window.attributes("-topmost",True)
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
    
    def update():
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
    
    edit_button = Button(right_frame,text="Edit",relief=GROOVE,font=("Arial bold",10),command=update)
    edit_button.pack(side=BOTTOM,anchor='se', padx=10, pady=10)
    
    if re.search(r'XXXXXXX|\[AMOUNT\]|\[DATE\]|\[SENT\]|\[REST\]|\[COUNTRY\]|\[DATE1\]|\[DATE2\]', macros[macro]):
        info_icon = PhotoImage(file='assets/info.png')
        info_label = Label(right_frame, text="", image=info_icon)
        info_label.image = info_icon
        info_label.pack(side=BOTTOM,anchor='se',padx=15, pady=10)
        
        info_label.bind("<Enter>",displayInfo)
        info_label.bind("<Leave>",hideInfo)

def do_popup(event,macro):
    global selected_macro
    selected_macro = macro
    try:
        right_click_menu.tk_popup(event.x_root, event.y_root)
    finally:
        right_click_menu.grab_release()

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
    
    info_icon = PhotoImage(file='assets/info.png')
    info_label = Label(right_frame, text="", image=info_icon)
    info_label.image = info_icon
    info_label.pack(side=BOTTOM,anchor='se',padx=18, pady=10)
    
    info_label.bind("<Enter>",displayInfo)
    info_label.bind("<Leave>",hideInfo)

def edit_macro(macro):
    
    global edit_window_ref
    
    if edit_window_ref is not None and edit_window_ref.winfo_exists():
        edit_window_ref.lift()
        return
    
    def on_close():
        global edit_window_ref
        edit_window_ref = None
        edit_window.destroy()
    
    edit_window = Toplevel(window)
    edit_window.attributes("-topmost",True)
    edit_window.title(f"Edit {macro}")
    edit_window.minsize(600, 400)
    edit_window.wm_iconphoto(False, ImageTk.PhotoImage(Image.open('assets/psicon.png')))
    
    edit_window_ref = edit_window
    
    edit_window.protocol("WM_DELETE_WINDOW",on_close)

    macro_text = macros[macro]

    placeholders = re.findall(r'XXXXXXX|\[AMOUNT\]|\[DATE\]|\[SENT\]|\[REST\]|\[COUNTRY\]|\[DATE1\]|\[DATE2\]', macro_text)
    unique_placeholders = list(set(placeholders))
    entry_vars = {ph: StringVar() for ph in unique_placeholders}
    
    left_frame = Frame(edit_window)
    left_frame.pack(side=LEFT, fill=BOTH, expand=True)

    text_area = Text(left_frame, wrap=WORD)
    text_area.insert(INSERT, macro_text)
    text_area.config(state=DISABLED)
    text_area.pack(expand=True, fill=BOTH)

    right_frame = Frame(edit_window)
    right_frame.pack(side=RIGHT, fill=Y)
    
    ordered_placeholders = ['XXXXXXX','[AMOUNT]', '[REST]', '[DATE]', '[COUNTRY]','[DATE1]','[DATE2]']
    row = 0
    for placeholder in ordered_placeholders:
        if placeholder in unique_placeholders:
            label = Label(right_frame, text=placeholder)
            label.grid(row=row, column=0, padx=5, pady=5)
            if placeholder == '[DATE]' or placeholder == '[DATE1]':
                entry = DateEntry(right_frame, textvariable=entry_vars[placeholder], date_pattern='dd/MM/yyyy')
            elif placeholder == '[DATE2]':
                entry = DateEntry(right_frame, textvariable=entry_vars[placeholder], date_pattern='dd/MM/yyyy')
                bd_button = Button(right_frame,text='Calculate 3BD',relief=GROOVE,command=lambda:add_3_bd_days())
                bd_button.grid(row=row+1,column=1,padx=5,pady=5)
            elif placeholder == '[COUNTRY]':
                with open("config/countries.json", "r", encoding="utf-8") as file:
                    countries = json.load(file)
                entry = AutocompleteCombobox(right_frame,completevalues=countries ,textvariable=entry_vars[placeholder])
                entry.bind("<<ComboboxSelected>>", lambda e, ph=placeholder: update_macro(text_area, macro_text, entry_vars))
                entry.bind('<FocusOut>', lambda e, ph=placeholder: update_macro(text_area, macro_text, entry_vars))
                entry.bind('<Return>', lambda e, ph=placeholder: update_macro(text_area, macro_text, entry_vars))
            else:
                entry = Entry(right_frame, textvariable=entry_vars[placeholder])
            entry.grid(row=row, column=1, padx=5, pady=5)
            if placeholder != '[COUNTRY]':
                entry.bind('<KeyRelease>', lambda e, ph=placeholder: update_macro(text_area, macro_text, entry_vars))
            if placeholder in ['[DATE]','[DATE1]','[DATE2]']:
                entry.bind('<<DateEntrySelected>>', lambda e, ph=placeholder: update_macro(text_area, macro_text, entry_vars))

            row += 1

    def apply_changes():
        updated_text = macro_text
        for placeholder, var in entry_vars.items():
            updated_text = updated_text.replace(placeholder, format_placeholder_value(placeholder, var.get(), entry_vars))
        pyperclip.copy(updated_text)
        edit_window.destroy()
        search.delete(0, END)
        reset_macro_frame()
        window.update_idletasks()
        window.geometry('')
    
    def add_3_bd_days():
        
        date1 = entry_vars.get('[DATE1]')
        if date1:
            day = datetime.strptime(entry_vars['[DATE1]'].get(),'%d/%m/%Y')
        else:
            day = datetime.strptime(entry_vars['[DATE]'].get(),'%d/%m/%Y')
        i = 0
        while i < 3:
            day = day + timedelta(1)
            if(day.weekday() not in [5,6]):
                i+=1
        day = datetime.strftime(day,"%d/%m/%Y")
        entry_vars['[DATE2]'].set(day)
        update_macro(text_area, macro_text, entry_vars)

    done_button = Button(right_frame, text="Done",relief=GROOVE,command=apply_changes)
    done_button.grid(row=row+2, columnspan=2, pady=10)

def update_macro(text_widget, macro_text, entry_vars):
    updated_text = macro_text
    for placeholder, var in entry_vars.items():
        updated_text = updated_text.replace(placeholder, format_placeholder_value(placeholder, var.get(), entry_vars))
    text_widget.config(state=NORMAL)
    text_widget.delete(1.0, END)
    text_widget.insert(INSERT, updated_text)
    text_widget.config(state=DISABLED)

def format_placeholder_value(placeholder, value, entry_vars):
    if placeholder in ['[DATE]','[DATE1]','[DATE2]']  and value:
        return format_date(value)
    elif placeholder == '[SENT]':
        try:
            amount = extract_number(entry_vars.get('[AMOUNT]', StringVar()).get())
            sent = extract_number(entry_vars.get('[REST]', StringVar()).get())
            rest = amount - sent
            return f"{rest:,.2f} {extract_currency(entry_vars.get('[AMOUNT]', StringVar()).get())}"
        except ValueError:
            return '[INVALID]'
    return value

#------------------------SETTINGS-------------------------#

def open_settings_page():
    
    global settings_window_ref,keyboard_toggle_on,keyboard_toggle_off,keyboard_macros_toggle_button,import_image,export_image,backup_image
    
    if settings_window_ref is not None and settings_window_ref.winfo_exists():
        settings_window_ref.lift()
        settings_window_ref.deiconify()
        return
    
    settings_window = Toplevel(window)
    settings_window.attributes("-topmost",True)
    settings_window.title("Settings")
    settings_window.minsize(200, 100)
    settings_window.wm_iconphoto(False, ImageTk.PhotoImage(Image.open('assets/psicon.png')))
    
    settings_window_ref = settings_window
    
    def on_close():
        global settings_window_ref
        settings_window_ref = None
        settings_window.destroy()
        
    settings_window.protocol("WM_DELETE_WINDOW",on_close)

    import_button = Button(settings_window,text="Import macros ",image=import_image,compound='right',font=("Arial",11),relief=GROOVE,command=import_macros)
    import_button.pack(side='top',anchor=CENTER,pady=10)
    export_button = Button(settings_window,text="Export macros ",image=export_image,compound='right',font=("Arial",11),relief=GROOVE, command=export_macros)
    export_button.pack(side='top',anchor=CENTER,pady=1)
    backup_button = Button(settings_window,text="Create backup ",image=backup_image,compound='right',font=("Arial",11),relief=GROOVE,command=create_backup)
    backup_button.pack(side='top',anchor=CENTER,pady=15)
    
    import_button.image = import_image
    export_button.image = export_image
    backup_button.image = backup_image

    keyboard_options_frame = Frame(settings_window)
    keyboard_options_frame.pack(side='top', anchor=CENTER, pady=1)
    
    keyboard_lable = Label(keyboard_options_frame,text="Keyboard macros:")
    keyboard_lable.pack(side='left',padx=5)
    
    if keyboard_macros_mode:
        keyboard_macros_toggle_button = Button(keyboard_options_frame,text='',bd=0,image=keyboard_toggle_on,command=keyboard_macro_mode_switch)
    else:
        keyboard_macros_toggle_button = Button(keyboard_options_frame,text='',bd=0,image=keyboard_toggle_off,command=keyboard_macro_mode_switch)
    keyboard_macros_toggle_button.pack(side='left',anchor=CENTER,pady=1)
    
    keyboard_macros_manage_button = Button(settings_window,text='Manage keyboard macros',font=("Arial",11),relief=GROOVE,command=manage_keyboard_macros)
    keyboard_macros_manage_button.pack(side='top',anchor=CENTER,pady=10)

def import_macros():
    file_path = filedialog.askopenfilename(title='Import macro file',filetypes=[("JSON file",".json")])
    
    if file_path == '':
        return
    
    with open(file_path,'r',encoding='utf-8') as new_file:
        try:
            new_macros = json.load(new_file)
        except ValueError:
            messagebox.showerror("Error","Import failed")
            return
        
        if new_macros == {}:
            messagebox.showerror("Error","Imported file is empty")
            return
    
    for key,value in new_macros.items():
        if key not in macros and value != "":
            macros.update({key:value})
    with open("macros.json",'w',encoding='utf-8') as file:
        json.dump(macros,file,ensure_ascii=False,indent=4)
    settings_window_ref.destroy()

def export_macros():
    file_path = filedialog.asksaveasfilename(defaultextension='.json',filetypes=[("JSON file",".json")])
    
    if file_path:
        with open(file_path,'w',encoding="utf-8") as file:
            json.dump(macros,file,ensure_ascii=False,indent=4)
    settings_window_ref.destroy()

def create_backup():
    
    folder = "backup"
    filepath = os.path.join(folder,"macros_backup.json")
    
    if not os.path.exists(filepath):
        os.makedirs(folder)
        with open(filepath,'w',encoding='utf-8') as backup:
            json.dump(macros,backup,ensure_ascii=False,indent=4)
            messagebox.showinfo("Backup","Backup successfull created")
    elif messagebox.askyesno("Confirm to delete","Current backup will be deleted. Are you sure you want to continue?"):
        shutil.rmtree(folder)
        create_backup()
    settings_window_ref.destroy()
    
#-----------------------THREADING---------------------#

def monitor_clipboard():
    
    global copied_items,stop_event,clipboard_listener_thread, last_clipboard_copy
    
    source_clipboard = ""
    
    while not stop_event.is_set():
        current = pyperclip.paste()
        
        if current != last_clipboard_copy and current.strip() != '' and current != source_clipboard:
            last_clipboard_copy = current
            copied_items.append(current)
            
            if is_transaction_number(current):
                combined = ', '.join(copied_items)
            else:
                combined = '\n\n'.join(copied_items)
                
            source_clipboard = combined
            pyperclip.copy(combined)
        time.sleep(0.1)
        
def stop_on_paste():
    global clipboard_listener_thread, copy_button, multi_copy_mode

    keyboard.wait("ctrl+v")
    multi_copy_mode = False
    copy_button.config(image=copy_icon)
    stop_event.set()

    if clipboard_listener_thread and clipboard_listener_thread.is_alive():
        clipboard_listener_thread.join()

        
def multi_copy():
    
    global multi_copy_mode,copy_icon,copy_icon_active,copied_items,copy_button,clipboard_listener_thread,stop_event
    
    multi_copy_mode = not multi_copy_mode
    
    if multi_copy_mode:
        copy_button.config(image = copy_icon_active)
        pyperclip.copy("")
        copied_items = []
        stop_event.clear()
        clipboard_listener_thread = threading.Thread(target=monitor_clipboard,daemon=True)
        paste_stop_thread = threading.Thread(target=stop_on_paste,daemon=True)
        clipboard_listener_thread.start()
        paste_stop_thread.start()
    else:
        copy_button.config(image = copy_icon)
        stop_event.set()
        clipboard_listener_thread.join()
        
        
#---------------------------KEYBOARD MACROS--------------------------#

def paste_keyboard_macro(key):
    
    global keyboard_macros
    
    already_coppied = pyperclip.paste()
    pyperclip.copy(keyboard_macros[key])
    time.sleep(0.05)
    keyboard.send('ctrl+v')
    time.sleep(0.05)
    pyperclip.copy(already_coppied)
    
    
def remove_all_hotkeys():
    for hotkey_id in list(keyboard._hotkeys):
        try:
            keyboard.remove_hotkey(hotkey_id)
        except KeyError:
            pass

def refresh_hotkeys():
    
    global keyboard_macros
    
    remove_all_hotkeys()
        
    for key in keyboard_macros:
        keyboard.add_hotkey(key,lambda k=key: paste_keyboard_macro(k),suppress=True)

    
def keyboard_macro_mode_switch():
    
    global keyboard_macros_mode,keyboard_macros_toggle_button,keyboard_toggle_on,keyboard_toggle_off,keyboard_macros,hotkeys
    
    keyboard_macros_mode = not keyboard_macros_mode
    
    keyboard_macros = load_keyboard_macros()
        
    if keyboard_macros_mode:
        keyboard_macros_toggle_button.config(image = keyboard_toggle_on)
        
        for key in keyboard_macros:
            keyboard.add_hotkey(key,lambda k=key: paste_keyboard_macro(k),suppress=True)
    else:
        keyboard_macros_toggle_button.config(image = keyboard_toggle_off)
        remove_all_hotkeys()

def manage_keyboard_macros():
    
    global keyboard_macros_window_ref,keyboard_macros,eye_img,edit_img,delete_img
    
    keyboard_macros = load_keyboard_macros()
    
    if keyboard_macros_window_ref is not None and keyboard_macros_window_ref.winfo_exists():
        keyboard_macros_window_ref.lift()
        keyboard_macros_window_ref.deiconify()
        return
    
    keyboard_macros_window = Toplevel(window)
    keyboard_macros_window.attributes("-topmost",True)
    keyboard_macros_window.title("Settings")
    keyboard_macros_window.minsize(200, 50)
    keyboard_macros_window.wm_iconphoto(False, ImageTk.PhotoImage(Image.open('assets/psicon.png')))
    
    keyboard_macros_window_ref = keyboard_macros_window
    
    def on_close():
        global keyboard_macros_window_ref
        keyboard_macros_window_ref = None
        keyboard_macros_window.destroy()
        
    keyboard_macros_window.protocol("WM_DELETE_WINDOW",on_close)
    
    if not keyboard_macros:
        no_keyboard_macros_frame = Frame(keyboard_macros_window)
        no_keyboard_macros_frame.pack(expand=True)
        
        empty_image_org = Image.open("assets/empty.png")
        resized_empty = empty_image_org.resize((70,70),Image.LANCZOS)
        empty_image = ImageTk.PhotoImage(resized_empty)
        
        empty_image_label = Label(no_keyboard_macros_frame,text='',image=empty_image)
        empty_image_label.image = empty_image
        empty_image_label.pack(side='top',anchor=CENTER,pady=0)
        empty_message_label = Label(no_keyboard_macros_frame,text="No keyboard macros found")
        empty_message_label.pack(side='top',anchor=CENTER)
        
        add_button = Button(no_keyboard_macros_frame,text="Add New",relief=GROOVE,command=add_keyboard_macro)
        add_button.pack(side="top",anchor=CENTER,pady=20)
    
    else:

        table_frame = Frame(keyboard_macros_window)
        table_frame.pack(padx=10, pady=10, anchor="w")

        Label(table_frame, text="Key", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=5)
        Label(table_frame, text="View").grid(row=0, column=1, padx=5, pady=5)
        Label(table_frame, text="Edit").grid(row=0, column=2, padx=5, pady=5)
        Label(table_frame, text="Delete").grid(row=0, column=3, padx=5, pady=5)

        for idx, keyboard_macro in enumerate(keyboard_macros, start=1):

            Label(table_frame, text=keyboard_macro, width=6, anchor="w").grid(row=idx, column=0, padx=0, pady=3, sticky="w")

            btn_view = Button(table_frame, image=eye_img, bd=0,command=lambda k=keyboard_macro: view_keyboard_macro(k))
            btn_view.image = eye_img
            btn_view.grid(row=idx, column=1, padx=5, pady=3)

            btn_edit = Button(table_frame, image=edit_img,bd=0, command=lambda k=keyboard_macro: edit_keyboard_macro(k))
            btn_edit.image = edit_img
            btn_edit.grid(row=idx, column=2, padx=5, pady=3)

            btn_delete = Button(table_frame, image=delete_img,bd=0,command=lambda k=keyboard_macro:confirm_keyboard_macro_delete(k))
            btn_delete.image = delete_img
            btn_delete.grid(row=idx, column=3, padx=5, pady=3)

        add_keyboard_macro_button = Button(keyboard_macros_window, text="+ Add New", relief=GROOVE, command=add_keyboard_macro)
        add_keyboard_macro_button.pack(pady=10)

def view_keyboard_macro(key):
    view_window = Toplevel(window)
    view_window.attributes("-topmost",True)
    view_window.title(f"Key {key} macro")
    view_window.minsize(300, 200)
    view_window.wm_iconphoto(False, ImageTk.PhotoImage(Image.open('assets/psicon.png')))
    
    left_frame = Frame(view_window)
    left_frame.pack(side=LEFT,fill=BOTH,expand = True)

    text = Text(left_frame, wrap=WORD)
    text.insert(INSERT, keyboard_macros[key])
    text.config(state=DISABLED)
    text.pack(expand=True, fill=BOTH)
    
    right_frame = Frame(view_window)
    right_frame.pack(side=RIGHT,fill=BOTH,expand=True)
    
def edit_keyboard_macro(key):
    
    global edit_keyboard_window_ref, keyboard_macros
    
    if edit_keyboard_window_ref is not None and edit_keyboard_window_ref.winfo_exists():
        edit_keyboard_window_ref.lift()
        return
    
    def on_close():
        global edit_keyboard_window_ref
        edit_keyboard_window_ref = None
        edit_keyboard_window.destroy()
        
    edit_keyboard_window = Toplevel(window)
    edit_keyboard_window.attributes("-topmost",True)

    edit_keyboard_window.title(f"Edit {key} macro")
    edit_keyboard_window.minsize(600, 400)
    edit_keyboard_window.wm_iconphoto(False, ImageTk.PhotoImage(Image.open('assets/psicon.png')))
    
    edit_keyboard_window_ref = edit_keyboard_window
    
    edit_keyboard_window.protocol("WM_DELETE_WINDOW",on_close)
    
    left_frame = Frame(edit_keyboard_window)
    left_frame.pack(side=LEFT,fill=BOTH,expand = True)

    text = Text(left_frame, wrap=WORD)
    text.insert(INSERT, keyboard_macros[key])
    text.pack(expand=True, fill=BOTH)
    
    right_frame = Frame(edit_keyboard_window)
    right_frame.pack(side=RIGHT,fill=BOTH,expand=True)
    
    def done():
        if keyboard_macros[key] != text.get('1.0','end-1c'):
            keyboard_macros[key] = text.get('1.0','end-1c')
            with open('config/keyboard_macros.json','w',encoding='utf-8') as file:
                json.dump(keyboard_macros,file,indent=4,ensure_ascii=False)
        edit_keyboard_window.destroy()
        
    done_button = Button(right_frame,text='Done',font=("Arial bold",10),command=done)
    done_button.pack(side=BOTTOM,anchor='se', padx=10, pady=10)

def delete_keyboard_macro(key):
    
    global keyboard_macros,hotkeys
    
    if key in keyboard_macros:
        del keyboard_macros[key]
        with open('config/keyboard_macros.json','w',encoding='utf-8') as file:
            json.dump(keyboard_macros,file,indent=4,ensure_ascii=False)
        
        if keyboard_macros_window_ref and keyboard_macros_window_ref.winfo_exists():
                keyboard_macros_window_ref.destroy()

        if keyboard_macros_mode:
            refresh_hotkeys()
        
        manage_keyboard_macros()
            
def confirm_keyboard_macro_delete(key):
    answer = messagebox.askyesno("Confirm to delete",f"Are you sure you want to delete macro for {key}?")
    if answer:
        delete_keyboard_macro(key)

def add_keyboard_macro():
    
    global add_keyboard_macro_window_ref,keyboard_macros, keyboard_macros_mode
    
    key = None
    
    if add_keyboard_macro_window_ref is not None and add_keyboard_macro_window_ref.winfo_exists():
        add_keyboard_macro_window_ref.lift()
        return
    
    add_keyboard_macro_window = Toplevel(window)
    add_keyboard_macro_window.attributes("-topmost",True)
    add_keyboard_macro_window.title("Add New Macro")
    add_keyboard_macro_window.minsize(600, 200)
    add_keyboard_macro_window_ref = add_keyboard_macro_window
    
    def on_close():
        global add_keyboard_macro_window_ref
        add_keyboard_macro_window_ref = None
        add_keyboard_macro_window.destroy()
        
    add_keyboard_macro_window.protocol("WM_DELETE_WINDOW", on_close)

    key_label = Label(add_keyboard_macro_window, text="Keyboard key:")
    key_label.grid(row=0, column=0, padx=10, pady=10)
    
    def keyboard_listen():
        
        key_entry.config(text="Waiting...")
        
        def wait_for_key():
            nonlocal key
            pressed_key = keyboard.read_key()
            key = pressed_key.upper()
            key_entry.config(text=key)
            
        threading.Thread(target=wait_for_key, daemon=True).start()
    
    key_frame = Frame(add_keyboard_macro_window)
    key_frame.grid(row=0,column=1,padx=10,pady=10)
    key_entry = Label(key_frame,text="No key added")
    key_entry.pack(side='left')
    key_comfirm_button = Button(key_frame,text="Add key",relief=GROOVE, command= keyboard_listen)
    key_comfirm_button.pack(side='left',padx=10)

    macro_text_label = Label(add_keyboard_macro_window, text="Macro Text:")
    macro_text_label.grid(row=1, column=0, padx=10, pady=10)
    macro_text_entry = Text(add_keyboard_macro_window, wrap=WORD, height=10)
    macro_text_entry.grid(row=1, column=1, padx=10, pady=10)
    
    def save_keyboard_macro():
        
        nonlocal key
        
        macro_text = macro_text_entry.get("1.0", "end-1c")
        if key and macro_text != '':
            keyboard_macros[key] = macro_text
            with open('config/keyboard_macros.json', 'w', encoding='utf-8') as file:
                json.dump(keyboard_macros, file, ensure_ascii=False, indent=4)
            add_keyboard_macro_window.destroy()
            
            if keyboard_macros_window_ref and keyboard_macros_window_ref.winfo_exists():
                keyboard_macros_window_ref.destroy()
                
            if keyboard_macros_mode:
                refresh_hotkeys()

            manage_keyboard_macros()
            
    save_button = Button(add_keyboard_macro_window, text="Save", relief=GROOVE,command= save_keyboard_macro)
    save_button.grid(row=2, columnspan=2, pady=10)
    
#--------------------------BIN LOOKUP-----------------------------#

def checkBin(bin_number):

    global macro_frame,search
    
    url = f"https://data.handyapi.com/bin/{bin_number}"
    
    response = requests.get(url)
    
    reset_macro_frame()
    bin_frame = Frame(macro_frame, bg='lightgrey', bd=2, relief=RAISED)
    bin_frame.grid(row=0, column=0, pady=2, sticky="ew")
    bin_frame.bind("<Button-1>", lambda event: (reset_macro_frame(),search.delete(0, END)))

    if response.ok:
        response = response.json()
        if response['Status'] == 'SUCCESS':
            res = f"Type: {response['Type']}\nBrand: {response['Scheme']}\nCountry: {response['Country']['Name']}\nBank: {response['Issuer']}"
        else:
            res = "NOT FOUND"
    else:
        res = "Server error"
        
    label = Label(bin_frame, width=30, text=res, bg='lightgrey', anchor="w", justify=LEFT)
    label.pack(side=LEFT, padx=10, pady=10)
    label.bind("<Button-1>", lambda event: (reset_macro_frame(),search.delete(0, END)))

#-------------------------COUNTRY_CODE_LOOKUP------------------------------------#

def findCountry(country_code):
    key = country_code if country_code.startswith('+') else f"+{country_code}"

    try:
        with open('config/country_codes.json', 'r', encoding='utf-8') as file:
            countries = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return "NOT FOUND"

    return countries.get(key, "NOT FOUND")

#---------------------------MAIN---------------------------------#

window = Tk()
window.title("Paysend macro manager")
window.minsize(230,50)
window.attributes("-topmost", True)

window.wm_iconphoto(False, ImageTk.PhotoImage(Image.open("assets/psicon.png")))

macros = load_macros()

add_window_ref = None
edit_window_ref = None
settings_window_ref = None
search_after_id = None
keyboard_macros_window_ref = None
add_keyboard_macro_window_ref = None
edit_keyboard_window_ref = None

delete_mode = False
multi_copy_mode = False
keyboard_macros_mode = False
copied_items = []
stop_event = threading.Event()
clipboard_listener_thread = None
paste_stop_thread = None
last_clipboard_copy = ""
already_copied = ''

keyboard_macros = []

searchTerm = StringVar()
search = Entry(window, width=22, font=8,textvariable=searchTerm)
search.bind('<KeyRelease>',on_search_key)
search.grid(row=0, column=0)

macro_frame = Frame(window)
macro_frame.grid(row=1, column=0)
macro_frame.grid_propagate(True)

eye_img = ImageTk.PhotoImage(Image.open("assets/eye.png").resize((20, 20), Image.LANCZOS))
edit_img = ImageTk.PhotoImage(Image.open("assets/pen.png").resize((20, 20), Image.LANCZOS))
delete_img = ImageTk.PhotoImage(Image.open("assets/delete_active.png").resize((20, 20), Image.LANCZOS))
del_img = PhotoImage(file="assets/delete.png")
del_active_img = PhotoImage(file="assets/delete_active.png")

add_img = PhotoImage(file="assets/add.png")

right_click_menu = Menu(window,tearoff=0)
right_click_menu.add_command(label="View  ",image=eye_img,compound='right',command=lambda:view_macro(selected_macro))
right_click_menu.add_separator()
right_click_menu.add_command(label="Edit ",image=edit_img,compound='right',command=lambda:right_click_edit(selected_macro))
right_click_menu.add_separator()
right_click_menu.add_command(label="Delete ",image=delete_img,compound='right',command=lambda:confirm_delete(selected_macro))


button_frame = Frame(window)
button_frame.grid(row=2,column=0, sticky='ew')
button_frame.grid_columnconfigure(0, weight=1)
button_frame.grid_propagate(True)

plus_button = Button(button_frame,relief=GROOVE, image=add_img, command=add_macro)
plus_button.grid(row=1, column=3, sticky="se", padx=1, pady=1)

delete_button = Button(button_frame,relief=GROOVE,image=del_img,fg='grey',command=delete_mode_change)
delete_button.grid(row=1,column=2,sticky="se",padx=1,pady=1)

settings_image = PhotoImage(file="assets/settings.png")
settings_button = Button(button_frame,image=settings_image,relief=GROOVE,command=open_settings_page)
settings_button.grid(row=1,column=1,sticky="se",padx=1,pady=1)

copy_icon= PhotoImage(file='assets/copy.png')
copy_icon_active = PhotoImage(file='assets/copy_active.png')
copy_button = Button(button_frame,relief=GROOVE, image=copy_icon,command=multi_copy)
copy_button.grid(row=1,column=0,sticky="se",padx=1,pady=1)

import_image = ImageTk.PhotoImage(Image.open("assets/import.png").resize((19,19),Image.LANCZOS))
export_image = ImageTk.PhotoImage(Image.open("assets/export.png").resize((19,19),Image.LANCZOS))
backup_image = ImageTk.PhotoImage(Image.open("assets/backup.png").resize((20,20),Image.LANCZOS))

keyboard_macros_toggle_button = Button()

keyboard_on = Image.open("assets/on.png")
resized_on = keyboard_on.resize((50,20),Image.LANCZOS)
keyboard_toggle_on = ImageTk.PhotoImage(resized_on)

keyboard_off = Image.open("assets/off.png")
resized_off = keyboard_off.resize((50,20),Image.LANCZOS)
keyboard_toggle_off = ImageTk.PhotoImage(resized_off)

window.mainloop()