from collections import UserDict
from typing import Any, Iterable, Callable, Mapping, Tuple, Union

# from pathlib import Path
# print('Running' if __name__ == '__main__' else 'Importing', Path(__file__).resolve())

# Only problem that still remains now is that _DotDict__settings is still accessible from the outside.
# But every attempt at fixing this brings me back into the loop of trying to fix __setattribute__ or something.


class DotDictOld():
    """
    Dictionary that enables referencing of items using `<dict>.<key>`.

    It works through implementing items as attributes.
    Traditional dictionary indexing (with []) is still possible.

    Attributes
    ----------
    __settings : dict
        a dictionary containing the settings
    ... : Any
        all dictionary items are saved as attributes

    Methods
    -------
    setting(name: str)
        Retrieve a specific setting
    add_setting(name: str, value: Any)
        Add/update a setting
    as_dict()
        Converts the dotdict to a standard dictionary
    """

    def __init__(self, __data: Iterable = None, __debug: bool = False, **kwargs) -> None:
        """
        Args:
            __data (Iterable, optional): The data that the dotdict will contain. Defaults to None.
            __debug (bool, optional): Enables debug mode if True. Defaults to False.

        Raises:
            TypeError: If the __data argument is of an unprocessable type.
        """
        self.__settings = {}
        self.add_setting('debug', __debug)

        if self.setting('debug'):
            print(f'__data: {__data}, __debug: {__debug}, kwargs: {kwargs}')

        if isinstance(__data, dict):
            if self.setting('debug'):
                print('dict')
            if kwargs:
                # Combine the dictionary with kwargs.
                __data = dict(__data, **kwargs)
            for key in __data:
                value = __data[key]
                if type(value) is dict:
                    value = DotDict(value)
                self.__setattr__(key, value)

        elif isinstance(__data, Iterable):
            if self.setting('debug'):
                print('Iterable')
            self.__init__(dict(__data, **kwargs))

        elif not __data:
            if self.setting('debug'):
                print('None')
            self.__init__(dict(**kwargs))

        else:
            raise TypeError()

    @property
    def __prefix(self):
        # Returns the prefix specific to an object of this class. Haven't found a way to get this automatically.
        return f'_{type(self).__name__}'

    @property
    def settings(self):
        return self.__settings

    def setting(self, name: str) -> Any:
        return self.__settings[name]

    def add_setting(self, name: str, value: Any) -> None:
        self.__settings[name] = value

    def toggle_debug(self) -> None:
        self.__settings['debug'] = not self.setting('debug')

    def __getitem__(self, __name: str):
        try:
            item = self.__getattribute__(__name)
        except AttributeError:
            raise KeyError(__name) from None
            # `from None` is added to suppress the raised AttributeError.
        else:
            return item

    def __setitem__(self, __name: str, __value: Any):
        self.__setattr__(__name, __value)

    def as_dict(self) -> dict:
        d = dict(self.__dict__)  # dict(dict) creates a copy.
        d.pop(self.__prefix + '__settings')
        return d

    def __repr__(self) -> str:
        # Using a dot in front of the opening bracket to indicate that it is a dotdict.
        # Removed the representation of the setting dict, since displaying nested DotDicts also calls repr,
        # which would turn into weird displaying. You can still view the settings via the settings property.
        return f'·{self.as_dict()}'

    # https://stackoverflow.com/questions/35282222/in-python-how-do-i-cast-a-class-object-to-a-dict
    # Behavior here differs from a normal dictionary. Returns key-value pairs instead of only keys.
    # This because otherwise `dict(<dotdict>)` would not work.
    def __iter__(self):
        # return (item for item in self.as_dict().items())
        yield (self.as_dict().items())
        # Still not working correctly I think


# Now trying: Mapping (or at least the `SupportsKeysAndGetItem` class)
# No, better: UserDict! https://realpython.com/inherit-python-dict/
# Will do this in a new class for testing.

class DotDict(UserDict):
    """
    Dictionary that enables referencing of items using `<dict>.<key>`.

    Built on top of collections.UserDict.
    Traditional dictionary indexing (with []) is still possible.

    Properties
    ----------
    debug : bool
        Flag that controls the operating mode. `False` for normal operation, `True` for debugging mode.

    Methods
    -------
    update(__m : Mapping | Iterable[tuple], **kwargs : Any)
        Inserts the items in __m into the dictionary.
    toggle_debug()
        Toggles debug mode.
    as_dict()
        Converts the dotdict to a standard dictionary.
    """

    def __init__(self, data=None, /, debug: bool = False, **kwargs) -> None:
        """_summary_

        Args:
            data (_type_, optional): _description_. Defaults to None.
            debug (bool, optional): _description_. Defaults to False.
        """
        self.data = {}
        if data is not None:
            self.update(data)
        if kwargs:
            self.update(kwargs)

        self.__debug = debug
        # Setting attributes like this puts them outside the data dict.
        # For now, creating non-public attributes (starting with one underscore) is not possible.

    def update(self, __m: Union[Mapping, Iterable[tuple]] = None, /, **kwargs: Any) -> None:
        # Inserts the specified items to the dictionary.
        if __m is not None:  # `is not None` because `if 0` would return False.
            if isinstance(__m, Mapping):  # First ABC that implements both `keys` and `__getitem__`
                vals = [__m[i] for i in __m.keys()]
                iter = zip(__m.keys(), vals)
            elif isinstance(__m, Iterable):
                iter = __m
            else:
                raise TypeError('Inappropriate argument type.')

            for key, val in iter:
                if type(val) in [dict, UserDict]:
                    val = DotDict(val)
                self.__setattr__(key, val)

        for key in kwargs:
            self.key = kwargs[key]

    @property
    def debug(self):
        return self.__debug

    @debug.setter
    def debug(self, x: bool, /):
        self.__debug = x

    def toggle_debug(self) -> None:
        self.debug = not self.debug

    def __getattr__(self, __name: str, /) -> Any:
        # See: https://stackoverflow.com/questions/3278077/difference-between-getattr-and-getattribute
        # `__getattr__` is only invoked if the attribute wasn't found the usual ways.
        # `__getattribute__` is invoked before looking at the actual attributes on the object.
        # I.e. lookups for the settings attributes will never come here, since they are resolved
        # before entering this function.
        if __name.startswith('_'):
            raise AttributeError('Names starting with underscores (`_`) are not allowed.')
        return self.__getitem__(__name)

    def __setattr__(self, __name: str, __value: Any, /) -> None:
        if __name in ['data', 'debug'] or __name.startswith(f'_{type(self).__name__}'):
            return super().__setattr__(__name, __value)

        if __name.startswith('_'):
            raise AttributeError('Names starting with underscores (`_`) are not allowed.')

        return self.__setitem__(__name, __value)

    def __repr__(self) -> str:
        return f'·{self.data}'

    def as_dict(self) -> dict:
        '''Casts the DotDict to dict recursively.

        `dict(DotDict)` will not recursively process.
        '''
        res = dict()
        for k, v in self.items():
            if type(v) == DotDict:
                v = dict(v)
            res[k] = v

        return res


def partition(func: Callable, d: Iterable) -> Tuple[Iterable, Iterable]:
    a, b = [], []
    for item in d:
        a.append(item) if func(item) else b.append(item)
    return a, b


def partitionx(func: Callable, d: Iterable) -> Tuple[Iterable, Iterable]:
    a, b = [], []
    for item in d:
        if func(item):
            a.append(item)
        else:
            b.append(item)
    return a, b


def is_dict(v: Any) -> bool:
    return type(v) in [dict, UserDict]


def partition_dict(func: Callable, d: Union[dict, UserDict, DotDict]) -> Tuple[dict, dict]:
    a, b = dict(), dict()
    for k, v in d.items():
        if func(v):
            a[k] = v
        else:
            b[k] = v
    return a, b


# Extra remarks

# Use @property for read-only values if you have hidden the original value.
# e.g. if you hide self.__settings, then using this syntax is necessary to access its contents from
# outside of this class.
