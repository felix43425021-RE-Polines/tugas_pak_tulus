from tkinter import ttk

from .BaseView import BaseView


class ViewAdmin(BaseView):
    def __init__(self, parent, router):
        super().__init__(parent, router)

        top = ttk.Frame(self, padding=16)
        top.pack(fill="x")
        ttk.Label(top, text="Admin Dashboard", font=("Arial", 18, "bold")).pack(side="left")

        button_box = ttk.Frame(top)
        button_box.pack(side="right")
        ttk.Button(button_box, text="Refresh", command=self.refresh).pack(side="left", padx=(0, 8))
        ttk.Button(button_box, text="Kembali", command=self.back_home).pack(side="left")

        self.notice_label = ttk.Label(self, text="", padding=(16, 0, 16, 8))
        self.notice_label.pack(fill="x")

        body = ttk.Frame(self, padding=(16, 0, 16, 16))
        body.pack(fill="both", expand=True)

        self.notebook = ttk.Notebook(body)
        self.notebook.pack(fill="both", expand=True)

        self.users_text = self._add_tab("Users")
        self.stock_text = self._add_tab("Stock")
        self.roles_text = self._add_tab("Role & Permission")
        self.permissions_text = self._add_tab("Permission")
        self.blacklist_text = self._add_tab("Blacklist")
        self.logs_text = self._add_tab("Logs")

    def _add_tab(self, title):
        frame = ttk.Frame(self.notebook, padding=8)
        self.notebook.add(frame, text=title)

        text = ttk.Treeview(frame)
        text.pack(fill="both", expand=True)

        # Reuse a simple Treeview with single text column for low-overhead rendering.
        text["columns"] = ("line",)
        text.heading("#0", text="#")
        text.heading("line", text="Data")
        text.column("#0", width=70, anchor="center")
        text.column("line", anchor="w", width=900)
        return text

    def set_notice(self, message):
        self.notice_label.config(text=message)

    def _fill_lines(self, tree, lines):
        for item_id in tree.get_children():
            tree.delete(item_id)

        if not lines:
            tree.insert("", "end", text="-", values=("(kosong)",))
            return

        for idx, line in enumerate(lines, start=1):
            tree.insert("", "end", text=str(idx), values=(line,))

    def render_snapshot(self, snapshot):
        db_note = "DB: Connected" if snapshot.get("db_connected") else "DB: Fallback Memory"
        self.set_notice(db_note)

        users_lines = []
        for row in snapshot.get("users", []):
            users_lines.append(f"id={row.get('user_id')} | username={row.get('username')} | role={row.get('roles_id')}")

        stock_lines = []
        for row in snapshot.get("stock", []):
            stock_lines.append(
                f"id={row.get('stock_id')} | name={row.get('stock_name')} | qty={row.get('stock_quantity')} | price={row.get('stock_price')}"
            )

        role_lines = []
        for row in snapshot.get("roles_permissions", []):
            role_lines.append(
                f"role={row.get('roles_id')} ({row.get('roles_description')}) | perm={row.get('permission_id')} ({row.get('permission_description')})"
            )

        permission_lines = []
        for row in snapshot.get("permissions", []):
            permission_lines.append(f"perm={row.get('permission_id')} | {row.get('permission_description')}")

        blacklist_lines = []
        for row in snapshot.get("blacklist", []):
            blacklist_lines.append(
                f"user={row.get('user_id')} ({row.get('username')}) | cause={row.get('cause_id')} | reason={row.get('reason')}"
            )

        log_lines = []
        for row in snapshot.get("logs", []):
            log_lines.append(
                f"log={row.get('log_id')} | user={row.get('user_id')} ({row.get('username')}) | activity={row.get('activity_id')} {row.get('activity_description')}"
            )

        self._fill_lines(self.users_text, users_lines)
        self._fill_lines(self.stock_text, stock_lines)
        self._fill_lines(self.roles_text, role_lines)
        self._fill_lines(self.permissions_text, permission_lines)
        self._fill_lines(self.blacklist_text, blacklist_lines)
        self._fill_lines(self.logs_text, log_lines)

    def refresh(self):
        if self.presenter is not None:
            self.presenter.refresh()

    def back_home(self):
        if self.presenter is not None:
            self.presenter.back_home()
        else:
            self.open_route("Home")
