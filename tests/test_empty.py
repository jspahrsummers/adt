from adt.decorator import adt


# We won't be able to use or do anything with this class, but it shouldn't
# choke the typechecker plugin, as this is how you would start defining a new
# ADT.
@adt
class Empty:
    pass
