class AppState:
    def __init__(self):
        self.path = None

        self.current_song_list = []
        self.current_index = -1
    
        #self.volume = 50  # 0 to 100
        self.is_muted = False
    
        self.is_paused = False
        self.is_stopped = False

        self.loop = 0  # 0 = no loop, 1 = loop all, 2 = loop one
        self.shuffle = False

    def next_index(self):
        if not self.current_song_list:
            return -1

        if self.shuffle:
            import random
            return random.randint(0, len(self.current_song_list) - 1)

        if self.loop != 0:
            if self.loop != 2:  # not loop one
                next_idx = self.current_index + 1
                if next_idx >= len(self.current_song_list):
                    return 0
                else:
                    return next_idx
            else:
                return self.current_index  # loop one
        else:
            return -1
    
    def reset_all(self):
        self.path = None
        self.current_song_list = []
        self.current_index = -1
        self.is_paused = False
        self.is_stopped = False
        self.loop = 0
        self.shuffle = False