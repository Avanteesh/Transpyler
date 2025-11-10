class null:
    def __repr__(self): return "Null"
    def __bool__(self): return False
    def __eq__(self, other): return isinstance(other, null.__class__)
    def __neq__(self, other): return isinstance(other, null.__class__)
    

