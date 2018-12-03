import re

# Generic recipe format - no whitespace:
# <{}Recipes>
# <item>
#   <key>
#       <string>name</string>
#   </key>
#   <value>
#       <int>value</int>
#   </value>
# </item>
# </{}Recipes>
SEARCH_TAGS = ["<{}Recipes>", "</{}Recipes>"]
SEARCH_STRING = "{}[\w\W]*{}"
LEADING_NAME_TAG_LENGTH = len("<item><key><string>")
TRAILING_NAME_TAG_LENGTH = len("</string></key><value><int>")
TRAILING_VALUE_TAG_LENGTH = len("</int></value></item>")
CRAFTABLE_ITEMS = ('Ancient Seeds', 'Bait', 'Barbed Hook', 'Barrel Brazier',
                   'Basic Fertilizer', 'Basic Retaining Soil', 'Bee House',
                   'Bomb', 'Campfire', 'Carved Brazier', 'Cask',
                   'Charcoal Kiln', 'Cheese Press', 'Cherry Bomb', 'Chest',
                   'Cobblestone Path', 'Cork Bobber', 'Crab Pot',
                   'Crystal Floor', 'Crystal Path', 'Crystalarium',
                   'Deluxe Speed-Gro', 'Dressed Spinner', 'Drum Block',
                   'Explosive Ammo', 'Field Snack', 'Flute Block', 'Furnace',
                   'Garden Pot', 'Gate', 'Gold Brazier', 'Gravel Path',
                   'Hardwood Fence', 'Iridium Band', 'Iridium Sprinkler',
                   'Iron Fence', 'Iron Lamp-post', 'Jack-O-Lantern', 'Keg',
                   'Life Elixir', 'Lightning Rod', 'Loom', 'Magnet',
                   'Marble Brazier', 'Mayonnaise Machine', 'Mega Bomb',
                   'Oil Maker', 'Oil Of Garlic', 'Preserves Jar',
                   'Quality Fertilizer', 'Quality Retaining Soil',
                   'Quality Sprinkler', 'Rain Totem', 'Recycling Machine',
                   'Ring of Yoba', 'Scarecrow', 'Seed Maker', 'Skull Brazier',
                   'Slime Egg-Press', 'Slime Incubator', 'Speed-Gro',
                   'Spinner', 'Sprinkler', 'Staircase', 'Stepping Stone Path',
                   'Stone Brazier', 'Stone Fence', 'Stone Floor', 'Stone Sign',
                   'Straw Floor', 'Stump Brazier', 'Sturdy Ring', 'Tapper',
                   'Torch', 'Transmute (Au)', 'Transmute (Fe)', 'Trap Bobber',
                   'Treasure Hunter', "Tub o' Flowers", 'Warp Totem: Beach',
                   'Warp Totem: Farm', 'Warp Totem: Mountains', 'Warrior Ring',
                   'Weathered Floor', 'Wicked Statue', 'Wild Bait',
                   'Wild Seeds (Fa)', 'Wild Seeds (Sp)', 'Wild Seeds (Su)',
                   'Wild Seeds (Wi)', 'Wood Fence', 'Wood Floor',
                   'Wood Lamp-post', 'Wood Path', 'Wood Sign',
                   'Wooden Brazier', 'Worm Bin')


class CraftingChecker:
    """
    A class for checking which items need to be crafted for the
    "Craft Master" achievement in Stardew Valley. An unedited save file is
    required (no reformatting - all data on one line).
    Stardew Valley version: 1.3.32
    """

    def __init__(self, save_files_directory, save_file_name,
                 checker_type="crafting"):
        self.save_file_name = save_file_name.split("_")[0]
        self.checker_type = checker_type  # this is dumb
        file = self.__load_save_file("{}\\{}\\{}".format(
            save_files_directory,
            save_file_name,
            save_file_name
        ))
        self.crafting_recipes = self.__get_recipes(checker_type, file)

    def get_unlearned_recipes(self):
        """
        Get recipes that have not been learned
        :return: (string, string, ...) a tuple of unlearned crafting items
        """
        return tuple(set(CRAFTABLE_ITEMS).difference(set(
            self.crafting_recipes.keys())))

    def get_uncrafted_items(self):
        """
        Get items that have not been crafted - including unlearned items
        :return: tuple[string, string, ...] a tuple containing items that
        have not been crafted
        """
        uncrafted_items = list(self.get_unlearned_recipes())

        for k, v in self.crafting_recipes.items():
            if v == 0:
                uncrafted_items.append(k)

        return tuple(uncrafted_items)

    def print_uncrafted_items(self):
        """
        Print a list of items that have not been crafted - including items
        that have not been learned
        """
        uncrafted_items = sorted(self.get_uncrafted_items())
        count = 0

        for i in uncrafted_items:
            count += 1
            print("{}. {}".format(count, i))

    def get_crafted_items(self):
        """
        Get items that have been crafted.
        :return: tuple[string, string, ...] a tuple containing items that have
        been crafted
        """
        crafted_items = []

        for k, v in self.crafting_recipes.items():
            if v > 0:
                crafted_items.append(k)

        return tuple(crafted_items)

    def get_learned_recipes(self):
        """
        Get crafting recipes that have been learned
        :return: tuple(string, string, ...) a tuple containing all crafting
        recipes that have been learned
        """
        return tuple(self.crafting_recipes.keys())

    def __load_save_file(self, save_file_name):
        """ Loads the save file.
        :param save_file_name: the absolute path to the file and file name
        :return: string: contents of the save file
        """
        file = open(save_file_name, "r")
        line = file.readline()
        file.close()

        return line

    def __get_recipes(self, recipe_type, file):
        """Get recipe data from within file.
        A generic function that can accept any valid recipe_type in the game (
        e.g. crafting, cooking), and will return a string containing the tags
        related to those recipes.

        :param recipe_type:
        :param file: the xml that has been read from the save file
        :return: a dictionary containing {item: amount_crafted} - this
        dictionary will not contain unlearned recipes
        """
        tags = (
            SEARCH_TAGS[0].format(recipe_type),
            SEARCH_TAGS[1].format(recipe_type)
        )
        search = re.search(SEARCH_STRING.format(tags[0], tags[1]), file)
        recipe_search = file[search.span()[0] + len(tags[0]): search.span()[1]
                                                              - len(tags[1])]
        recipes = dict()
        scan_counter = 0

        while scan_counter < len(recipe_search):
            # skip the first set of tags
            scan_counter = scan_counter + LEADING_NAME_TAG_LENGTH

            # name
            name = recipe_search[scan_counter: recipe_search.index("<",
                                                                   scan_counter)]
            # find the index of the < at the end of the name as names are
            # variable length
            scan_counter = recipe_search.index("<", scan_counter)

            # skip closing name and opening value tags
            scan_counter = scan_counter + TRAILING_NAME_TAG_LENGTH
            # the value is >= 0 and has len >= 0, find the index of the
            value = recipe_search[
                    scan_counter: recipe_search.index("<",
                                                      scan_counter)]
            # closing tag immediately following the value
            scan_counter = recipe_search.index("<", scan_counter)
            # add the length of the trailing closing tags to the counter
            scan_counter = scan_counter + TRAILING_VALUE_TAG_LENGTH

            # if value is "0", the item has not be crafted
            recipes[name] = int(value)

        return recipes

    def __repr__(self):
        return "{:-^30}\n" \
               "Save file: {}\n" \
               "There are {} total items\n" \
               "{} have been crafted\n" \
               "{} have not been crafted (including unlearned)\n" \
               "{} recipes have not been learned\n" \
               "{:-^30}".format(
            "",
            self.save_file_name,
            len(CRAFTABLE_ITEMS),
            len(self.get_crafted_items()),
            len(self.get_uncrafted_items()),
            len(self.get_unlearned_recipes()),
            "")
