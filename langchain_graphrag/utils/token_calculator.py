class TokenCalculator(object):
    def __init__(self):
        pass

    def __call__(self, text: str) -> int:
        return len(text.split())
