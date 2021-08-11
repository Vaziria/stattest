from typing import List
import pickle
import os

class Persist:
    loc: str
    persist_exclude: List = []

    def loc_not_exist(self):
        pass

    def save_obj(self):
        data = {}
        for key, value in self.__dict__.items():
            if key not in self.persist_exclude:
                data[key] = value

        with open(self.loc, 'w+b') as out:
            pickle.dump(data, out)

    def load_obj(self):
        if not os.path.exists(self.loc):
            self.loc_not_exist()
            return False

        with open(self.loc, 'rb') as out:
            data = pickle.load(out)

        self.__dict__.update(data)

        return True
