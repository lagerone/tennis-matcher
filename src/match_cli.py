from matching.games import StableRoommates


def main():
    player_prefs = {
        'a': ['b', 'c', 'd'],
        'b': ['a', 'c', 'd'],
        'c': ['a', 'b', 'd'],
        'd': ['a', 'b', 'c'],
    }
    game = StableRoommates.create_from_dictionary(player_prefs=player_prefs)
    result = game.solve()
    print(result)


if __name__ == "__main__":
    main()
