import enum


class KeyValueBaseEnum(enum.Enum):
    """Enumeration for items with key and label properties"""

    @property
    def key(self):
        return self.value[0]

    @property
    def label(self):
        return self.value[1]


class FieldTypeEnum(enum.Enum):
    """
    Enumeration for supported DocType Fields
    """

    """
	All forms of plain text character fields for a maximum size of 255
	"""
    DATA = "Data"

    """
	Supports Booleans
	"""
    CHECK = "Check"

    """
	Supports integers
	"""
    INT = "Integer"

    """
	Floating point numbers
	"""
    FLOAT = "Float"

    """
	Shows models records
	"""
    LINK = "Link"

    """
	Small text allowing new lines
	"""
    SMALL_TEXT = "Small Text"

    """
	Long text
	"""
    TEXT = "Text"

    """
	Column break. Adds a column to a view
	"""
    COLUMN_BREAK = "Column Break"

    """
	Section break. Adds a field set
	"""
    SECTION_BREAK = "Section Break"
