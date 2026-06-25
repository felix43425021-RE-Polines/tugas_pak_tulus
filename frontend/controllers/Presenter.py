class Presenter:
    def __init__(self, view=None, router=None, model=None):
        self._view = view
        self.router = router
        self.model = model

    @property
    def view_instance(self):
        return self._view

    def attach_view(self, view):
        self._view = view

    def detach_view(self):
        self._view = None

    def set_model(self, model):
        self.model = model

    def view(self, route_name):
        if self.router is None:
            raise RuntimeError("Presenter cannot open a view without a router")
        return self.router.show_page(route_name)

    def navigate(self, route_name):
        return self.view(route_name)

    def present(self, method_name, *args, **kwargs):
        if self._view is None:
            return None

        view_method = getattr(self._view, method_name, None)
        if callable(view_method):
            return view_method(*args, **kwargs)
        return None

    def start(self):
        pass

    def stop(self):
        pass