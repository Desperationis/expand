from expand.probes import *


class ExpansionCard:
    """
    This class enforces a certain format for ansible files for `expand` as well
    as parse information from them.

    FORMAT:
        # PriviledgeLevel()
        # [ CompatibilityProbe(), ... ]
        # This is the description for this file. It is important that the length of this description doesn't have a newline unless starting a new paragraph, as `expand` wraps this description on changing screen sizes.
        #
        #
        #
        # As long as there are consecutive # characters, you can keep extending the description as long as you want. 
        
    """
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.content = open(file_path, "r", encoding="UTF-8").read()

    def get_probes(self):
        """
        Given an ansible file, return the list of probes by parsing the first line.
        If the ansible file doesn't have a list, raise Exception.
        """

        first_line = self.content.split("\n")[0]
        if first_line.startswith("#"):
            # Literally run it as python code
            first_line = first_line[1:].strip()
            result = eval(first_line)

            return result

        raise LookupError(f"Probes not found in {self.file_path}")

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
        
        if len(comments) <= 1:
            return ["N/A"]

        # These lines are all descriptions without # or whitespace
        comments = list(map(lambda a: a.lstrip("# \t"), comments[1:]))

        def split_sentence(sentence, index):
            # Find the closest space before the index to split the sentence
            split_index = index
            while split_index > 0 and sentence[split_index] != ' ':
                split_index -= 1
            
            # If no space is found, split at the index directly
            if split_index == 0:
                split_index = index
            
            # Return the split sentence
            return [sentence[:split_index], sentence[split_index+1:]]


        result = []
        for string in comments:
            while len(string) > max_length:
                split = split_sentence(string, max_length)
                result.append(split[0])
                string = split[1]

            result.append(string)

        return result


