import tkinter


class TextArea(tkinter.Text):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def set_text(self, text): 
        self.delete(1.0, tkinter.END)
        self.insert(tkinter.INSERT, text)


