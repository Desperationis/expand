from expand.probes import *
from expand.priviledge import *


class ExpansionCard:
    """
    This class enforces a certain format for ansible files for `expand` as well
    as parse information from them.

    FORMAT:
        # PriviledgeLevel()
        # [ CompatibilityProbe(), ... ]
        # [ InstalledProbe(), ... ]
        # This is the description for this file. It is important that the length of this description doesn't have a newline unless starting a new paragraph, as `expand` wraps this description on changing screen sizes.
        #
        #
        #
        # As long as there are consecutive # characters, you can keep extending the description as long as you want.

    """
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.content = open(file_path, "r", encoding="UTF-8").read()

        # This throws an exception if there's an error
        self.get_probes()

    def get_priviledge_level(self):
        """
        Get the privilege level of a expansion card by parsing the first line.
        If first line isn't a priviledge level, raise an Exception.
        """
        first_line = self.content.split("\n")[0]
        if first_line.startswith("#"):
            # Literally run it as python code
            first_line = first_line[1:].strip()
            result = eval(first_line)

            if not isinstance(result, PriviledgeLevel):
                raise RuntimeError(f"{result} is not a PriviledgeLevel.")

            return result

        raise LookupError(f"Priviledge level not found in {self.file_path}")

    def get_probes(self):
        """
        Given an ansible file, return the list of probes by parsing the second line.
        If the ansible file doesn't have a list, raise Exception.
        """

        second_line = self.content.split("\n")[1]
        if second_line.startswith("#"):
            # Literally run it as python code
            second_line = second_line[1:].strip()
            result = eval(second_line)

            if not isinstance(result, list):
                raise RuntimeError(f"{result} is not a list.")

            return result

        raise LookupError(f"Probes not found in {self.file_path}")

    def get_installed_probes(self):
        """
        Given an ansible file, return the list of installed probes by parsing the third line.
        If the ansible file doesn't have a list on line 3, return an empty list.
        """

        lines = self.content.split("\n")
        if len(lines) < 3:
            return []

        third_line = lines[2]
        if third_line.startswith("#"):
            third_line = third_line[1:].strip()
            # If it looks like a list, eval it
            if third_line.startswith("["):
                result = eval(third_line)
                if isinstance(result, list):
                    return result
        return []

    def get_ansible_description(self, max_length: int) -> list[str]:
        """
        Given the CONTENT (string form) of a ansible file specifically made for
        `expand`, extract its description. This is defined as all the consecutive
        comments after the probe comment.

        E.x. 
        # [probe1(), probe2(), ...]
        # This is the first line.
        # This is the second line.

        Each newline character creates a new line in the output. However, if a line
        is longer than `max_width`, it gets split into many lines that are
        `max_width` long.

        Each lines has all left whitespace removed, and whenever a line gets moved
        to another line, the word is wrapped around.

        If the file does not contain any description, return "N/A"
        """

        lines = self.content.split("\n")
        comments = []
        for line in lines:
            if line.startswith("#"):
                comments.append(line)
            else:
                break
        
        if len(comments) <= 2:
            return ["N/A"]

        # This starts on Line 4 (after privilege, probes, and installed probes)
        # These lines are all descriptions without # or whitespace
        comments = list(map(lambda a: a.lstrip("# \t"), comments[3:]))

        if max_length <= 0:
            return []

        def split_sentence(sentence, index):
            # Find the closest space before the index to split the sentence
            split_index = index
            while split_index > 0 and sentence[split_index] != ' ':
                split_index -= 1

            # If a space was found, split there (dropping the space)
            if split_index > 0:
                return [sentence[:split_index], sentence[split_index+1:]]

            # No space found — hard-split at the index without dropping a character
            return [sentence[:index], sentence[index:]]


        result = []
        for string in comments:
            while len(string) > max_length:
                split = split_sentence(string, max_length)
                result.append(split[0])
                string = split[1]

            result.append(string)

        return result


