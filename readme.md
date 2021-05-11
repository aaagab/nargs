# NARGS USER DOCUMENTATION

There are two documentation files:
- [Nargs user's documentation](readme.md) is for developers who create programs that use Nargs as a module. 
- [Nargs end-user's documentation](nargs-syntax.md) describes Nargs command-line syntax to interact with programs using Nargs as a module.

## Table of Contents
- [Specifications](#specifications)
- [Why Nargs?](#why-nargs)
- [Get Started](#get-started)
- [Glossary](#glossary)
- [Nargs Class](#nargs-class)
    - [Nargs \_\_init__](#nargs-init)
    - [Nargs dump](#nargs-dump)
    - [Nargs get_documentation](#nargs-getdocumentation)
    - [Nargs get_metadata_template](#nargs-getmetadatatemplate)
    - [Nargs get_default_theme](#nargs-getdefaulttheme)
    - [Nargs get_args](#nargs-getargs)
- [Arguments Definition](#arguments-definition)
    - [Arguments Options with Default Values:](#arguments-options-with-default-values)
        - [Options Default Values](#options-default-values)
        - [Options Types](#options-types)
        - [Options Explained](#options-explained)
    - [Notes on YAML Arguments Definition Files and Pickle binaries](#notes-on-yaml-arguments-definition-files-and-pickle-binaries)
- [Built-in Arguments](#built-in-arguments)
- [Arguments Explicit Implicit Notation](#arguments-explicit-implicit-notation)
    - [Explicit Notation](#explicit-notation)
    - [Implicit Notation](#implicit-notation)
    - [Note](#note)
    - [Examples](#examples)
- [Command-line Values Notation](#command-line-values-notation)
    - [Argument Aliases](#argument-aliases)
- [Nargs Errors Contexts](#nargs-errors-contexts)
- [How to Implement Nargs Global Arguments](#how-to-implement-nargs-global-arguments)
- [How to Implement a Nargs Radio Button Like Argument](#how-to-implement-a-nargs-radio-button-like-argument)

## Specifications
- Nargs has 3 contexts: 
  - arguments definition, command-line arguments, and in code arguments.
- Arguments definition is set with either a JSON file, a Python dictionary, or a YAML file.
  - JSON definition file and Python dictionary can have their nodes arguments duplicated with `@` notation.
  - Once parsed, definition can be cached to reach the fastest definition parsing possible.
- Built-in command-line Arguments (--cmd, --conf-path, --examples, --help, --uuid4, --usage, --version).
- Four aliases forms: concatenated, dashless, long, and short.
- Auto-aliases: long form alias and short form alias are set automatically if aliases are not provided in arguments definition.
- There are several notations for argument's values. Values can be set either with spaces, or with equal notation. i.e.:
  - `main.py value1 value2`
  - `main.py -a value1 value2`
  - `main.py -a="value1"`
  - `main.py --arg='value1'`
  - `main.py -a="value1 value2"`
  - `main.py --arg='value1 "this is value2"'`
  - `main.py --arg "one value"`
  - `main.py --arg one two three`
- Infinite arguments nesting, with explicit and implicit notations to select arguments.
- Explicit notation uses symbols `-` and `+` signs. i.e.:
  - implicit: `main.py --arg --sibling-arg`
  - explicit: `main.py - --arg + --sibling-arg`
  - implicit: `main.py --arg --nested-arg --sibling-arg`
  - explicit: `main.py --arg - --nested-arg ++ --sibling-arg`
- Special global commands on the command-line for current argument:
  - Use `:` to print argument and children usage.
  - Use `@` to print argument path and values.
  - Use `e` to print argument and children definition examples fields.
  - Use `h` to print argument and children hint fields.
  - Use `i` to print argument and children info fields.
- Repeated Arguments behavior can be defined:
  - `repeat="error"` triggers an error when argument is repeated.
  - `repeat="append"` appends values to the same argument when repeated.
  - `repeat="create"` creates an argument's fork each time an argument is repeated.
  - `repeat="replace"` resets previous argument's fork if any.
- In code Nargs returns a CliArg class object that has for members argument properties and nested arguments objects. Arguments can then be accessed with their name either dynamically with a string in a dictionary or as a class member.
- On the command-line Nargs allows variable placeholders that may be substituted by environment variables.
- Arguments sibling order does not matter in definition. Arguments order is set by user with conditional statements inside code.
- Auto-generated documentation from definition file, that can be printed to the terminal or exported in the following formats: asciidoc, html, markdown, and text.
- Auto-generated documentation may include [Nargs end-user's documentation](nargs-syntax.md).
- Typed argument's values:
  - Standard types: `bool, float, int, and str`.
  - File types: `dir, file, path, vpath`.
  - JSON types: `.json, json`

## Why Nargs?
- Nargs prevents end-users from guessing program arguments' combinations. An descriptive error is triggered for either each wrong argument or each wrong argument's values.
- Nargs auto-generated Help and Usage ensure that a program core documentation is provided out of the box.
- Nargs empowers users by providing them a notation for infinite arguments nesting.
- Nargs notation follows command-line arguments notation standard practice with its implicit arguments notation.  
- Nargs can be used to easily wrap existing command-line programs. It provides them all the Nargs bells and whistles from auto-generated documentation, arguments error checking, auto-aliases, multiple-forms aliases, ...
- Nargs built-in arguments ensure that programs provide a consistent arguments set for program identification with uuid4, version, help, usage, and more.

## Get Started
**Context: Arguments definition. User creates arguments definition with either**:  
- a YAML definition file (.yaml or .yml)
```bash
nano nargs.yaml
```
```yaml
prog:
  arg_one:
    nested_arg_one:
      _values: "*",
      nested_nested_arg_one: {}
  arg_two:
    _values: "*",
    _repeat: create,
    nested_arg_two: {}
      _values: "*",
```

- a JSON definition file (.json)
```bash
nano nargs.json
```
```json
{
  "prog":{
    "arg_one":{
      "nested_arg_one":{
        "_values": "*",
        "nested_nested_arg_one":{}
      }
    },
    "arg_two":{
      "_repeat":"create",
      "_values": "*",
      "nested_arg_two":{
        "_values": "*"
      }
    }
  }
}
```

- Python dictionary as definition
```python
dy_args=dict(
  prog=dict(
    arg_one=dict(
      nested_arg_one=dict(
        _values="*",
        nested_nested_arg_one=dict()
      )
    ),
    arg_two=dict(
      _repeat="create",
      _values="*",
      nested_arg_two=dict(
        _values="*",
      )
    )
  )
)
```

In arguments definition, argument's options start with underscore and argument's children start with either an uppercase letter or a lowercase letter.  

**Context in code arguments. User creates program's logic according to arguments properties and values**:  
```bash
nano program.py
```
```python
import sys
from ..gpks.nargs import Nargs

dy=dict(
  name="My Program",
  executable="program",
  version="1.2.3",
  uuid4="12345678-1234-1234-1234-123456789123",
)

# this is how Nargs object is created
# use either:
args=Nargs(definition="nargs.yaml", metadata=dy).get_args()
# or
args=Nargs(definition="nargs.json", metadata=dy).get_args()
# or
args=Nargs(definition=dy_args, metadata=dy).get_args()

## Then user creates program's logic with either:
### Nargs object class attributes
if args.arg_one._here:
    if args.arg_one.nested_arg_one._here:
        # print argument first value
        print(args.arg_one.nested_arg_one._value)
        # print all argument values
        print(args.arg_one.nested_arg_one._values)
        sys.exit(0)

### Nargs object class attributes and dictionary
if args._["arg_one"]["_here"]:
    if args._["arg_one"]._["nested_arg_one"]["_here"]:
        print(args._["arg_one"]._["nested_arg_one"].["_value"])
        sys.exit(0)

### Nargs arguments can be looped, option _repeat allows multiple arguments forks.
for arg in args.arg_two._forks:
  if arg.nested_arg_two._here:
    print(args.arg_one.nested_arg_two._value)
  sys.exit(0)

## using forks with class attributes and dictionary
for arg in args._["arg_two"]["_forks"]:
  if arg._["nested_arg_two"]["_here"]:
    print(args._["arg_one"]._["nested_arg_two"].["_value"])
  sys.exit(0)
```

**Context: command-line. End-user provides arguments to execute program functions**:
```bash
# arguments implicit notation
program.py --arg-one --nested-arg-one
program.py --arg-two --nested-arg-two value1 value2 "value 3" --arg-one
program.py --arg-two="value1 value2 \"value 3\"" --nested-arg-two

# arguments explicit notation
program.py - --arg-one - --nested-arg-one
program.py - --arg-two - --nested-arg-two value1 value2 "value 3" ++ --arg-one
program.py - --arg-two="value1 value2 \"value 3\"" - --nested-arg-two

# special terminal commands
program.py --arg-two :
program.py --arg-two ::
program.py --arg-two @
program.py :
program.py --arg-two value --nested-arg-two value value

# built-in arguments
program.py --version
program.py --uuid4
program.py --help
program.py --usage
```

## Glossary
- **Generic Package Manager (GPM)**: References to the Generic Package Manager can be found throughout this documentation. The Generic Package Manager is an ongoing project that is not available publicly yet. For instance `gpm.json` file refers to main configuration file from package managed by the Generic Package Manager. The import statement `from ..gpks.nargs import Nargs` is also related to GPM. Nargs is a standalone module and does not need the Generic Package Manager, however Nargs Module is needed in order to continue the Generic Package Manager development.  
- **user**: Developer who create a program that use Nargs as a module.  
- **end-user**: Person that interact on the command-line with a program using Nargs module.
- **Host Program**: Program created by user that import Nargs as a module.  
- **arguments**: In code arguments are objects from Nargs CliArg class. In definition arguments are tree nodes with properties and children arguments. On the command-line arguments are selected by typing their aliases.   
- **arguments siblings level**: Arguments are defined with a tree structure where executable (i.e.: `main.py`) is generally the root argument. Nested arguments can be defined at will from the root argument. Each argument is on a siblings level. Root argument is siblings level 1, then its children are on siblings level 2, and siblings level continue incrementing if more children of children are added.  
- **arguments aliases**: User calls arguments on the command-line with arguments' aliases. For a given argument `arg_one` aliases may be `--arg-one, -a, argone, arg-one`. Arguments' aliases are only unique at their siblings level.  
- **arguments names**: An argument name is a string chosen by user to identify an argument at the argument's siblings level in the arguments definition tree. An argument's name is unique at its sibling level. Argument's name is later used in code by user to set program's logic.  
- **command-line**: It is either the end-user's terminal command-line from `sys.argv`, user providing a command-line string with Nargs Class `cmd` parameter, or end-user providing a command-line with Nargs built-in `cmd` argument value.  
- **Nargs Arguments' contexts**:
    - **command-line arguments**: Arguments are provided through the command-line i.e. `program.py --my-argument my_value my_other_value --my-other argument`.
    - **arguments' definition**: Arguments are defined either in a JSON file, YAML file, or a Python dictionary. i.e. `{"prog": "arg_one": {"nested_arg":{}}}`
    - **in code arguments**: It generally refers to `main.py` file. It is where user writes program's logic using arguments. i.e. `if root.arg_one.nested_arg._here:`  
- **Root argument**: It is the command-line's first argument or the calling program name with or without path. It starts the cmd. i.e.: in cmd `dev/prog.py --arg-one` root argument is `dev/prog.py`  

## Nargs Class
```Python
class Nargs():
  def __init__(self,
    cached_dfn=None,
    definition=None,
    explicit=False,
    metadata=dict(),
    pretty=True,
    substitute=False,
    theme=None,
    usage_on_root=True,
  ):
    self.args=None

  def dump(self,
    filenpa=None
  ):
    return dump

  def get_args(self, 
    cmd=None,
  ):
    return args

  def get_default_theme():
    return dict()

  def get_metadata_template():
    return dict()

  def get_documentation(self, output, filenpa=None, wsyntax=False):
    return str
```

**WARNING**: Nargs class attributes starting with an underscore are either internal fields or internals functions and user should ignore them. Internal attributes may be changed at anytime without being considered a breaking change. Internal attributes are also not documented.  

### Nargs \_\_init__
- **cached_dfn**: This parameter helps speeding-up arguments command-line parsing by using cached arguments definition data. `cached_dfn` accepts either a JSON string, a dict, a .json file, or a .pickle file. If either provided .json file or provided .pickle file does not exist then Nargs will create the cache file by automatically calling Nargs().dump() with the file as argument for filenpa. The JSON string, dict, .json file, or .pickle file must have been generated from `Nargs().dump()` otherwise an unexpected error is triggered.  If `cached_dfn` data exists then Nargs uses that data as arguments' definition instead of generating the cached-definition. `cached_dfn` relative paths are resolved according to `Nargs()` class caller file path and not user current directory on the command-line. It allows to keep cached_dfn dump files in the project. Definition is not needed anymore when `cached_dfn` points to existing cached data. **Warning**: when `cached_dfn` is set any changes to definition is ignored. In other words `cached_dfn` is generally set when application is packed for production release (see also [Nargs dump](#nargs-dump) or [Arguments Definition](#arguments-definition)).  
- **definition**: This parameter provides arguments definition to Nargs. Parameter is ignored if cached_dfn has been provided with cached data. `definition` accepts either, a dict, or a .json/.yaml/.yml file path (relative or absolute). Relative path is relative to `Nargs()` class caller file path (see also [Arguments Definition](#arguments-definition)). `definition` can be an empty dictionary. `definition` is set to an empty dictionary when it equals `None`.  
- **explicit**: This parameter sets Nargs `explicit` mode to True or False. If parameter is set to True then only explicit notation is authorized when providing Nargs arguments command. If parameter is set to False then both explicit notation and implicit notation are authorized (see [Arguments Explicit Implicit Notation](#arguments-explicit-implicit-notation).  
- **metadata**: This parameter accepts a dictionary that helps populating built-in arguments, usage and help. User can get available fields with Nargs function `Nargs.get_metadata_template()`. Any metadata field that is not present, null or empty is discarded. Provided fields are trimmed. Program `name` and `executable` fields are mandatory and it needs to be provided in metadata parameter i.e. `Nargs(metadata=dict(name="My Program", executable="program"))`. (see also [built-in arguments](#built-in-arguments))  
- **pretty**: This parameter sets Nargs `pretty` mode to True or False. When set to True, it prints colored usage and colored help on the command-line.  
- **substitute**: This parameter sets Nargs `substitute` mode to True or False. If `substitute=True`, it allows to have any variable placeholders with syntax `__variable__` from the terminal command to be substituted with matching environment variables. It is useful on Windows systems. Syntax must match regex `__([a-zA-Z][a-zA-Z0-9]*)__`  
- **theme**: This parameter accepts a style dictionary to style both help, usage in the terminal and help when exported to html (see also [Nargs get_default_theme](#nargs-get_default_theme), [Nargs get_documentation](#nargs-get_documentation)).  
- **usage_on_root**: This parameter sets Nargs `usage_on_root` mode to True or False and it determines if usage is printed when only root argument is provided. `usage_on_root` is set to True by default. This mode is only effective when both using `Nargs().get_args()` and when arguments definition has been provided or when root argument `_enabled` property is set to True. The reason for providing `usage_on_root` parameter is that arguments on siblings level 2 are generally optional but they are the ones calling program's function and not the root argument. Thus without `usage_on_root` parameter, end-user would type the root argument at the command-line without nothing happening. Now with Nargs parameter `usage_on_root` end-user can see the program's usage by default when typing only the root argument. This behavior is not wanted in all scenarios and user can disable it by setting `usage_on_root` to False.  

### Nargs dump
User writes the least amount of data possible in order to create definition data (file or dict). Nargs always parses the entire definition data before parsing command-line arguments. Nargs validates arguments and properties syntax during definition parsing. For instance Nargs sets default properties values, and it transforms other properties for inner-processing. A dump is the final output of the arguments definition parsing process. A dump can be stored and retrieved for faster command-line parsing. It may be useful in production environment for large definition file. User may use `Nargs().dump()` to get a dump of its definition file. Then in order to reuse that dump, user can feed it to `Nargs(cached_dfn=dump_data)`. A dump is also auto generated if user sets `cached_dfn` with a non-existing file path. In that case the type of dump is going to be defined with the file path extension (`.json` for JSON dump and `.pickle` for pickle dump).  
**filenpa**: User can specify a file path for the dump when calling `Nargs().dump(filenpa="userpath.json")`. Given file directory must exist. `Nargs().dump()` relative paths are resolved according to `Nargs()` class caller file path and not user current directory on the command-line. It allows to keep `cached_dfn` dump files in the project. For most scenarios, only `cached_dfn` is needed for user instead of using `Nargs().dump()` . However in some cases user may want to call `Nargs().dump()` function manually when developing. For instance user can get a definition dump output in order to add it directly in its code as a JSON string. In other words `Nargs().dump()` is only used once to extract a definition dump.  
**WARNING**:  
- If regular definition data is parsed with `Nargs(cached_dfn="")`then the program will throw an unexpected error and parsing will break. 
- `Nargs().dump()` resets Arguments Tree. It means that if `Nargs().dump()` is called manually after `Nargs.get_args()` then user will not be able to access command-line arguments from in code context. A warning is triggered to notify user about the behavior when `Nargs().dump()` is called manually. This behavior is not an issue when using `cached_dfn` because `cached_dfn` is always executed before `Nargs.get_args()` thus warning is not triggered.
- Both `Nargs().dump()` and `Nargs(cached_dfn="")` throw and error when arguments definition is null or empty or when root argument `_enabled` property is set to False.  

### Nargs get_documentation
`Nargs().get_documentation()` allows to get the documentation in multiple formats. `get_documentation()` returns formatted help as a string, excepts for `cmd_usage`, and `cmd_help`. `output` parameter sets the output format and it can have one of the following values:
- "asciidoc": returns help string in ASCIIDOC format.
- "cmd_help": print help to the terminal.
- "cmd_usage": print usage to the terminal.
- "markdown": returns help string in MARKDOWN format.
- "html": returns help string in HTML format.
- "text": returns help string in text format.

If a file path is provided to `filenpa` parameter and output is not `cmd_usage` or `cmd_help` then help is going to be written to that file. If `wsyntax=True` then Arguments' help syntax cheat sheet is appended to the help see [Nargs end-user's documentation](nargs-syntax.md). The cheat sheet provides end-user a thorough description of Nargs syntax for help and usage. `Nargs().get_documentation()` is also provided through Nargs built-in arguments:  
- `--usage` for `cmd_usage`
- `--help` for `cmd_help`
- `--help --export` with either `asciidoc`, `html`, `markdown` or `text` for the different export formats. i.e.: `prog.py --help --export html --to documentation.html --syntax`  

`Nargs().get_documentation()` provides minimum documentation data even when arguments definition is either empty or disabled.   

### Nargs get_metadata_template
In order to include metadata information in Nargs module user can provide a dictionary by using `Nargs(metadata=dict())`. A dictionary template can be retrieved with `Nargs.get_metadata_template()`. Available fields are:  
- authors: list, optional. program's authors.
- description: string, optional. program's description.
- executable: string, required. program's alias.
- licenses: list, optional. program's licenses.
- name: string, required. program's name.
- conf_path: string, optional. program's conf_path.
- uuid4: string, optional. program's uuid4.
- version: string, optional. program's version.
- timestamp: float, optional. program latest version's timestamp.

### Nargs get_default_theme
`Nargs.get_default_theme()` returns default built-in theme dictionary with the following style elements: 
- `about_fields`
- `aliases_indexes`
- `aliases_text`
- `examples`
- `examples_bullet`
- `headers`
- `hint`
- `info`
- `nargs_sheet_emphasize`
- `nargs_sheet_headers`
- `square_brackets`
- `values_text`

Each field accepts a dict with the following properties:  
```python
dict(
  background=None,
  bold=False,
  foreground=None,
  italic=False,
  underline=False,
)
```
`Nargs.get_default_theme()` gives user a complete set of style elements with their properties that can be set by user.  
User can customize help, and usage on the command-line and html export by modifying properties values for the different style elements and providing them to Nargs with `Nargs(theme=user_theme)`. If user does not provide a theme, then a built-in theme is provided. Built-in theme uses colors from `David Liang wombat256.vim's theme`. If user wants to style the theme, user does not need to provide all style elements, nor all the properties. For instance when user add a style element in its theme dictionary then theme style element is automatically set with non-initialized values. Then for each user style elements' properties user's values are set. i.e. user theme may be:
```python
user_theme=dict(
  examples=dict(
    bold=True,
    foreground="#123456"
  ),
  headers=dict(
    underline=True,
    background="123;456;789",
  )
)
```
`bold, italic, and underline` style element properties accept a boolean value.  
`background and foreground` style element properties accept a string value that must be an hexadecimal color (hashpound optional) or a RGB color split with semi-colon.  
`Nargs(theme=dict())` is disabled on the command-line when `Nargs(pretty=False)`.  

Theme is mainly use for output format `cmd_usage` (if pretty is True), `cmd_help` (if pretty is True), `html`. Other formats like `asciidoc`, `markdown`, and `text` do not rely on theme to provide help or usage. html format has also added global CSS rules that are hard-coded and can only be modified manually by the user in the exported help i.e.:`body { background-color: #2b2b2b;}`.  

### Nargs get_args
`Nargs.get_args()` returns the root command-line argument node for user to create in code logic.  
**cmd**: It is provided either implicitly from end-user typing arguments on the command-line, explicitly from user providing Nargs cmd parameter, or implicitly from end-user providing Nargs built-in cmd. When `Nargs().get_args()` cmd parameter is provided either explicitly from user providing Nargs cmd parameter or implicitly from end-user providing Nargs built-in cmd then root parameter must be provided with one of its argument alias. Argument's aliases are either explicitly provided by user in arguments definition or implicitly automatically generated by Nargs. In order to know root argument alias, Usage can be printed by either end-user or user. When end-user types arguments to the command-line `cmd` is provided implicitly with `sys.argv` and the root argument is the first argument of the command-line. When `cmd` is provided by `sys.argv` then the root argument does not need to match the root argument's alias. In this context root argument matches the name of the executable that launches the program i.e. `program.py`.  

For each argument on the command-line Nargs create a CliArg object with `argument children` and `argument properties`.  
```python
class CliArg():
  def __init__(self, name):
      self._=dict()
      self._alias=None
      self._default_alias=None
      self._index=None
      self._id=None
      self._forks=None
      self._here=None
      self._name=name
      self._parent=None
      self._value=None
      self._values=[]

  def get_path(self, explicit=False, wvalues=False):
    pass
```

**Note**: Class properties with underscore notation are not considered internal fields in the CliArg Class context. In other words user can use these properties. Any future modification for these fields would be considered a Nargs major version change or breaking change. Underscore prefix for `CliArg` provides:  
- a differentiation between `CliArg argument's properties` and `CliArg argument's children`.
- a shorter in code notation for user. For instance to test the presence on the command-line of a deeply nested argument could be written this way: `rootArg.argOne.nestedArg.nestedNestedArg.nestedNestedNestedArg._here`.

**argument children** are all CliArg class members that allow accessing children arguments. Nargs parses the arguments definition and a CliArg object is created for each child argument. CliArg object children are added dynamically if any. Nargs uses `setattr()` to add children arguments as class members. It allows user to type arguments in the in code context as if arguments were a nested namespaces. i.e.: `root_arg.arg_one.nested_arg_one._here`. children argument class member names start with either an uppercase letter or a lowercase letter.  

**argument properties** are all CliArg class members that are not a child argument. An argument property starts with an underscore:  
- `self._`: It is a dict that permits dynamic access to argument's properties and and children:
    - For argument properties `self._ dict` is filled with CliArg attributes name as keys and CliArg attributes values as values.
    - For argument children `self._ dict` is filled with CliArg children arguments names as keys and CliArg children arguments objects addresses as values.
- `self._alias`: It is set with end-user argument's alias as provided in the command-line.
- `self._default_alias`: Default alias is automatically generated and it is only used in the `get_path()` function. Default alias is either the first given or automatically set long alias if any, the first given dashless alias if any, or the first given or automatically set short alias if any.
- `self._index`: Each argument has an index. The first time an argument is used on the command-line, `_index` is set to 1. Later if argument option `_repeat="create"` and the argument is repeated on the command-line then a new argument is created and its index is incremented by one.  
- `self._id`: This attribute is a unique argument's identifier that is composed of all the argument's parents' `_index` plus the argument's `_index`. All `_index` properties are joined with a dot to create the argument's `_id`. This attribute is mainly used when generating the definition for internal purpose.  
- `self._forks`: This property always returns a list that contains at least the argument object address. When an argument is created its object address is appended to `self._forks`. If argument option `_repeat="create"` and end-user types multiple times the argument on the command-line, then for each `"fork"` of the argument a new argument is created and the new argument's address is appended to the `self._forks`. In other words `self._forks` is a list of twin nodes that is shared between all twin nodes. It allows later for user in code to loop through an argument `self._forks` to manage an argument's multiple forks. i.e.: `for arg_fork in root_arg.arg_one._forks:`  
- `self._here`: It defines if an argument is present on the command-line. Nargs generates the whole CliArg arguments tree at once. If an argument is repeated and option `_repeat="create"` then a new complete fork of the repeated argument is created. It means that all command-line arguments are always available to user for in code logic. However having an argument created does not mean it is present on the command-line. That is why property `_here` is needed to allow determining if an argument is present on the command-line. i.e.: `if root_arg.arg_one._here is True:`  
- `self._name`: It is the name of the argument as set in the arguments definition.
- `self._parent`: It provides the argument CliArg parent object's address of an argument. It is mainly used for Nargs internal purpose when parsing the command-line.  
- `self._value`: It returns `None` if argument has no values on the command-line, or a value if the argument have one or more values. If argument has multiple values `self.value` returns the first value.  
- `self._values`: It returns an empty list if argument has no values on the command-line, otherwise it returns a list of values. For instance, if argument has only one value then `_values` returns a list that contains only the value.   

**get_path**: argument `get_path()` returns all parent aliases joined with spaces. If `explicit=True` then explicit notation is used between arguments. For each returned alias, alias is returned with index notation if the alias related argument has multiple forks .i.e: `--arg-one_1 --arg-one_2`. If `wvalues=True` then only the values of the argument are returned after the argument alias. When `Nargs` throw an error to end-user, `get_path` is used to provide the argument's full path. Arguments aliases are provided by end-user through command-line but sometimes user may want to get an argument's path that is not present on the command-line. In this context, `get_path()` returns argument and parent arguments default aliases see [Options Explained _aliases](#options-explained). : 

Argument's aliases are set in `_aliases` option that is either set by user or set by auto-alias function. Each argument has a `default alias` that is selected from argument's `_aliases` option. Default alias is whatever alias that comes first from:  
- either the first long form alias or the first dashless form alias
- the first short form alias  

## Arguments Definition
User can write arguments definition either as a Python dictionary, a YAML file or a JSON file. It is a tree structure and its first node is the root argument. Nargs definition can be empty and in this case `Nargs().get_args()` returns None. Argument's properties start with an underscore. Argument's children names start with a letter.    

`@` is a special notation for argument name in arguments definition that can duplicate an argument and its nested arguments to a different location in the arguments tree. Nargs triggers an error for infinite recursion if any when using `@` duplicate notation. `@` is useful to duplicate similar nested arguments. This notation is only needed when user sets definition in a JSON file or a Python dictionary. `@` is not needed for definition in a YAML file because arguments can be duplicated with existing YAML syntax `node anchors (&) and references (*)`.  
```json
// "@" notation duplicates nodes
{
  "gpm": {
    "arg_one":{
      "nested_arg_one": {
        "nested_nested_arg": {}
      },
      "nested_arg_two": {
        "nested_nested_arg": {}
      }
    },
    "arg_two": {
      // either notation one (a string for one node)
      "@": "arg_one.nested_arg_one",
      // or notation two (a string with commas to split multiple nodes)
      "@": "arg_one.nested_arg_one,arg_one.nested_arg_two",
      // or notation three (a list of nodes)
      "@": [
        "arg_one.nested_arg_one",
        "arg_one.nested_arg_two"
      ]
    }
  }
}
```
### Arguments Options with Default Values:
For each argument in definition file, all the options below can be set. If these options are not set then their default values are set. None of these options need to be set, they are all optional.  
To set an option means that option is present in argument's definition and option value is not null. An option with a null value is considered not set and this option is automatically set with its default value.  

In arguments definition, argument's options starts with an underscore and argument's children arguments do not. The first argument or root argument is set like any other arguments. All other arguments are children of the root argument. User can infinitely nest arguments. Arguments' name must match regex `[a-zA-Z][a-zA-Z0-9_]*`. User will generally not be using a lot of argument's options. User will probably rely on default argument options. For instance when user writes a small arguments definition like `dict(prog=dict(my_arg=dict()))`,  user already have:  
- argument aliases automatically created. `prog.py --my-arg` or `prog.py -m`
- all the built-in arguments' aliases are available depending on metadata provided.
- [command-line special commands](nargs-syntax.md#special-commands)  

#### Options Default Values
```python
{
  "_aliases": None,
  "_default": None,
  "_either": None,
  "_enabled": True,
  "_examples": None,
  "_hint": None,
  "_in": None,
  "_info": None,
  "_label": None,
  "_repeat": "replace",
  "_required": False,
  "_show": True,
  "_single": False,
  "_type": None,
  "_values": None,
}
```

#### Options Types
**_aliases**: null, string (comma split), or list of strings.  
**_default**: null, or same type as defined in `_type`.  
**_either**: null, string (comma split), or list of strings (comma split).  
**_enabled**: null, or boolean.  
**_examples**: null, string, or list of strings.  
**_hint**: null, or string.  
**_in**: null, string (comma split), list of strings, or dictionary.  
**_info**: null, or string.  
**_label**: null, or string.  
**_repeat"**: null, or string.  
**_required**: null, or boolean.  
**_show**: null, or boolean.  
**_single**: null, or boolean.  
**_type**: null, or string.  
**_values**: null, or string.  

#### Options Explained
**_aliases**: Set aliases for argument. Each argument can have no aliases or unlimited number of aliases. If no aliases are provided or `_aliases=None` then Nargs auto-alias inner function is triggered and creates arguments' aliases automatically. For instance for arg_one, auto-alias is going to set aliases `-a` and `--arg-one`. Arguments' aliases are used on the command-line and arguments' names are used in the code. A valid argument needs to have at least one alias form otherwise an error is triggered. Built-in arguments can be overloaded by user aliases and an error won't be triggered if they don't have an alias left. If at least one alias is set manually for an argument then auto-alias won't apply to this argument. During alias setup a `default alias` is automatically set. `default alias` is used in a special case [Nargs get_args get_path](#nargs-get_args). User can set 3 types of aliases for an argument in definition: 
- long form alias:
  - regex: `^--[a-zA-Z0-9][a-zA-Z0-9\-]*$` 
  - example: `--argument`
- short form alias:
  - regex: `^-[a-zA-Z0-9]$` 
  - example: `-a`
- dashless form alias:    
  - regex: `^[a-zA-Z0-9][a-zA-Z0-9\-]*$` 
  - example: `argument` or `a`  
```python
# aliases syntax is a string where are aliases are split with a comma
"aliases": "-a,--arg,arg"
"aliases": ["-a" ,"--arg", "arg"]
```
It is recommended to use dashless form aliases on arguments that accept no values. This way it is easier to differentiate values from arguments when reading the command-line.  
Even root argument has aliases because it can be repeated like any other arguments if its option `_repeat="create"`. `Concatenated short form alias` is another form of arguments' alias that is only available on the command-line (see [Argument Aliases](#argument-aliases)).  

**_default**: Option sets argument's default value(s). If `_default` is set and `_type` is None, then `_type` is set to `str`. If `_default` is set and `_values` is None then `_values` is set with number of `_default` values. `_default` type and number of values must match both `_type` and `_values` when `_type` and `_values` have already been set. If `_default` is `None` then it is ignored. If argument is provided on the command-line without a value and values are required then the argument default value(s) is/are added automatically. `_default` value(s) must also match `_in` values if `_in` is set. `_default` values must matches any type from `bool`, `float`, `int`, `str`. `_default` values must match type `str` when option `_type` is either `dir`, `file`, `path`, or `vpath`. `_default` can't be set when option `_type` is either `.json`, or `json`, otherwise Nargs throws an error.  

**_either**: Option determines if children arguments are compatible at siblings levels. `_either` create groups of arguments that can't be used at the same time at their siblings level. `_either` is set at the parent argument and applies on the children arguments. `_either` accepts a string or a list of strings. Each string defines a group of children arguments names split with commas. An argument can't be both present in its parent `_either` options and have its option `_single=True` or `_required=True`.  
```python
# _either different notations
"_either": "arg_one,arg_two,arg_three"
# it means that arg_one can't be present if arg_two is present or arg_three is present. Same logic applies to arg_two and arg_three.
"_either": [
    "arg_one,arg_two,arg_three",
    "turn_off,turn_on",
]
# In this second notation another _either group has been added. It means that turn_off argument can't be used if turn_on argument is present. 
```

**_enabled**: Option defines if argument and its children arguments are parsed. If set to False then the argument is disabled and not visible in the help. Also all its nested arguments are disabled. If root argument is disabled then Nargs will silently discard end-user command-line arguments and `Nargs.get_args()` will return `None`.  

**_examples**: Option provides argument's command examples. It accepts a string or a list of string. User can provide command examples for a particular argument. Argument examples are then printed on the screen if any when end-user types either `--help` or a [command-line special commands](nargs-syntax.md#special-commands).  

**_hint**: Option provides a short description of the argument's purpose. It accepts a string or a list of strings. `_hint` length is limited to 100 char.  

**_in**: Option sets a list of authorized values for an argument. If `_in` is set and `_type` is None, then `_type` is set to `str`. If `_in` is set and `_values` is None then `_values` is set to 1. `_in` accepts either a list, a string, or a dict:   
- If `_in` is a list then all list values must match argument's `_type`.
- If `_in` is a string then string is comma split to create a list and all list values are cast to match argument's `_type`.
- If `_in` is a dict then dictionary keys are labels that can be provided by end-user. Matching dictionary values are returned to the program. Each dict key value can match either `null` or any type from `bool`, `float`, `int`, and `str`. dictionary keys must be of type string.  

`_in` can't be set when option `_type` is either `.json`, or `json`, otherwise Nargs throws an error. `_in` matching type is string for `_in` list of values or `_in` dictionary keys when argument's type is either `dir`, `file`, `path`, or `vpath`.  

```python
# _in option syntax
## comma split string
"_in": "building,house",
## list
"_in": [0,1],
## dictionary
"_in": {
  "min": 0,
  "max": 1,
}
## dictionary
"_in": {
  "on": True,
  "off": False,
}
```  
**_info**: Option provides the argument's purpose full description. `_info` accepts either a string or a list of strings. `_info` has no length limit.  

**_label**: Option provides a label for argument's values. Label is printed with help or usage commands. `_label` must be a string or null. Label is put to uppercase when set. i.e. if `labels:"fruit"` for argument items with aliases --item then help may print `[--item [<str:FRUIT>]]`. `_label` can't be set when `_in` is present. If `_label` is set:  
- if `_values` is not set, then `_values` is set to 1.
- if `_type` is not set, then `_type` is set to `str`.

**_repeat**: Option defines Nargs action when an argument is typed several times by end-user on the command-line. Same argument can be added several times on the command-line. Even the whole program can be repeated on the command-line by using argument root's aliases. `_repeat` default value is `replace`. There are four actions for `_repeat` option:  
- **append**: It means that only one argument is kept and each repeated argument's values are appended to a list of values for the argument. In this context, `arg._alias` is set with the latest alias user input in the terminal.  
- **create**: It means that each repeated argument creates a new independent argument or fork with its own nested arguments. Multiple same arguments are also called twin arguments. Each twin argument keeps the alias provided to create the argument. End-user can accurately select a twin argument with its alias and its index. For instance two forks have been created for `arg_one` with command `prog.py --arg-one --arg-one`. Then if end-user wants to go back to first fork it can uses notation underscore with index .i.e. `prog.py --arg-one --arg-one + --arg-one_1 --arg-one_2`. Here `--arg-one_1` goes back to the first --arg-one argument and `--arg-one_2` to the second --arg-one argument. `Underscore index alias notation` only works with existing forks of an argument. It means that `--arg-one_1` will always work but `--arg-one_2` or greater may not work. `_repeat` property applies also to root argument. It means that end-user can also repeats the program as many times as end-user needs and underscore index notation is also available to root argument. i.e.:  
```bash
# explicit
prog.py - --arg-one ++ --prog - --arg-one ++ --prog_1 - --arg-one
# implicit
prog.py --arg-one --prog --arg-one --prog_1 --arg-one
```
- **exit**: It means that an error is triggered if the argument is repeated.  
- **replace**: It means that only one argument is kept and each repeated argument's values replace the previous argument's values. In this context, the last alias used is the one kept for the argument. If nested arguments have already been selected on the command-line with a previous argument, then they are reset to their non-selected state when selecting the same argument. .i.e.: `_repeat:"replace"` means that basically you restart an argument fork as if it has not already been selected on the command-line.  

**_required**: Option defines if argument is required when end-user adds argument's parent to command-line. If end-user types an argument that has a child argument with option `_required` set to True and end-user does not type the child argument then Nargs throws an error. `_required` option is set to True for root argument only and it can't be changed for root argument. Root argument is always required. `_required` option is set to False by default for all the other arguments. An error is thrown if an argument `_required` option is set to True and argument's name is present in parent argument `_either` option.  

**_show**: Option defines if argument is printed in help, usage and documentation. If set to False end-user and user can still use the argument but argument won't show either in help, usage, or documentation.  

**_single**: Option sets argument as a single sibling. Nargs throws an error if at a siblings level a `_single` argument is present with other argument(s). `_single` option can't be set if either option `_required` is set to True or option `_either` is set to False.  

**_type**: Option sets type argument's value(s). If option `_type` is set and option `_values` is not set, then option `_values` is set to 1. Argument's values are cast to the different types. Multiple types are supported:  

- **bool**: Argument value(s) expected must be of type boolean. Bool is generally a string that is case insensitive and is equal to 'true' or 'false'. If 1 is given then it is interpreted as true. If 0 is given then it is interpreted as false.
- **float**: Argument value(s) expected must be of type float.
- **int**: Argument value(s) expected must be of type integer.
- **str**: Argument value(s) expected must be of type str.
- **dir**: Argument value(s) expected is a relative or absolute path to an existing directory.
- **file**: Argument value(s) expected is a relative or absolute path to an existing file.
- **path**: Argument value(s) expected is a relative or absolute path to either an existing directory or an existing file.
- **vpath**: Argument value(s) expected is a relative or absolute path to an existing or non-existing directory or file.
- **json**: Argument value(s) expected is a JSON/YAML string. String may be single-quoted.
- **.json**: Argument value(s) expected is either a .json/.yaml/.yml file or JSON/YAML string that may be single-quoted.
- In types `dir`, `file`, `path`, and `vpath`, relative paths are resolved according to terminal current directory.
- JSON strings can be single-quoted.
- YAML strings or YAML files are discarded if PyYAML has not been installed.

**_values**: Option sets the accepted number of argument's values. An argument's values are first either required or optional and second they have a minimum and a maximum number of values. `_values` can be expressed as:  
- a positive integer: number of values is set as `required`.
- a string that matches regex `r"^(?P<star>\*)|(?P<plus>\+)|(?P<qmark>\?)|(?P<min>[1-9][0-9]*)(?:\-(?P<max>(?:[1-9][0-9]*|\*)))?(?P<optional>\?)?$"` with rules:
  - If string equals '*' it means that values are optional and number of values can range from 1 to infinite.
  - If string equals '+' it means values are required and number of values must range from 1 to infinite.
  - If string equals '?' it means values are optional and number of values can be 1.
  - If string equals a number i.e. 4:
    - number must be a positive integer. 
    - If number ends with a question mark then values are optional.
    - If number does not end with question mark values are required.
    - If values are given on the command-line then the number of values must be equal to the positive integer. 
  - If string equals a range i.e. 4-5 or 4-*: 
    - Range sets a minimum and a maximum number of values. 
    - Minimum must be a positive integer. 
    - Maximum must be either a positive integer or a star char. 
    - If Maximum number of values is a positive integer then it must be greater than minimum number of values. 
    - Star char sets maximum number of values to infinite. i.e.: 4-*
    - If range ends with a question mark then values are optional.
    - If range does not end with question mark then values are required. 
- If `_type` is not set and `_values` is set then `_type` is set to `str`.
- `_values` examples:
```python
# optional values with minimum 1 and maximum infinite
_values="*"
# required values with minimum 1 and maximum infinite
_values="+"
# optional values with minimum 1 and maximum 1
_values="?"
# optional values with number of values set to 5
_values="5?"
# optional values with minimum 1 and maximum 9
_values="1-9?"
# optional values with minimum 2 and maximum infinite
_values="2-*?"
# required values with number of values set to 5
_values="5"
# required values with minimum 1 and maximum 9
_values="1-9"
# required values with minimum 2 and maximum infinite
_values="2-*"
```

If an argument is present on the command-line and argument's values are required but no values are present then:  
- if argument's `_default` option is set then values are implicitly added from `_default` option.
- if argument's `_default` option is not set then Nargs throws an error.

### Notes on YAML Arguments Definition Files and Pickle binaries

In order to use .yaml/.yml definition file, user and end-user needs to `pip install pyyaml`. PyYAML import statement is only triggered if a YAML file is provided. In other words users only using JSON definition file do not need to install PyYAML.  
Parsing a YAML file reveals to be 300x times slower using PyYAML 5.4.1 safe_load, than parsing JSON file, according to a quick benchmark test. In order to improve speed with PyYAML you can use the CLoader this way: `yaml.load("!!python/object/new:os.system [echo EXPLOIT!]", Loader=yaml.CLoader)`. This time, yaml is only 50x times slower than JSON. However as you can see in the code snippet, your YAML file can also executes arbitrary code. It means you can't trust your configuration file as it could behave like a script when parsed. Nargs only use the PyYAML SafeLoader, which is safe to use against arbitrary code `yaml.load("!!python/object/new:os.system [echo EXPLOIT!]", Loader=yaml.SafeLoader)`. YAML definition file is still an interesting choice despite being slower to parse than JSON. YAML files are smaller, easier to read and to write. User may need to use a JSON definition file to speed-up slow application startup. For instance, it takes approximately `0.001s` to parse a JSON file of approximately 2000 nodes and it takes `0.3s` with the same file written in YAML.  
In order to improve both speed in yaml and security user could implement yaml as a string inside code this way:
```python
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

# CLoader is only available if PyYAML has been built with libyaml so speed may not be available on all devices.
# It can be verified with if yaml.__with_libyaml__ returns True

yaml_str=r"""
prog:
  arg_one: 
    _values: "0..."
    nested_arg_one: 
      _aliases: "-n,--nested-arg-one"
      nested_nested_arg_one:
    nested_arg_two:
      _aliases: "-b,--nested-arg-two"
  arg_two:
    _aliases: -b,--arg-two
"""

args=Nargs(definition=yaml.load(yaml_str, Loader=Loader))
```

The best way to improve Nargs arguments parsing speed is to use Nargs `cached_dfn` parameter see [cached_dfn](#nargs-__init__). `.pickle` format can be used to cache Nargs arguments definition however it suffers from the same safety issue than YAML parsing because arbitrary code may be executed. So end-user should either:  
- ensure the package definition file integrity
- generates the pickle cached definition with `cached_dfn` Nargs parameter on first program run after program installation.  

## Built-in Arguments
Nargs provides end-user built-in arguments:  
```json
{
  "cmd": {
    "_aliases": "-c,--cmd",
    "_hint":"Load program's arguments from a file.",
    "_type":"file"
  },
  "conf_path": {
    "_aliases": "--conf-path",
    "_hint": "Print program configuration path."
  },
  "examples": {
    "_aliases": "--examples",
    "_hint": "Print program examples."
  },
  "help": {
    "_aliases": "-h,--help",
    "_hint": "Print program help.",
    "export": {
      "_hint": "Export help to selected format.",
      "_in": "asciidoc,html,markdown,text",
      "to":{
        "_hint": "Export help to selected path.",
        "_type": "vpath"
      }
    },
    "syntax":{
      "_hint":"Print arguments Cheat Sheet syntax."
    }
  },
  "uuid4": {
    "_aliases": "--uuid4",
    "_hint": "Print program UUID4."
  },
  "usage": {
    "_aliases": "--usage",
    "_hint": "Print program usage."
  },
  "version": {
    "_aliases": "-v,--version",
    "_hint": "Print program version."
  }
}
```

Built-in arguments `cmd, examples, help, usage` are available to end-user if user did not overload their aliases in arguments definition. Built-in arguments `conf_path, uuid4, version` are available to end-user only if they exists in Nargs `metadata` dictionary and user did not overload their aliases in arguments definition. In order to import metadata Nargs searches first a `gpm.json` file in the program executable root directory. If `gpm.json` file is found then it is used as a based dictionary for Nargs metadata. If `gpm.json` file is not found then Nargs metadata starts with an empty dictionary. User can also provide a dictionary through `Nargs(metadata=dict())` parameter and this dictionary is merged into Nargs based metadata dictionary. In other words, Nargs metadata comes first from a gpm.json file if any and then user metadata is merged into that dictionary and user metadata overloads any previous similar dictionary key. User can overload built-in arguments if arguments with similar aliases than arguments built-in aliases are provided in arguments definition at siblings level 2. Overloaded built-in arguments are set to `_enabled` equals False and thus they are not available anymore.  

`cmd` built-in argument allows end-user to write command-line arguments in a file with newlines, empty lines, indentation, and comments using '#'. `cmd` goal is to overcome terminal command length limitation and/or to allow user to write commands in a readable way. When command-line is provided through built-in argument `cmd` then the root argument must match its argument's alias. Root argument's alias is provided in the arguments definition either implicitly by Nargs auto-alias generation or explicitly by user.  

`conf_path` built-in argument provides end-user host program configuration path as set in Nargs `metadata`. A module called `Etconf` manages configuration and can provide configuration path to Nargs host program. i.e. `metadata=dict(conf_path=etconf.direpa_configuration)`.  

`examples` built-in argument prints all the examples written into user Nargs arguments definition (see [Arguments Definition with property \_examples](#arguments-definition)).  

`help` built-in argument generates host program minimum help from Nargs arguments definition and metadata. Users and end-users can print help to terminal with `prog.py --help` or export it in 4 different formats `asciidoc`, `html`, `markdown`, and `text`. A file path can also be provided. i.e.: `prog.py --help --export html --to ../userpath.html`. Help can be printed or exported with arguments `syntax` explained. `--help --syntax` gives end-user the essential information to understand how to read and use Nargs Notation. Help has multiple sections:  
- About Section: It provides metadata information from the program. Metadata is provided implicitly with `gpm.json` and/or explicitly by user with `Nargs metadata` parameter. The printed fields are `Authors, Date, Description, Executable, Licenses, Name, UUID4, Version`.
- Usage Section: It provides program's usage. 
- Help Section: It provides program's help.
- Examples Section: It provides all program's examples.
- Nargs Argument Syntax Section. It contains:
    - Nargs module metadata.
    - How to read Nargs syntax.
    - How to type arguments and values in the terminal.

`uuid4` built-in argument prints program uuid4 to the terminal.  

`usage` built-in argument prints all the arguments in a tree structure with Nargs notation.  

`version` built-in argument prints program version and if program executable parent directory equals `beta` then Nargs returns `version-beta` i.e.: `1.2.3-beta`. Adding suffix `-beta` function is related to the `Generic Package Manager gpm`.  
  
Built-in arguments are only available at siblings level 2. If there are multiple forks of the root argument and built-in arguments are typed by end-user then the built-in triggered is going to be the latest built-in typed.  

## Arguments Explicit Implicit Notation
In order to navigate through the arguments tree, end-user can provide arguments on the command-line by using two notations **explicit notation** and **implicit notation**. There is always a reference argument when using explicit or implicit notation. The reference argument is the current argument. For instance when Nargs starts parsing a command-line the first reference argument is the root argument. Then any other argument provided on the command-line becomes reference argument one after the other following `Nargs().get_args()` parsing the command-line from left to right.  

### Explicit Notation
Explicit notation describes exactly the arguments position in the arguments tree using `+` and `-` symbols. Explicit notation is used to exactly select one alias argument from multiple same alias located at different siblings levels. Explicit notation is optional when Nargs explicit parameter is set to False and it can be mixed with implicit notation.
Explicit notation uses the following syntax before an argument:  
**dash symbol `-`**: It goes down one siblings level (siblings level increments). Only one dash symbol can be used before an argument.  
**plus symbol `+`**: It goes up one siblings level (siblings level decrements). Unlike `-` notation, multiple `+` characters can be concatenated for instance `++` or `++++` until the siblings level reaches 1 maximum (`++` means go up 2 siblings levels). `+` notation also accepts a positive integer instead of concatenation i.e. `+4` permits to go up four siblings levels at time.  
After an explicit notation end-user has to provide an argument otherwise Nargs through an error. When end-user navigates in the arguments tree, end-user goes either up to reach root argument or down to access nested arguments. However siblings level starts at 1 for the root argument and the siblings level is incremented for each nested arguments level. Thus there is an inverse relationship between the end-user navigation direction and the siblings level incrementation.

**Explicit notation pros**:  
- notation describes exactly each argument location in the argument's tree.
- Explicit notation added to values quoted notation would allow a third party program to accurately parse a Nargs terminal command without arguments definition.

**Explicit notation cons**:  
- It is verbose and thus hard to read.

### Implicit Notation
Implicit notation allows to navigate through the arguments tree without using **dash symbol syntax** or **plus symbol syntax**. Arguments' aliases are searched implicitly in the arguments tree. For instance the root argument does not need to use the `-` symbol for its nested arguments because root argument is the only sibling at level 1. Then for lower siblings level, aliases may be needed. Implicit notation is forbidden if Nargs explicit parameter is set to True. Implicit notation is optional and can be mixed with explicit notation when Nargs explicit parameter is set to False. For a given argument's alias in the terminal, implicit notation follows the rules:  
- Alias is first searched in current argument's children arguments aliases.
- If not found alias is searched in parent argument's children arguments aliases. When not found the process is repeated recursively to all argument's parents until reaching the root argument. If alias is not found then Nargs throw an error on the command-line.
- End-user needs explicit notation to select chosen alias when chosen alias is located in a parent argument but the same alias is also present in the reference argument's children.
**Implicit notation pros**:  
- Shorter notation.
- Closer to command-line arguments "standard syntax". 
**Implicit notation cons**:  
- It is hard to read even if it is less verbose than explicit notation.
- It is limited because end-user still needs to use explicit notation in specific scenarios.
- Terminal command can't be parsed by a third-party program in a consistent way without arguments definition.

### Note
Both explicit notation and implicit notation are hard to read for long command-line. It is not specific to Nargs but to any program that accepts command-line. To improve terminal commands readability, Nargs use the following features:  
- [command-line special commands](nargs-syntax.md#special-commands).
- [Built-in argument cmd](#built-in-arguments).
- Nargs `cmd` parameter.

### Examples
For definition:  
```yaml
prog:
  arg_one: # auto-alias sets aliases to "-a and --arg-one". 
    nested_arg_one: 
      _aliases: "-n,--nested-arg-one"
      nested_nested_arg_one: {} # auto-alias sets aliases to "-n and --nested-nested-arg-one"
    nested_arg_two:
      _aliases: "-b,--nested-arg-two"
  arg_two:
    _aliases: -b,--arg-two
```

```bash
# explicit
main.py - --arg-one - --nested-arg-one - --nested-nested-arg-one + --nested-arg-two + --arg-two
# semi explicit/implicit (both notation can be mixed together)
main.py --arg-one --nested-arg-one - --nested-nested-arg-one + --nested-arg-two --arg-two
# implicit
main.py --arg-one --nested-arg-one --nested-nested-arg-one --nested-arg-two --arg-two

# explicit notation is needed in some scenarios. 
# implicit 
main.py -a -n -b # -b selects nested_arg_two
# explicit 
main.py -a -n + -b # -b selects arg_two
```

## Command-line Values Notation
More information on command-line syntax is available at [Nargs end-user documentation](nargs-syntax.md).  

For definition:  
```yaml
prog:
  _values: "?"
  arg_one: # implicit aliases "-a,--arg-one"
    _values: "+"
    nested_arg_one:
      _aliases: "-n,--nested-arg-one"
      nested_nested_arg_one: {}
    nested_arg_two:
      _aliases: "-b,--nested-arg-two"
  arg_two:
    _aliases: "-b,--arg-two"
    _values: "?"
```

Values Notations are:  
```bash
main.py value
main.py -a value
main.py -a value1 value2 "this is value 3"
main.py -a="value"
main.py -a='value1 value2 "this is value3"'
main.py --arg-one value
main.py --arg-one value1 value2 "this is value 3"
main.py --arg-one="value"
main.py --arg-one='value1 value2 "this is value3"'
```

### Argument Aliases
Three argument aliases form have been described in [Options Explained \_aliases](#options-explained):  
- long form alias
- short form alias
- dashless form alias

There is another alias form that can be used by end-user on the command-line. It is a `concatenated short form alias`. A `concatenated short form alias` starts with a dash and each char represents one existing short form alias argument. Concatenated short form alias follows specific rules:  
- regex: `^-[a-zA-Z0-9][a-zA-Z0-9]+$`
- Concatenated short aliases are built from arguments that have short aliases only.
- Concatenated aliases don't accept values. It means arguments' values must be optional or null.
- Concatenated aliases don't accept underscore index notation. End-user can't select its argument's fork. The argument's fork selected is the current one. Same argument can be repeated if `_repeat` option allows it i.e. `-aaa`.
- Short Aliases concatenated notation does not work with explicit notation.
- All arguments short aliases that forms a concatenated alias must be on the same siblings level.

Example with definition:  
```yaml
prog:
  arg_one:
    _aliases: "-a,--arg-one"
  arg_two:
    _aliases: "-b,--arg-two"
  arg_three:
    _aliases: "-c,--arg-three"
```
```bash
# working
main.py -acbb
# equivalent to implicit
main.py --arg-one --arg-three --arg-two --arg-two
# equivalent to explicit
main.py - --arg-one + --arg-three + --arg-two + --arg-two
```

## Nargs Errors Contexts
- **Nargs in definition**: error comes from user arguments' definition context.
- **Nargs on the command-line**: error comes from end-user command-line arguments context.
- in code arguments context errors are not managed. These errors should be mainly class attributes error. i.e.: `AttributeError: 'CliArg' object has no attribute`.  

## How to Implement Nargs Global Arguments
A global argument is an argument that is available on all siblings levels of the arguments tree. Nargs [command-line special commands](nargs-syntax.md#special-commands) are available globally but they are not arguments that can be defined by user. There is no global arguments in Nargs. Built-in arguments are only available on arguments siblings level 2. However user can simulate a global argument by using argument implicit notation. For instance starting at current argument if another argument alias is located at siblings level 2 and no other arguments have the same alias in current argument children or current argument parents then user can provide argument alias located at siblings level 2 and it is going to be called as if it was a global argument. Simulating a global argument does not necessarily happens on siblings level 2, because arguments definition is a tree structure. Thus simulating global arguments can happen on any siblings level that is higher than current argument.  

## How to Implement a Nargs Radio Button Like Argument
A radio button like argument is an argument that provides multiple option and only one can be selected at a time. There are two ways:
- with values using `_in` option. i.e.: `_in="logout,reboot,shutdown,suspend"
- with argument's aliases using `_aliases` option. i.e.: `_aliases="--logout,--reboot,--shutdown,--suspend"

In Definition:  
```yaml
prog.py:
  home_server:
    _in: "logout,reboot,shutdown,suspend"
  work_server:
    leave:
      _aliases: "--logout,--reboot,--shutdown,--suspend"
```

In code for user:  
```python
# for _in option
if prog.home_server._here:
  if prog.home_server._value == "logout":
    pass
  elif prog.home_server._value == "reboot":
    pass
  elif prog.home_server._value == "shutdown":
    pass
  elif prog.home_server._value == "suspend":
    pass

# for _aliases option
if prog.work_server.leave._here:
  if prog.work_server.leave._alias == "--logout":
    pass
  elif prog.work_server.leave._alias == "--reboot":
    pass
  elif prog.work_server.leave._alias == "--shutdown":
    pass
  elif prog.work_server.leave._alias == "--suspend":
    pass
```

On the command-line for end-user:
```shell
# _in option
prog.py --home-server logout
# _aliases option
prog.py --work-server --logout
```
