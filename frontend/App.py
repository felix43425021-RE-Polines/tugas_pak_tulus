from controllers.Routes import Routes
from repositories.BusinessRepositories import RepositoryBase

x = RepositoryBase()

if __name__ == "__main__":
    app = Routes()
    print(x.connected)
    app.mainloop()
