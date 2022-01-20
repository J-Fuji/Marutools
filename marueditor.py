import argparse, libtools, os, sys

__version__="Marueditor b1.0.0"
__revision__="0"

class DefaultArgv:
    log_level=0
    filepath=None

class Editor():
    def __init__(self, argv=DefaultArgv):
        self.argv=argv
        self.opening={}
    def Setup(self, appinfo=None):
        self.LoadConfig()
        self.Loadl10n()
        self.LoadLogger()
        if not appinfo is None:
            self.appinfo.update(**appinfo)
        libtools.core.adjustEnv(self.logger.getChild("AdjustEnv"), self.appinfo)
        self.addon=libtools.Addon(self.logger.getChild("Addon"), self.appinfo)
        self.addon.loadAll(self.appinfo["addons"],"editor")
        self.logger.info("start")
        self.ui=libtools.UI.UI(self.config, self.logger.getChild("UI"))
        self.ui.changeIcon(os.path.join(self.appinfo["image"],"marueditor.png"))
        self.ui.setcallback("close", self.exit)
        self.ui.changeSize('500x500')
        self.ui.notebook=self.ui.Notebook(close=True, command=self.close, onzero=self.exit)
        self.ui.notebook.pack(fill="both", expand=True)
    def mainloop(self):
        self.ui.mainloop()
    def LoadConfig(self):
        import platform, locale
        default_conf={"welcome":1, "lang":"ja_JP"}
        if platform.system() == "Windows":
            default_conf.update(theme="xpnative")
        elif platform.system() == "Darwin":
            default_conf.update(theme="aqua")
        else:
            default_conf.update(theme="default")
        if None in locale.getlocale():
            default_conf.update([("lang",locale.getlocale()[0]),("encode",locale.getlocale()[1])])
        else:
            default_conf.update([("lang",locale.getdefaultlocale()[0]),("encode",locale.getdefaultlocale()[1])])
        self.config=libtools.Config("Marueditor", default_conf=default_conf)
        self.appinfo=self.config.appinfo
        self.conf=self.config.conf
    def Loadl10n(self, language=None):
        if language is None:
            language=self.conf["lang"]
        req = ['welcome', 'marueditor', 'exit', 'close_all', 'close_tab', 'save', 'save_as', 'save_from', 'open_from', 'open',
        'new', 'file', 'open_new', 'full_screen', 'help', 'window', 'setting', 'addon', 'file_addon', 'delete', 'marueditor_file',
        'all', 'error', 'error_cant_open', 'select_file_type', 'next', 'check', 'save_check', 'were_sorry', 'new_main', 'back', 
        'cancel', 'dir_name', 'choose_dir', 'file_name', 'new_sub1', 'new_sub2', 'new_check', 'wait', 'done', 'new_e1', 'new_e2', 
        'new_e3', 'done_msg', 'new_e1_msg', 'chk_upd', 'style', 'lang', 'st_open_from', 'st_dnd', 'new_check2', 'about']
        self.lang = libtools.Lang(self.appinfo, req)
        self.txt = self.lang.getText(language)
    def LoadLogger(self):
        #logging
        if "log_dir" in self.conf:
            self.appinfo["log"] = self.conf["log_dir"]
        log_dir = self.appinfo["log"]
        self.logger=libtools.core.Logger(log_dir=log_dir, log_level=self.argv.log_level, name="")
    def CreateMenu(self):
        self.ui.menu=self.ui.Menu(type="bar")
        self.ui.menu.apple=self.ui.menu.add_category("apple", name="apple")#Macos apple menu
        if not self.ui.menu.apple is None:
            self.ui.menu.apple.add_item(type="button", label="About Marueditor")
            self.ui.menu.apple.add_item(type="separator")
        #self.ui.menu.system=self.ui.menu.add_category("system", name="system")#Windows icon menu(Disabled)
        #if not self.ui.menu.system is None:
        #    self.ui.menu.system.add_item(type="checkbutton", label="Fullscreen", command=self.ui.fullscreen)
        #    self.ui.menu.system.add_item(type="separator")
        self.ui.menu.file=self.ui.menu.add_category("File")#File
        self.ui.menu.file.add_item(type="button", label="New File", command=self.new)
        self.ui.menu.file.add_item(type="button", label="Open", command=self.open)
        self.ui.menu.file.add_item(type="button", label="Open as...", command=lambda: self.open(force_select=True))
        self.ui.menu.file.add_item(type="button", label="Save", command=self.save)
        self.ui.menu.file.add_item(type="button", label="Save as...", command=lambda: self.save(as_other=True))
        self.ui.menu.file.add_item(type="button", label="Close tab", command=self.close)
        self.ui.menu.file.add_item(type="button", label="Close all", command=self.exit)
        self.ui.menu.edit=self.ui.menu.add_category("Edit", name="edit")#Edit
        self.ui.menu.window=self.ui.menu.add_category("Window", name="window")#Window
        self.ui.menu.window.add_item(type="checkbutton", label="Fullscreen", command=self.ui.fullscreen)
        self.ui.menu.window.add_item(type="button", label="Open New Window", command=lambda: run(argv=self.argv))
        self.ui.menu.settings=self.ui.menu.add_item(type="button", label="Settings")#Settings
        self.ui.menu.help=self.ui.menu.add_category("Help", name="help")#Help
        self.ui.menu.help.add_item(type="button", label="Version and License", command=self.version)
    def welcome(self):
        self.welcome_tab=self.ui.notebook.add_tab(label="Welcome!")
        self.welcome_tab.label=self.welcome_tab.Label(text="Welcome to Marueditor!\nWhat would you like to do?")
        self.welcome_tab.label.pack()
        self.welcome_tab.new=self.welcome_tab.Input.Button(label="Create New File", command=self.new)
        self.welcome_tab.new.pack(fill="x", side="top")
        self.welcome_tab.open=self.welcome_tab.Input.Button(label="Open File", command=lambda: self.open(as_diff_type=True))
        self.welcome_tab.open.pack(fill="x", side="top")
        if self.welcome_tab.backend=="tkinter":
            if self.welcome_tab.dnd:
                def dnd_process(event):
                    for file in event.data:
                        self.open(file=file, as_diff_type=True)
                self.welcome_tab.frame=self.welcome_tab.Frame(label="Drop file here!")
                self.welcome_tab.frame.pack(fill="both", expand=True)
                self.welcome_tab.frame.setup_dnd(dnd_process, "file")
    def open(self, file=None, as_diff_type=False, force_select=False):#TODO: mime and directory
        def select_addon(exts, recom=None):
            root=self.ui.makeSubWindow(dialog=True)
            root.title=root.Label(text="Please select an addon.\nFile:"+file)
            root.title.pack()
            root.list=root.Input.List()
            root.list.pack(expand=True, fill="both")
            def cancel():
                root.list.set_selection([])
                root.close()
            def ok():
                if len(root.list.value) == 1:
                    root.close()
            root.ok=root.Input.Button(label="OK", command=ok)
            root.ok.pack(expand=True, fill="both", side="bottom")
            root.cancel=root.Input.Button(label="Cancel", command=cancel)
            root.cancel.pack(expand=True, fill="both", side="bottom")
            for ext, addons in exts.items():
                for addon in addons:
                    if not root.list.exist_item(addon):
                        root.list.add_item(label=addon, id=addon)
                    root.list.add_item(label=ext, id=addon+"."+ext, parent=addon)
            root.wait()
            if len(root.list.value) == 1:
                value=root.list.value[0].split(".")
                return value[0], (value[1] if len(value)==2 else self.addon.loaded_addon_info[value[0]]["filetypes"][0])
            else:
                return
        if file is None:
            file=self.ui.Dialog.askfile()
            if not os.path.exists(file):
                return
        ext=os.path.splitext(file)[1].lstrip(".")
        if force_select:
            selected=select_addon(self.addon.extdict, recom=(self.addon.extdict[ext] if ext in self.addon.extdict else None))
            if selected is None:
                return
            addon, ext = selected
        else:
            if ext in self.addon.extdict:
                addon=self.addon.extdict[ext][0]
            else:
                if as_diff_type:
                    selected=select_addon(self.addon.extdict)
                    if selected is None:
                        return
                    addon, ext = selected
                else:
                    self.ui.Dialog.error(title="Error", message="Can't find valid addon.")
                    return
        label=f'{os.path.basename(file)} {f"[{ext}]" if os.path.splitext(file)[1]!="."+ext else ""}'
        tab=self.ui.notebook.add_tab(label=label)
        ctx=self.addon.getAddon(addon, file, ext, tab, self)
        self.opening[label]=ctx
        self.ui.notebook.select_tab("end")
        ctx.saved=False
    def save(self, as_other=False):
        if not self.ui.notebook.value in self.opening:
            return
        if as_other:
            file=self.ui.Dialog.askfile()
            if not os.path.exists(file):
                return
            self.opening[self.ui.notebook.value].addon.save(file)
        else:
            self.opening[self.ui.notebook.value].addon.save()
    def new(self, **options):
        def dialog():
            def close():
                buttons.next.release()
                root.close()
            root=self.ui.makeSubWindow(dialog=True)
            root.setcallback("close", close)
            body=root.Frame()
            body.pack()
            body.title=body.Label(text="You can make new files using this dialog.")
            body.title.pack()
            buttons=root.Frame()
            buttons.pack(side="bottom", expand=True)
            buttons.cancel=buttons.Input.Button(label="Cancel", command=close)
            buttons.cancel.pack()
            buttons.next=buttons.Input.Button(label="Next")
            buttons.next.pack()
            options={"file":None, "filetype":None}
            buttons.next.wait()
            if not body.exist():
                return options
            while 1:
                for i in options:
                    if options[i] is None:
                        break
                else:
                    break
                if i == "file":
                    body.title.configure(text="Please set file path.")
                    body.file=body.Input.Form(type="filesave")
                    body.file.pack(fill="both", expand=True)
                elif i == "filetype":
                    body.title.configure(text="Please set file type.")
                    body.filetype=body.Input.List()
                    body.filetype.pack(fill="both", expand=True)
                    for ext, addons in self.addon.extdict.items():
                        for addon in addons:
                            if not body.filetype.exist_item(addon):
                                body.filetype.add_item(label=addon, id=addon)
                            body.filetype.add_item(label=ext, id=addon+"."+ext, parent=addon)
                buttons.next.wait()
                if not body.exist():
                    break
                if i == "file":
                    if body.file.value != "":
                        options["file"]=body.file.value
                    body.file.destroy()
                elif i == "filetype":
                    if len(body.filetype.value) == 1:
                        filetype=body.filetype.value[0].split(".")
                        options["filetype"]=filetype
                        options["addon"]=filetype[0]
                        if len(filetype) == 1:
                            options["ext"]=self.addon.loaded_addon_info[addon]["filetypes"][0]
                        else:
                            options["ext"]=filetype[1]
                    body.filetype.destroy()
            root.close()
            return options
        if not "file" in options or not "filetype" in options:
            options=dialog()
        if None in options.items():
            return
        file=options["file"]
        addon=options["addon"]
        ext=options["ext"]
        if getattr(self.addon.loaded_addon[addon], "append_ext", True):
            file+="."+ext
        label=f'{os.path.basename(file)} {f"[{ext}]" if os.path.splitext(file)[1]!="."+ext else ""}'
        tab=self.ui.notebook.add_tab(label=label)
        ctx=self.addon.getAddon(addon, file, ext, tab, self)
        self.opening[label]=ctx
        ctx.saved=False
        ctx.addon.new()
        self.ui.notebook.select_tab("end")
    def close(self, value=None, question=-1):
        if value is None:
            value=self.ui.notebook.value
        if not value in self.opening:
            self.ui.notebook.del_tab("current")
            return
        if not self.opening[value].saved:
            if question == -1:
                question=self.ui.Dialog.question("yesnocancel", "Save...?", f"Do you want to save?\nFile:{value}")
            if question == True:
                self.save()
            elif question != False:
                return
        self.opening[value].addon.close()
        self.opening.pop(value)
        self.ui.notebook.del_tab("current")
    def exit(self):
        try:
            for i in self.opening:
                if not self.opening[i].saved:
                    question=self.ui.Dialog.question("yesnocancel", "Save...?", f"Do you want to save?\nFile:{i}")
                    if question is None:
                        break
                else:
                    question=None
                self.close(i, question)
            else:
                self.ui.close()
        except RuntimeError:
            self.exit()
    def update_state(self, addon):
        index=self.ui.notebook.value
        if not index in self.opening:
            return
        before=self.opening[index]
        old_index=index
        if addon.saved and "*" in index:
            self.opening.pop(index)
            index=index.lstrip("*")
            self.ui.notebook.config_tab(old_index, text=index)
            self.opening[index]=before
        elif not addon.saved and not "*" in index:
            self.opening.pop(index)
            index="*"+index
            self.ui.notebook.config_tab(old_index, text=index)
            self.opening[index]=before
        self.ui.notebook.callback()
    def version(self):
        root=self.ui.makeSubWindow(dialog=True)
        root.changeTitle(self.appinfo["appname"]+" - Version and License")
        root.note=root.Notebook()
        root.note.pack(fill="both", expand=True)
        version=root.note.add_tab(label="Version")
        version.title=version.Label(image="init.png")
        version.title.pack()
        version.text=version.Label(text=f"{__version__} {__revision__} -2023 Marusoftware")
        version.text.pack()
        licence=root.note.add_tab(label="Licence")
        licence.text=licence.Input.Text(scroll=True, readonly=True)
        licence.text.pack(fill="both", expand=True)
        with open(os.path.join(self.appinfo["cd"], "LICENCE")) as f:
            licence.text.insert("end", f.read())
"""
# setting
def setting():
    def done():
        conf.update(theme=s.style.get())
        conf.update(open_other=s_v1.get())
        if conf["lang"] != s.lang.get():
            tkmsg.showinfo("Info","Language Changing will apply when you start Marueditor next time.", parent=s)
            conf.update(lang=s.lang.get())
        config.setConfig(conf)
        #pickle.dump(conf, open(conf_path, "wb"))
        s.destroy()
    def cancel():
        root.style.theme_use(conf["theme"])
        s.destroy()
    def change(gomi, argv):
        if argv == "style":
            root.style.theme_use(s.style.get())
        elif argv == "lang":
            pass
    s = tkinter.Toplevel()
    s.title(txt["setting"])
    s.note = ttk.Notebook(s)
    s.note.pack(fill="both",expand=True)
    s.frames = {}
    s.frames.update(Main=ttk.Frame(s.note))
    s.note.add(s.frames["Main"],text="Main")
    s.frames["Main"].note = ttk.Notebook(s.frames["Main"])
    s.frames["Main"].note.pack(fill="both",expand=True)
    Main = {"Appearance" : "", "File" : "", "Addons" : ""}
    for i in Main.keys():
        Main[i] = (ttk.Frame(s.frames["Main"].note))
        s.frames["Main"].note.add(Main[i], text=i)
    s_b1 = ttk.Button(s, text=txt["done"], command=done)
    s_b2 = ttk.Button(s, text=txt["cancel"], command=cancel)
    if "open_other" in conf:
        s_v1 = tkinter.IntVar(Main["File"], value=conf["open_other"])
    else:
        s_v1 = tkinter.IntVar(Main["File"], value=0)
    if "en_dnd" in conf:
        s_v2 = tkinter.IntVar(Main["File"], value=conf["en_dnd"])
    else:
        s_v2 = tkinter.IntVar(Main["File"], value=0)
    s_c1 = ttk.Checkbutton(Main["File"], text=txt["st_open_from"], variable=s_v1)
    s_c1.pack(side="top",fill="x")
    s_c2 = ttk.Checkbutton(Main["File"], text=txt["st_dnd"], variable=s_v2)
    s_c2.pack(side="top",fill="x")
    s_b1.pack(side="left",fill="both",expand=True)
    s_b2.pack(side="left",fill="both",expand=True)
    def remove():
        try:
            addons.remove(addons.get_file()[s.a_fl.curselection()[0]-1])
            s.a_fl.delete(s.a_fl.curselection()[0]-1)
        except:
            pass
        os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
    s.style = ttk.Combobox(Main["Appearance"], width=30, value=root.style.theme_names())
    s.style.pack()
    s.lang = ttk.Combobox(Main["Appearance"], width=30, value=list(map(lambda value: value.replace(".lang",""), list(filter(lambda value: ".lang" in value, os.listdir(cd+"/language"))))))
    s.lang.pack()
    s.a_fl = tkinter.Listbox(Main["Addons"], width=30)
    s.a_fl.pack()
    s.a_fl.insert("end",txt["file_addon"]+":")
    s.a_b1 = ttk.Button(Main["Addons"], text=txt["delete"], command=remove)
    s.a_b1.pack()
    s.style.insert("end",root.style.theme_use())
    s.lang.insert("end",conf["lang"])
    s.style.bind('<<ComboboxSelected>>', lambda null: change(gomi=null, argv="style"))
    s.lang.bind('<<ComboboxSelected>>', lambda null: change(gomi=null, argv="lang"))
    s.style.bind('<Return>', lambda null: change(gomi=null, argv="style"))
    s.lang.bind('<Return>', lambda null: change(gomi=null, argv="lang"))
    for i in range(len(file_addons)):
        s.a_fl.insert("end", "  " + file_addon_list[i] + "(" + file_addon_type[i] + " " +file_addon_type_ex[i] + ")")
#help
class hlp():
    #show help
    def help():
        pass
    def update():
        pass """

def run(argv=DefaultArgv):
    app=Editor(argv)
    app.Setup()
    app.CreateMenu()
    app.welcome()
    if not argv.filepath is None:
        app.open(file=argv.filepath, as_diff_type=True)
    app.mainloop()

if __name__ == "__main__":
    """INIT"""
    #argvParse
    argv_parser = argparse.ArgumentParser("marueditor", description="Marueditor. The best editor.")
    argv_parser.add_argument("--shell", dest="shell", help="Start in shell mode.", action="store_true")
    argv_parser.add_argument("--debug", dest="debug", help="Start in debug mode.", action="store_true")
    argv_parser.add_argument("-log_level", action="store", type=int, dest="log_level", default=0 ,help="set Log level.(0-50)")
    argv_parser.add_argument("filepath", action="store", type=str, default=None ,help="Open file path.", nargs='?')
    argv = argv_parser.parse_args()
    run(argv)