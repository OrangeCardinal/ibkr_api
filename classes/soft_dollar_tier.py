class SoftDollarTier(object):
    def __init__(self, name = "", val = "", displayName = ""):
        self.name = name
        self.val = val
        self.displayName = displayName

    def __str__(self):
        return "Name: %s, Value: %s, DisplayName: %s" % (self.name, self.val, self.displayName)
