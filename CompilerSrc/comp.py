class Token:
    def __init__(self, type_, value):
        self.type_ = type_
        self.value = value
    def __eq__(self, other):
        return (self.type_ == other.type_) and (self.value == other.value)
