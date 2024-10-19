

class ID_creator:

    def __init__(self, current= None):

        if current is None: self.id = -1
        else: self.id = current
        
    def get_id(self):
        self.id += 1
        return self.id
    
    def set_current(self, value):
        self.id = value
    
def format_time(time_in_sec):
    hours, remainder = divmod(time_in_sec, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 0: return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
    elif minutes > 0: return f"{int(minutes)}m {int(seconds)}s"
    else: return f"{int(seconds)}s"