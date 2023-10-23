class TransformationFunction:
    name = "transformation function"
    """
        Base class for transformation function
    """
    @staticmethod
    def transform(x):
        return x

    
class Abbreviation(TransformationFunction):
    name = "Abbreviation"
    """
        Transformation function to abbreviate input string
    """
    @staticmethod
    def transform(x):
        return " ".join((token[0].upper() + '.') for token in str(x).split())

class Prefix(TransformationFunction):
    name = "Prefix"
    """
        Transformation function to take the prefix of the input string
    """
    @staticmethod
    def transform(x):
        return str(x)[:3]
    
class FirstToken(TransformationFunction):
    name = "First Token"
    """
        Transformation function to take the first token of the input string
    """
    @staticmethod
    def transform(x):
        x = str(x)
        return x.split()[0] if len(x.split()) > 0 else ""
    
class LastToken(TransformationFunction):
    name = "Last Token"
    """
        Transformation function to take the last token of the input string
    """
    @staticmethod
    def transform(x):
        x = str(x)
        return x.split()[-1] if len(x.split()) > 0 else ""
    
transformations = [Abbreviation.transform, Prefix.transform, FirstToken.transform, LastToken.transform]
