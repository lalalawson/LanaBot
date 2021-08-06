import random

simple_response = ["mhm..", "ok.. gets..", "ahh...", "o...", "gets...", "wah...", "sry..."]
fourth_response = ["wah.. dunno if this is the right time but.. sometimes i know i don't act right! hopefully we can work through this together!", 
        "ok! now tell the real me @lalalawson! scold me n wake my idea up!", 
        "j a friendly reminder that no matter wtv is going on, i really love you okay my dear!"]

class RantResponse():
    def __init__(self):
        simple = simple_response.copy()
        fourth = fourth_response.copy()
        random.shuffle(simple)
        random.shuffle(fourth)
        self.count = 0
        self.curr_simple = simple
        self.curr_fourth = fourth

    def get_response(self):
        if not self.curr_simple:
            simple = simple_response.copy()
            random.shuffle(simple)
            self.curr_simple = simple
        if not self.curr_fourth:
            fourth = fourth_response.copy()
            random.shuffle(fourth)
            self.curr_fourth = fourth

        if self.count < 4:
            self.count = self.count + 1
            return self.curr_simple.pop()
        elif self.count >= 4:
            self.count = 0
            return self.curr_fourth.pop()