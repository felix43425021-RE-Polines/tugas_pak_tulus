from tkinter import ttk


class BaseView(ttk.Frame):
    def __init__(self, parent, router):
        super().__init__(parent)
        self.router = router
        self.presenter = None

    def attach_presenter(self, presenter):
        self.presenter = presenter

    def open_route(self, route_name):
        self.router.show_page(route_name)

    def set_status(self, message):
        status_label = getattr(self, "status_label", None)
        if status_label is not None:
            status_label.config(text=message)

    def clear_children(self, widget):
        for child in widget.winfo_children():
            child.destroy()

    @staticmethod
    def format_currency(value):
        return f"Rp {value:,.0f}".replace(",", ".")