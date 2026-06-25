from importlib import import_module


class PresenterFactory:
    def resolve(self, presenter_ref):
        if isinstance(presenter_ref, str):
            module_name, class_name = presenter_ref.rsplit(".", 1)
            module = import_module(module_name)
            return getattr(module, class_name)
        return presenter_ref

    def create(self, presenter_ref, **kwargs):
        presenter_class = self.resolve(presenter_ref)
        if presenter_class is None:
            return None
        return presenter_class(**kwargs)