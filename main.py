"""<<main>> entry point from the report class diagram."""
from health_monitor.injector import AppInjector


class Main:
    def main(self):
        self.injector=AppInjector.get()
        self.main_window=self.injector.create_main_window()
        self.main_window.mainloop()
    run=main


if __name__ == "__main__":
    Main().main()
