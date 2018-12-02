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
CRAFTABLE_ITEMS = {
    "Keg": 0,
    "Bee House": 0,
    "Scarecrow": 0,
    "Torch": 0,
    "Chest": 0,
    "Gate": 0,
    "Hardwood Fence": 0,
    "Iron Fence": 0,
    "Stone Fence": 0,
    "Wood Fence": 0,
    "Cask": 0,
    "Furnace": 0,
    "Cheese Press": 0,
    "Mayonnaise Machine": 0,
    "Seed Maker": 0,
    "Loom": 0,
    "Oil Maker": 0,
    "Recycling Machine": 0,
    "Worm Bin": 0,
    "Preserves Jar": 0,
    "Charcoal Kiln": 0,
    "Tapper": 0,
    "Lightning Rod": 0,
    "Slime Incubator": 0,
    "Slime Egg-Press": 0,
    "Crystalarium": 0,
    "Sprinkler": 0,
    "Quality Sprinkler": 0,
    "Iridium Sprinkler": 0,
    "Staircase": 0,
    "Flute Block": 0,
    "Drum Block": 0,
    "Basic Fertilizer": 0,
    "Quality Fertilizer": 0,
    "Basic Retaining Soil": 0,
    "Quality Retaining Soil": 0,
    "Speed-Gro": 0,
    "Deluxe Speed-Gro": 0,
    "Cherry Bomb": 0,
    "Bomb": 0,
    "Mega Bomb": 0,
    "Explosive Ammo": 0,
    "Transmute (Fe)": 0,
    "Transmute (Au)": 0,
    "Ancient Seeds": 0,
    "Wild Seeds (Sp)": 0,
    "Wild Seeds (Su)": 0,
    "Wild Seeds (Fa)": 0,
    "Wild Seeds (Wi)": 0,
    "Warp Totem: Farm": 0,
    "Warp Totem: Mountains": 0,
    "Warp Totem: Beach": 0,
    "Rain Totem": 0,
    "Field Snack": 0,
    "Crystal Floor": 0,
    "Wood Path": 0,
    "Gravel Path": 0,
    "Cobblestone Path": 0,
    "Wild Bait": 0,
    "Bait": 0,
    "Spinner": 0,
    "Magnet": 0,
    "Trap Bobber": 0,
    "Cork Bobber": 0,
    "Dressed Spinner": 0,
    "Treasure Hunter": 0,
    "Barbed Hook": 0,
    "Oil Of Garlic": 0,
    "Life Elixir": 0,
    "Crab Pot": 0,
    "Iridium Band": 0,
    "Ring of Yoba": 0,
    "Sturdy Ring": 0,
    "Warrior Ring": 0,
    "Wicked Statue": 0,
    "Campfire": 0,
    "Wood Sign": 0,
    "Stone Sign": 0,
    "Garden Pot": 0,
    "Weathered Floor": 0,
    "Wooden Brazier": 0,
    "Wood Lamp-post": 0,
    "Iron Lamp-post": 0,
    "Wood Floor": 0,
    "Stone Floor": 0,
    "Stepping Stone Path": 0,
    "Straw Floor": 0,
    "Crystal Path": 0,
    "Stone Brazier": 0,
    "Barrel Brazier": 0,
    "Stump Brazier": 0,
    "Gold Brazier": 0,
    "Carved Brazier": 0,
    "Skull Brazier": 0,
    "Marble Brazier": 0,
    "Tub o' Flowers": 0,
    "Jack-O-Lantern": 0
}


class CraftingChecker:
    """
    A class for checking which items need to be crafted for the
    "Craft Master" achievement in Stardew Valley. An unedited save file is
    required (no reformatting - all data on one line).
    Stardew Valley version: 1.3.32
    """

    def __init__(self, save_files_directory, save_file_name,
                 checker_type="crafting"):
        self.checker_type = checker_type
        file = self.__load_save_file("{}\\{}\\{}".format(
            save_files_directory, save_file_name, save_file_name))
        self.crafting_recipes = self.__get_recipes(checker_type, file)

    def get_unlearned_recipes(self):
        return set(CRAFTABLE_ITEMS.keys()).difference(set(
            self.crafting_recipes.keys()))

    def get_uncrafted_items(self):
        uncrafted_items = list(self.get_unlearned_recipes())

        for k, v in self.crafting_recipes.items():
            if v == 0:
                uncrafted_items.append(k)

        return uncrafted_items

    def get_crafted_items(self):
        crafted_items = []

        for k, v in self.crafting_recipes.items():
            if v > 0:
                crafted_items.append(k)

        return crafted_items

    def get_learned_recipes(self):
        """

        :return:
        """
        return list(self.crafting_recipes.keys())

    def __load_save_file(self, save_file_name):
        """

        :param save_file_name:
        :return:
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
               "There are {} total items\n" \
               "{} have been crafted\n" \
               "{} have not been crafted (including unlearned)\n" \
               "{} recipes have not been learned\n" \
               "{:-^30}".format(
            "",
            len(CRAFTABLE_ITEMS.keys()),
            len(self.get_crafted_items()),
            len(self.get_uncrafted_items()),
            len(self.get_unlearned_recipes()),
            ""
        )
