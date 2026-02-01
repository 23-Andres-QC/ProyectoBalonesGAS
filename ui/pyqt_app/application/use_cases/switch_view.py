class SwitchView:
    def __init__(self):
        self.current_mode = "raw"

    def execute(self, mode: str):
        if mode in ["raw", "processed"]:
            self.current_mode = mode
        return self.current_mode
