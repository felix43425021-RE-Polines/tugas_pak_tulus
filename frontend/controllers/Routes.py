from .Router import Router

class Routes(Router):
    @property
    def app_model(self):
        return "models.TokokitaModel.TokokitaModel"

    @property
    def routes(self):
        return {
            "Login": {
                "view": "view.ViewLogin.ViewLogin",
                "presenter": "controllers.PresenterLogin.PresenterLogin",
            },
            "Home": {
                "view": "view.ViewHome.ViewHome",
                "presenter": "controllers.PresenterHome.PresenterHome",
            },
            "Detail": {
                "view": "view.ViewDetail.ViewDetail",
                "presenter": "controllers.PresenterDetail.PresenterDetail",
            },
            "Cart": {
                "view": "view.ViewCart.ViewCart",
                "presenter": "controllers.PresenterCart.PresenterCart",
            },
            "Profile": {
                "view": "view.ViewProfile.ViewProfile",
                "presenter": "controllers.PresenterProfile.PresenterProfile",
            },
            "Admin": {
                "view": "view.ViewAdmin.ViewAdmin",
                "presenter": "controllers.PresenterAdmin.PresenterAdmin",
            },
        }
