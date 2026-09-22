import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import os,json,webbrowser,datetime,csv,hashlib,urllib.request,tempfile,shutil,subprocess,sys
APP_NAME='After Hours AI Mega Studio V17'; APP_VERSION='17.0.0'
REPO='kevinfoley-hub/after-hours-ai-studio-updates'
MANIFEST='https://raw.githubusercontent.com/'+REPO+'/main/update_manifest.json'
BASE=Path.home()/'Documents'/'After Hours AI Mega Studio'; BOOKS=BASE/'BookFactory'; DATA=BASE/'Data'
for p in (BASE,BOOKS,DATA): p.mkdir(parents=True,exist_ok=True)
CFG=DATA/'v17_config.json'
def load():
    d={'first_run':True,'author':'','pen_name':'','quality_gate':True,'ai_disclosure':True,'daily_target':10}
    try:d.update(json.loads(CFG.read_text(encoding='utf-8')))
    except:pass
    return d
cfg=load()
URLS={'ChatGPT':'https://chatgpt.com/','Canva':'https://www.canva.com/','OpenArt':'https://openart.ai/','Adobe Express':'https://new.express.adobe.com/','Amazon KDP':'https://kdp.amazon.com/','Kobo':'https://www.kobo.com/writinglife','Google Play Books':'https://play.google.com/books/publish/','GitHub':'https://github.com/'+REPO}
def open_url(n): webbrowser.open(URLS[n])
def ver(v):
    try:return tuple(map(int,v.split('.')))
    except:return (0,)
def check_updates(silent=False):
    try:
        m=json.loads(urllib.request.urlopen(MANIFEST,timeout=12).read().decode())
        latest=m.get('version','0.0.0')
        if ver(latest)<=ver(APP_VERSION):
            if not silent: messagebox.showinfo('Updates','You already have the latest version.')
            return
        url=m.get('url',''); sha=m.get('sha256','').lower(); notes=m.get('notes','')
        if not url or not sha:
            if not silent: messagebox.showinfo('Update available',f'Version {latest} is listed but the EXE is not ready yet.\n\n{notes}')
            return
        if messagebox.askyesno('Update available',f'Version {latest} is available.\n\n{notes}\n\nInstall now?'): apply_update(url,sha,latest)
    except Exception as e:
        if not silent: messagebox.showwarning('Update check',str(e))
def apply_update(url,expected,latest):
    try:
        d=Path(tempfile.gettempdir())/'AfterHoursV17Update'; d.mkdir(exist_ok=True)
        new=d/f'After_Hours_AI_Mega_Studio_V{latest}.exe'
        with urllib.request.urlopen(url,timeout=90) as r,open(new,'wb') as f: shutil.copyfileobj(r,f)
        h=hashlib.sha256(new.read_bytes()).hexdigest().lower()
        if h!=expected: new.unlink(missing_ok=True); return messagebox.showerror('Update blocked','SHA-256 verification failed.')
        cur=Path(sys.executable)
        if cur.suffix.lower()!='.exe': return messagebox.showinfo('Update verified',f'Verified update downloaded to:\n{new}')
        backup=cur.with_name(cur.stem+'_backup.exe'); bat=d/'APPLY_UPDATE.bat'
        bat.write_text(f'@echo off\ntimeout /t 2 /nobreak >nul\ncopy /y "{cur}" "{backup}" >nul\ncopy /y "{new}" "{cur}" >nul\nstart "" "{cur}"\ndel "%~f0"\n')
        subprocess.Popen(['cmd','/c',str(bat)],creationflags=0x08000000); root.destroy()
    except Exception as e: messagebox.showerror('Update failed',str(e))
def first_run():
    w=tk.Toplevel(root); w.title('First-Time Setup'); w.geometry('720x560'); w.configure(bg=BG); w.grab_set()
    tk.Label(w,text='Welcome to V17',bg=BG,fg=TEXT,font=('Segoe UI',22,'bold')).pack(anchor='w',padx=24,pady=(24,8))
    msg=('GitHub is now connected. V17 uses your public update repository automatically.\n\n'
         '1. Keep this repository public so the app can read update_manifest.json.\n'
         '2. Open Settings and add your author or pen name.\n'
         '3. Book Factory can prepare up to 10 book jobs per batch.\n'
         '4. Review every book before publishing. Keep Quality Approval and AI Disclosure checks enabled.\n'
         '5. Amazon/Kobo/Google Play publishing still uses each platform’s official account and review process.')
    tk.Label(w,text=msg,bg=PANEL,fg=TEXT,justify='left',wraplength=650,padx=18,pady=18).pack(fill='both',expand=True,padx=24,pady=12)
    def done(): cfg['first_run']=False; CFG.write_text(json.dumps(cfg,indent=2)); w.destroy()
    ttk.Button(w,text='Open Update Repository',command=lambda:open_url('GitHub')).pack(fill='x',padx=24,pady=5)
    ttk.Button(w,text='Finish Setup',style='Accent.TButton',command=done).pack(fill='x',padx=24,pady=(5,20))
def book_prompt(title,topic):
    who=pen.get().strip() or author.get().strip() or 'Author name to be supplied'
    return f'''Create an ORIGINAL, useful, professionally edited non-fiction book production package.\nTITLE: {title}\nTOPIC: {topic}\nAUTHOR/PEN NAME: {who}\n\nDeliver: reader promise, detailed TOC, full manuscript, fact-check list, editing checklist, description, 7 accurate keyword phrases, 3 category suggestions, subtitle options, cover concept, author bio, launch copy and AI-content disclosure note.\n\nRules: no copying or imitation, no invented citations, no keyword stuffing, flag facts needing verification, avoid trademark/copyright misuse, and do not assume publication approval.'''
def create_batch():
    try:n=max(1,min(10,int(count.get())))
    except:n=10
    topic=topic_var.get().strip() or 'practical everyday skills'; batch=BOOKS/f'{datetime.datetime.now():%Y%m%d_%H%M}_Batch'; batch.mkdir()
    themes=['Beginners Guide','30-Day Plan','Practical Handbook','Quick Start Guide','Mistakes to Avoid','Step-by-Step Blueprint','Reference Guide','Simple Systems','Action Workbook','Problem-Solving Guide']
    for i in range(n):
        title=f'{themes[i]}: {topic.title()}'; folder=batch/f'{i+1:02d}_{title.replace(":","-")}'; folder.mkdir()
        (folder/'BOOK_MASTER_PROMPT.txt').write_text(book_prompt(title,topic),encoding='utf-8')
        (folder/'book_job.json').write_text(json.dumps({'title':title,'status':'WAITING_FOR_AI','quality_approved':False,'ai_disclosure_confirmed':False,'folder':str(folder)},indent=2))
    os.startfile(batch); refresh()
def refresh():
    for x in tree.get_children():tree.delete(x)
    for f in BOOKS.rglob('book_job.json'):
        try:
            j=json.loads(f.read_text()); tree.insert('', 'end',values=(j['title'],j['status'],'Yes' if j.get('quality_approved') else 'No',j['folder']))
        except:pass
def selected_job():
    s=tree.selection()
    if not s:return None,None
    folder=Path(tree.item(s[0],'values')[3]); return folder,folder/'book_job.json'
def generate_selected():
    folder,jf=selected_job()
    if not folder:return messagebox.showinfo('Book Factory','Select a book first.')
    root.clipboard_clear(); root.clipboard_append((folder/'BOOK_MASTER_PROMPT.txt').read_text(encoding='utf-8')); root.update(); open_url('ChatGPT')
def approve():
    folder,jf=selected_job()
    if not jf:return
    j=json.loads(jf.read_text()); j['quality_approved']=True; j['status']='QUALITY_APPROVED'; jf.write_text(json.dumps(j,indent=2)); refresh()
def disclose():
    folder,jf=selected_job()
    if not jf:return
    j=json.loads(jf.read_text()); j['ai_disclosure_confirmed']=True; jf.write_text(json.dumps(j,indent=2)); refresh()
def publish(platform):
    folder,jf=selected_job()
    if not jf:return messagebox.showinfo('Publishing','Select a book in Book Factory first.')
    j=json.loads(jf.read_text())
    if quality_gate.get() and not j.get('quality_approved'):return messagebox.showwarning('Quality required','Mark the book Quality Approved first.')
    if disclosure_gate.get() and not j.get('ai_disclosure_confirmed'):return messagebox.showwarning('Disclosure required','Confirm AI disclosure before publishing.')
    open_url(platform); messagebox.showinfo('Publishing handoff','Official publisher page opened. Complete the platform’s required review and submission steps.')
def save_settings():
    cfg.update(author=author.get(),pen_name=pen.get(),quality_gate=quality_gate.get(),ai_disclosure=disclosure_gate.get()); CFG.write_text(json.dumps(cfg,indent=2)); status.set('Settings saved')
def show(name):
    for p in pages.values():p.pack_forget()
    pages[name].pack(fill='both',expand=True); title_lbl.config(text=name)
BG='#07101d';PANEL='#101b2e';PANEL2='#182740';TEXT='#f6f8fc';MUTED='#9eabc0';ACC='#7c5cff'
root=tk.Tk();root.title(APP_NAME);root.geometry('1350x820');root.configure(bg=BG)
st=ttk.Style();st.theme_use('clam');st.configure('Accent.TButton',background=ACC,foreground='white',padding=10,font=('Segoe UI',10,'bold'));st.configure('TButton',padding=9)
author=tk.StringVar(value=cfg.get('author',''));pen=tk.StringVar(value=cfg.get('pen_name',''));quality_gate=tk.BooleanVar(value=cfg.get('quality_gate',True));disclosure_gate=tk.BooleanVar(value=cfg.get('ai_disclosure',True));topic_var=tk.StringVar(value='AI, productivity and practical guides');count=tk.StringVar(value='10');status=tk.StringVar(value='Ready')
head=tk.Frame(root,bg=BG);head.pack(fill='x',padx=20,pady=14);tk.Label(head,text='AFTER HOURS  V17',bg=BG,fg=TEXT,font=('Segoe UI',24,'bold')).pack(side='left');tk.Label(head,text='BOOK FACTORY • AUTO UPDATES',bg=PANEL2,fg=MUTED,padx=12,pady=7).pack(side='right')
main=tk.Frame(root,bg=BG);main.pack(fill='both',expand=True,padx=18);side=tk.Frame(main,bg=PANEL,width=220);side.pack(side='left',fill='y',padx=(0,14));side.pack_propagate(False);content=tk.Frame(main,bg=BG);content.pack(fill='both',expand=True)
title_lbl=tk.Label(content,text='Home',bg=BG,fg=TEXT,font=('Segoe UI',20,'bold'));title_lbl.pack(anchor='w',pady=(4,10));holder=tk.Frame(content,bg=BG);holder.pack(fill='both',expand=True);pages={}
for n in ['Home','Book Factory','Publishing','AI Tools','Updates','Settings']: ttk.Button(side,text=n,command=lambda x=n:show(x)).pack(fill='x',padx=12,pady=4)
ttk.Button(side,text='First-Time Setup',style='Accent.TButton',command=first_run).pack(fill='x',padx=12,pady=(20,4))
home=tk.Frame(holder,bg=BG);pages['Home']=home;tk.Label(home,text='Create books. Manage AI. Keep the app updated.',bg=BG,fg=TEXT,font=('Segoe UI',22,'bold')).pack(anchor='w',pady=20);ttk.Button(home,text='Create 10 Book Jobs',style='Accent.TButton',command=create_batch).pack(fill='x',pady=6);ttk.Button(home,text='Check for Updates',command=check_updates).pack(fill='x',pady=6)
bf=tk.Frame(holder,bg=BG);pages['Book Factory']=bf;ttk.Entry(bf,textvariable=topic_var).pack(fill='x',pady=5);ttk.Entry(bf,textvariable=count).pack(fill='x',pady=5);ttk.Button(bf,text='CREATE BOOK JOBS',style='Accent.TButton',command=create_batch).pack(fill='x',pady=5);tree=ttk.Treeview(bf,columns=('title','status','qa','folder'),show='headings');
for c,h,w in [('title','Title',420),('status','Status',180),('qa','QA',60),('folder','Folder',420)]:tree.heading(c,text=h);tree.column(c,width=w)
tree.pack(fill='both',expand=True,pady=8);r=tk.Frame(bf,bg=BG);r.pack(fill='x');
for text,cmd in [('Generate with ChatGPT',generate_selected),('Quality Approved',approve),('Confirm AI Disclosure',disclose),('Refresh',refresh)]:ttk.Button(r,text=text,command=cmd).pack(side='left',fill='x',expand=True,padx=2)
pub=tk.Frame(holder,bg=BG);pages['Publishing']=pub;tk.Label(pub,text='Official publishing handoffs',bg=BG,fg=TEXT,font=('Segoe UI',18,'bold')).pack(anchor='w',pady=12)
for n in ['Amazon KDP','Kobo','Google Play Books']:ttk.Button(pub,text=n,command=lambda x=n:publish(x)).pack(fill='x',pady=5)
tools=tk.Frame(holder,bg=BG);pages['AI Tools']=tools
for n in ['ChatGPT','Canva','OpenArt','Adobe Express','GitHub']:ttk.Button(tools,text='Open '+n,command=lambda x=n:open_url(x)).pack(fill='x',pady=5)
upd=tk.Frame(holder,bg=BG);pages['Updates']=upd;tk.Label(upd,text='Automatic Updates',bg=BG,fg=TEXT,font=('Segoe UI',18,'bold')).pack(anchor='w',pady=12);tk.Label(upd,text='Current version: '+APP_VERSION,bg=BG,fg=MUTED).pack(anchor='w');ttk.Button(upd,text='Check for Updates Now',style='Accent.TButton',command=check_updates).pack(fill='x',pady=10);ttk.Button(upd,text='Open Update Repository',command=lambda:open_url('GitHub')).pack(fill='x',pady=5)
settings=tk.Frame(holder,bg=BG);pages['Settings']=settings
for label,var in [('Author name',author),('Pen name',pen)]:tk.Label(settings,text=label,bg=BG,fg=MUTED).pack(anchor='w');ttk.Entry(settings,textvariable=var).pack(fill='x',pady=(0,8))
ttk.Checkbutton(settings,text='Require quality approval before publishing',variable=quality_gate).pack(anchor='w',pady=5);ttk.Checkbutton(settings,text='Require AI disclosure confirmation',variable=disclosure_gate).pack(anchor='w',pady=5);ttk.Button(settings,text='Save Settings',style='Accent.TButton',command=save_settings).pack(fill='x',pady=10)
tk.Label(root,textvariable=status,bg=PANEL,fg=MUTED,anchor='w').pack(fill='x',side='bottom',padx=18,pady=6)
refresh();show('Home')
if cfg.get('first_run',True):root.after(700,first_run)
root.after(3500,lambda:check_updates(True if False else True) if False else check_updates(silent=True))
root.mainloop()
