# Alexander Kim, kima4
# CS372 Programming Assignment 4

# there were no outside sources used to write this code

# ascii characters to use for displaying the battleship board
BLANK = '   '
VERT = '║'
HORI = '═══'
HIT = '###'
MISS = ' O '
COL_LABELS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
BOARD_SEP = '     '


# contains the functions and variables needed to play battleship
class Battleship:

    # board dimensions - by default, there are 100 positions on the board
    _width = 10
    _height = 10

    # ship information, name and length
    _ships = [['Carrier', 5], ['Battleship', 4], ['Destroyer', 3], ['Submarine', 3], ['Patrol Boat', 2]]
    # _ships = [['Patrol Boat', 2]]  # for testing

    # messages to display based on user input
    _add_ship_msg = ['The SHIP was successfully added!',
                     'The coordinates must be separated by a colon (:)',
                     'The first coordinate is out of bounds',
                     'The second coordinate is out of bounds',
                     'The coordinates are not aligned properly',
                     'The ship is not the correct length',
                     'The coordinates overlap with an existing ship',
                     'At least one of the coordinates is invalid']

    _add_attk_msg = ['Miss...',
                     'Successful hit!',
                     'You destroyed the opponent\'s SHIP!',
                     'The coordinate is out of bounds',
                     'You have already attacked there',
                     'The coordinate is invalid']

    # defense messages are given only if an attack was performed without error
    _def_msg = ['Your opponent attacked SPACE and missed!',
                'Your opponent hit your SHIP on SPACE!',
                'Your SHIP was destroyed!',
                '',
                '',
                '']

    # initialization
    def __init__(self):

        self._finished = False

        # ships are tracked as arrays, with index 0 containing the ship name and the remaining
        # indices containing the position on the board
        self._p1_ships = []
        # self._p1_ships = [['Carrier', 11, 12, 13, 14, 15], ['Submarine', 45, 46, 47]]
        self._p2_ships = []
        # self._p2_ships = [[46, 47, 48], [75, 76, 77]]

        # the attacks each player have performed are tracked as a list of board positions
        self._p1_attacks = []
        # self._p1_attacks = [3, 6, 48, 77]
        self._p2_attacks = []
        # self._p2_attacks = [2, 4, 45, 77]

        # tracks how many ships each player has left
        # once one reaches 0, the game is over
        self._p1_ships_left = len(self._ships)
        self._p2_ships_left = len(self._ships)

    # gets the list of ship types for game setup
    def get_ship_types(self):
        return self._ships

    # true if a player has 0 ships left, false otherwise
    def is_finished(self):
        return self._finished

    # returns a tuple with the number of ships the server player has left and the number of ships
    # the client player has left
    def get_ships_left(self):
        return self._p1_ships_left, self._p2_ships_left

    # returns the array that represents a ship occupying a specified board location, if it exists
    def get_ship_on(self, player, index):
        ship = [s for s in self.player_ships(player) if index in s]
        if ship:
            return ship[0]
        return None

    # gets the list of ships for a specified player
    def player_ships(self, player):
        if player:
            return self._p1_ships
        return self._p2_ships

    # gets the list of attacks carried out by a specified player
    def player_attacks(self, player):
        if player:
            return self._p1_attacks
        return self._p2_attacks

    # to allow for print() to work
    def __str__(self):
        return self.board_to_strings()

    # returns a string representing the gridlines of the board
    # the string contains both the player board and the targeting board
    # ship edges are represented as double horizontal lines
    def print_row_lines(self, row, player):
        printed_row = '   '

        # player board
        for col in range(self._width):
            printed_row += '+'
            ship = self.get_ship_on(player, self.ctoi(col, row))

            # determines if the double horizontal lines should be added based on if it would bisect a ship
            if ship:
                if self.ctoi(col, row - 1) in ship:
                    printed_row += BLANK
                else:
                    printed_row += HORI

            # checks to see if there is a ship in the preceding row that needs a border added
            elif row != 0:
                ship = self.get_ship_on(player, self.ctoi(col, row - 1))
                if ship:
                    printed_row += HORI
                else:
                    printed_row += BLANK
            else:
                printed_row += BLANK
        printed_row += '+'

        printed_row += BOARD_SEP + BLANK + '   '

        # targeting board
        for col in range(self._width):
            printed_row += '+   '
        printed_row += '+'

        return printed_row

    # returns a string representing the spaces of the board
    # the string contains both the player board and targeting board
    # ship edges, successful attacks, and missed shots have their own special representation
    def print_col_lines(self, row, player):

        # print row numbers
        printed_col = '\n{0:>2} '.format(row + 1)

        # player board - largely the same logic as print_row_lines()
        for col in range(self._width + 1):
            ship = self.get_ship_on(player, self.ctoi(col, row))
            if ship:
                if self.ctoi(col - 1, row) in ship:
                    printed_col += ' '
                else:
                    printed_col += VERT
                if self.ctoi(col, row) in self.player_attacks(not player):
                    printed_col += HIT
                else:
                    printed_col += BLANK

            elif col != 0:
                ship = self.get_ship_on(player, self.ctoi(col - 1, row))
                if ship:
                    printed_col += VERT + BLANK
                else:
                    printed_col += ' ' + BLANK
            else:
                printed_col += ' ' + BLANK

        # targeting board - prints hit icons and miss icons as well
        printed_col += BOARD_SEP
        printed_col += '{0:>2} '.format(row + 1)
        for col in range(self._width):
            printed_col += ' '
            if self.ctoi(col, row) in self.player_attacks(player):
                ship = self.get_ship_on(not player, self.ctoi(col, row))

                if ship:
                    printed_col += HIT
                else:
                    printed_col += MISS
            else:
                printed_col += BLANK
        printed_col += '\n'
        return printed_col

    # converts an entire battleship object into a string for printing
    def board_to_strings(self, player=True):
        printed_board = '   '

        # adding number headings
        for col in range(self._width):
            printed_board += '  ' + COL_LABELS[col] + ' '
        printed_board += BOARD_SEP + BLANK + '    '
        for col in range(self._width):
            printed_board += '  ' + COL_LABELS[col] + ' '
        printed_board += '\n'

        # adding the actual board
        for row in range(self._height + 1):
            printed_board += self.print_row_lines(row, player)

            if row < self._height:
                printed_board += self.print_col_lines(row, player)

        # adding board labels
        printed_board += '\n                  YOUR BOARD      '\
                         + BOARD_SEP + '                             TARGETING BOARD\n'

        return printed_board

    # determines if coordinate values are inside the permitted bounds
    def in_bounds(self, col, row):
        if col < 0:
            return False
        if row < 0:
            return False
        if col >= self._width:
            return False
        if row >= self._height:
            return False
        return True

    # converts a space (e.g. A3) to an index (e.g. 2)
    def stoi(self, space):
        col, row = self.stoc(space)
        if not self.in_bounds(col, row):
            return -1
        return self.ctoi(col, row)

    # converts a space (e.g. A3) to coordinates (e.g. (2, 0))
    def stoc(self, space):
        space = space.upper()
        col = COL_LABELS.find(space[0])
        row = int(space[1:]) - 1
        return col, row

    # converts coordinates (e.g. (2, 0)) to an index (e.g. 2)
    def ctoi(self, col, row):
        index = row * self._width + col
        return index

    # adds a specified ship to a specified player's board
    def add_ship(self, player, name, length, spaces):
        ship = [name]

        # parses the spaces to determine if the location is valid
        spaces = spaces.split(':')
        if len(spaces) < 2:
            return 1  # if there aren't two spaces in the input
        front = spaces[0]
        back = spaces[1]

        try:
            f_col, f_row = self.stoc(front)
            b_col, b_row = self.stoc(back)
        except:
            return 7  # if the spaces are not in a valid format

        if not self.in_bounds(f_col, f_row):
            return 2  # if the first space is out of bounds
        if not self.in_bounds(b_col, b_row):
            return 3  # if the second space is out of bounds
        if f_col != b_col and f_row != b_row:
            return 4  # if the alignment of the spaces is not valid
        else:
            # getting all the spaces between the specified spaces
            if f_col == b_col:
                for r in range(min(f_row, b_row), max(f_row, b_row) + 1):
                    ship.append(self.ctoi(f_col, r))
            else:
                for c in range(min(f_col, b_col), max(f_col, b_col) + 1):
                    ship.append(self.ctoi(c, f_row))

        if len(ship) != length + 1:
            return 5  # if the ship length is different from specified

        for c in ship:
            other_ships = self.get_ship_on(player, c)
            if other_ships:
                return 6  # if the ship would overlap with another ship

        if player:
            self._p1_ships.append(ship)
        else:
            self._p2_ships.append(ship)

        return 0  # if a ship is successfully placed

    # returns a message based on the success or lack thereof in placing a ship on the board
    def ship_messages(self, ship_name, status):
        message = self._add_ship_msg[status]
        if status == 0:
            message = message.replace('SHIP', ship_name)
        return message

    # true if the specified player was hit on the specified index, false otherwise
    def is_hit(self, player, index):
        ship = self.get_ship_on(player, index)
        if ship:
            return True
        return False

    # true if the specified player's specified ship was destroyed
    def is_destroyed(self, player, ship):
        for s in ship[1:]:
            if s not in self.player_attacks(not player):
                return False

        # decrement the number of ships the player has
        if player:
            self._p1_ships_left -= 1
        else:
            self._p2_ships_left -= 1

        # check to see if the game is over
        if self._p1_ships_left == 0 or self._p2_ships_left == 0:
            self._finished = True

        return True

    # adds an attack on the specified space for the specified player
    def add_attack(self, player, space):
        try:
            index = self.stoi(space)
        except:
            return 5  # if the specified space is in an invalid format

        if index < 0:
            return 3  # if the specified space is out of bounds
        if index in self.player_attacks(player):
            return 4  # if the player has already attacked the specified space

        if player:
            self._p1_attacks.append(index)
        else:
            self._p2_attacks.append(index)

        if self.is_hit(not player, index):
            # check to see if the ship is destroyed or just hit
            ship = self.get_ship_on(not player, index)
            if self.is_destroyed(not player, ship):
                return 2  # if a ship is hit and destroyed
            return 1  # if a ship is hit but not destroyed
        else:
            return 0  # if the attack missed

    # returns a message based on the success or lack thereof in attacking
    def attack_messages(self, player, space, status):

        atk_msg = self._add_attk_msg[status]
        def_msg = self._def_msg[status]

        # if a ship was destroyed, prepend the hit message as well
        if status == 2:
            atk_msg = self._add_attk_msg[status - 1] + ' ' + atk_msg
            def_msg = self._def_msg[status - 1] + ' ' + def_msg

        ship_name = ''

        # only try to get ship name if an attack occurred
        if status < 3:
            ship = self.get_ship_on(not player, self.stoi(space))
            if ship:
                ship_name = ship[0]

        atk_msg = atk_msg.replace('SHIP', ship_name)
        def_msg = def_msg.replace('SHIP', ship_name).replace('SPACE', space)

        return atk_msg, def_msg

    # perform a turn of the game and return the results of the turn
    def turn(self, player, space):
        atk_result = ''
        def_result = ''

        status = self.add_attack(player, space)

        # the result includes a print of the new board as well as the status of the attack
        atk_result += self.board_to_strings(player)
        atk_msg, def_msg = self.attack_messages(player, space, status)

        atk_result += atk_msg

        if def_msg != '':
            def_result += self.board_to_strings(not player)
            def_result += def_msg

        return atk_result, def_result


# used for testing
def main():
    b = Battleship()
    print(b)
    print(b.add_ship(True, 'Battleship', 4, 'J4:J1'))
    print(b.add_attack(False, 'J2'))
    print(b.add_attack(False, 'I2'))
    print(b)


if __name__ == '__main__':
    main()