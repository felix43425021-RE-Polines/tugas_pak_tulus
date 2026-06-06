from Router import Router

class Routes(Router):
    @property
    def routes(self):
        return {
            "Home": {
                "view": "ViewHome.ViewHome",
                "presenter": "PresenterHome.PresenterHome",
            },
            "Settings": {
                "view": "ViewSettings.ViewSettings",
                "presenter": "PresenterSettings.PresenterSettings",
            },
            "Profile": {
                "view": "ViewProfile.ViewProfile",
                "presenter": "PresenterProfile.PresenterProfile",
            },
        }