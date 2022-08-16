

class Friends:

    def __init__(self):
        self.friends = []

    def add_friend(self, pair):
        if isinstance(pair,set):
            self.friends.append(pair)
        elif isinstance(pair,list):
            self.friends += pair

    def print_friends_of(self, name):
        for pair in self.friends:
            if name in pair:
                x = list(pair)
                x.remove(name)
                print(x[0])


if __name__ == "__main__":
    data = Friends()
    data.add_friend([('Taras','Alex'), ('Alex','Stas'), ('Stas', 'Oleg')])
    data.print_friends_of("Stas")