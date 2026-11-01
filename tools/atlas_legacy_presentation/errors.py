class ReaderError(Exception):
    """Stable, payload-free diagnostic; paths and literals never enter error text."""
    def __init__(self, code):
        self.code = code
        super().__init__(code)
