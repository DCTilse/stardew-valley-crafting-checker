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


class CraftingChecker:
    """
    A class for checking which items need to be crafted for the
    "Craft Master" achievement in Stardew Valley. An unedited save file is
    required (no reformatting - all data on one line).
    Stardew Valley version: 1.3.32
    """

    def __init__(self, checker_type="crafting"):
        self.checker_type = checker_type

    def check_save_file(self, save_file_name):
        """
        A raging dumpster fire.
        :param save_file_name: the name of your save file
        :return: None
        """
        file = self.__load_save_file(save_file_name)
        recipes = self.__get_recipes(self.checker_type, file)

        scan_counter = 0
        remaining_items = 0
        total_items = 0

        print("{:-^30}".format(""))

        # This is a dumpster fire
        while scan_counter < len(recipes):
            # skip the first set of tags
            scan_counter = scan_counter + LEADING_NAME_TAG_LENGTH

            # name
            name = recipes[scan_counter: recipes.index("<", scan_counter)]
            # find the index of the < at the end of the name as names are
            # variable length
            scan_counter = recipes.index("<", scan_counter)

            # skip closing name and opening value tags
            scan_counter = scan_counter + TRAILING_NAME_TAG_LENGTH
            # the value is >= 0 and has len >= 0, find the index of the
            value = recipes[scan_counter: recipes.index("<", scan_counter)]
            # closing tag immediately following the value
            scan_counter = recipes.index("<", scan_counter)
            # add the length of the trailing closing tags to the counter
            scan_counter = scan_counter + TRAILING_VALUE_TAG_LENGTH
            total_items += 1

            # if value is "0", the item has not be crafted
            if value == "0":
                print("{}".format(name))
                remaining_items += 1

        print("{:-^30}".format(""))
        if remaining_items == 0:
            print("You have crafted everything.")
        else:
            print("You have {}/{} ({:.2%}) items remaining in {}.".format(
                remaining_items, total_items, (remaining_items / total_items),
                self.checker_type))

    def __load_save_file(self, save_file_name):
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
        :param file:
        :return:
        """
        tags = (
            SEARCH_TAGS[0].format(recipe_type),
            SEARCH_TAGS[1].format(recipe_type))
        search = re.search(SEARCH_STRING.format(tags[0], tags[1]), file)

        return file[search.span()[0] + len(tags[0]): search.span()[1] - len(
            tags[1])]
