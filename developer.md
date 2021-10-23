# NARGS USER DOCUMENTATION

There are two documentation files:
- [Nargs developer's documentation](developer.md) is for developers who create programs that use Nargs as a module. 
- [Nargs end-user's documentation](end-user.md) describes Nargs command-line syntax to interact with programs using Nargs as a module.

## Table of Contents
- [NARGS USER DOCUMENTATION](#nargs-developer-documentation)
  - [Table of Contents](#table-of-contents)
  - [Specifications](#specifications)
  - [Why Nargs?](#why-nargs)
  - [Get Started](#get-started)
  - [Glossary](#glossary)
  - [Nargs Class](#nargs-class)
    - [Nargs \_\_init__](#nargs-__init__)
    - [Nargs dump](#nargs-dump)
    - [Nargs get_documentation](#nargs-get_documentation)
    - [Nargs get_metadata_template](#nargs-get_metadata_template)
    - [Nargs get_default_theme](#nargs-get_default_theme)
    - [Nargs get_args](#nargs-get_args)
  - [Arguments Definition](#arguments-definition)
    - [Arguments Properties with Default Values:](#arguments-properties-with-default-values)
      - [Properties Default Values](#properties-default-values)
      - [Properties Types](#properties-types)
      - [Properties Explained](#properties-explained)
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
  - Once parsed for the first time definition is cached to reach the fastest definition parsing possible.
  - Caching format can be either json (safer) or pickle (may be faster)
  - Definition can also only be read from cache.
- Built-in command-line Arguments (cmd, help, path_etc, usage, version).
- Built-in arguments usage and help are color themeable.
- Multiple aliases prefixes: `"", "+", "-", "--", "/", ":", "_"`.
- Concatenated flags aliases with at symbol i.e. `@123aAbBcC`. 
- Flags are context-sensitive.
- Built-in usage argument can provide details on available flags for each argument.
- Command-line arguments form a tree where each node may have multiple branches.
- Auto-aliases with default prefix and alias style.
- There are several notations for argument's values. Values can be set either with spaces, or with equal/comma notation. i.e.:
  - `main.py value1 value2`
  - `main.py -a value1 value2`
  - `main.py -a="value1"`
  - `main.py --arg='value1'`
  - `main.py --arg=value1`
  - `main.py -a="value1 value2"`
  - `main.py --arg='value1 "this is value2"'`
  - `main.py --arg "one value"`
  - `main.py --arg one two three`
  - `main.py -a:"value1"`
  - `main.py --arg:'value1'`
  - `main.py --arg:value1`
  - `main.py -a:"value1 value2"`
  - `main.py --arg:'value1 "this is value2"'`
- Infinite arguments nesting, with explicit and implicit notations to select arguments.
- Explicit notation uses symbols `-`, `=` and `+`. i.e.:
  - implicit: `main.py --arg --sibling-arg`
  - explicit: `main.py - --arg = --sibling-arg`
  - implicit: `main.py --arg --nested-arg --sibling-arg`
  - explicit: `main.py --arg - --nested-arg + --sibling-arg`
- Multiple same argument occurences may be defined:
  - `_repeat="append"` appends values to the same argument when repeated.
  - `_repeat="error"` triggers an error when argument is repeated.
  - `_repeat="replace"` resets and replace previous argument's branch and values if any.
- In code Nargs returns a CliArg class object that has for members argument properties and nested arguments objects. Arguments can then be accessed:
  - Dynamically with their name in a dictionary
  - With their name as a class member.
  - From a list that follows the order they have been selected.
- Even non-selected arguments on the command-line are available in the arguments tree through dictionary and class members.
- On the command-line Nargs allows variable placeholders that may be substituted by environment variables.
- Auto-generated documentation from definition file, that can be printed to the terminal or exported in the following formats: asciidoc, html, markdown, and text.
- Auto-generated documentation may include [Nargs end-user's documentation](end-user.md).
- Typed argument's values:
  - Standard types: `bool, float, int, and str`.
  - File types: `dir, file, path, vpath`.
  - JSON types: `.json, json`
- Logical rules may be set to arguments by using arguments definition properties `_allow_parent_fork`, `_allow_siblings`, `_need_child`, `_repeat`, `_required`, `_xor`.

## Why Nargs?
- Nargs prevents end-users from guessing program arguments' combinations. A descriptive error is triggered for either each wrong argument or each wrong argument's values.
- Nargs auto-generated Help and Usage ensure that a program core documentation is provided out of the box.
- Nargs empowers users by providing them a notation for infinite arguments nesting.
- Nargs notation follows command-line arguments notation standard practice with its implicit arguments notation.  
- Nargs can be used to easily wrap existing command-line programs. It provides them all the Nargs bells and whistles from auto-generated documentation, arguments error checking, auto-aliases, multiple-forms aliases, ...
- Nargs built-in arguments ensure that programs provide a consistent arguments set for program identification with cmd, help, usage and version.

## Get Started
**Context: Arguments definition. Developer creates arguments definition with either**:  
- a YAML definition file (.yaml)
```bash
nano nargs.yaml
```
```yaml
args:
  arg_one:
    nested_arg_one:
      _values: "*"
      nested_nested_arg_one:
  arg_two:
    _fork: true
    _values: "*"
    nested_arg_two:
      _values: "*"
```

- a JSON definition file (.json)
```bash
nano nargs.json
```
```json
{
  "args":{
    "arg_one":{
      "nested_arg_one":{
        "_values": "*",
        "nested_nested_arg_one":{}
      }
    },
    "arg_two":{
      "_fork": true,
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
  args=dict(
    arg_one=dict(
      nested_arg_one=dict(
        _values="*",
        nested_nested_arg_one=dict()
      )
    ),
    arg_two=dict(
      _fork=True,
      _values="*",
      nested_arg_two=dict(
        _values="*",
      )
    )
  )
)
```

In arguments definition, argument's properties start with underscore and argument's children start with either an uppercase letter or a lowercase letter.  

**Context in code arguments. Developer creates program's logic according to arguments properties and values**:  
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

## Then developer creates program's logic with either:
### Nargs object class attributes
if args.arg_one._here:
    if args.arg_one.nested_arg_one._here:
        # print argument first value
        print(args.arg_one.nested_arg_one._value)
        # print all argument values
        print(args.arg_one.nested_arg_one._values)
        sys.exit(0)

### Nargs object class attributes and dictionary
if args._["arg_one"]._here:
    if args._["arg_one"]._["nested_arg_one"]._here:
        print(args._["arg_one"]._["nested_arg_one"]._value)
        sys.exit(0)

### Nargs arguments can be looped, property _fork allows multiple arguments branches.
for arg in args.arg_two._branches:
    if arg._here is True:
        print(arg._value)
    else: # arg is also present in the tree even if not on the command-line
        print(arg._value) # returns None
    sys.exit(0)

## using branches with class attributes and dictionary
for arg in args._["arg_two"]._branches:
    print(arg._value)
    sys.exit(0)
```

**Context: command-line. End-user provides argument.**:
```bash
# arguments implicit notation
program.py --arg-one --nested-arg-one
program.py --arg-two --nested-arg-two value1 value2 "value 3" --arg-one
program.py --arg-two="value1 value2 \"value 3\"" --nested-arg-two

# arguments explicit notation
program.py - --arg-one - --nested-arg-one
program.py - --arg-two - --nested-arg-two value1 value2 "value 3" + --arg-one
program.py - --arg-two="value1 value2 \"value 3\"" - --nested-arg-two

# built-in arguments (alias prefix is developer defined)
program.py --help
program.py --usage
program.py --help --metadata --version
program.py --help --metadata --uuid4
```

## Glossary
- **Generic Package Manager (GPM)**: References to the Generic Package Manager can be found throughout this documentation. The Generic Package Manager is an ongoing project that is not available publicly yet. For instance `gpm.json` file refers to main configuration file from package managed by the Generic Package Manager. The import statement `from ..gpks.nargs import Nargs` is also related to GPM. Nargs is a standalone module and does not need the Generic Package Manager, however Nargs Module is needed in order to continue the Generic Package Manager development.  
- **developer**: Developer user who creates a program that uses Nargs as a module.  
- **end-user**: User who interacts on the command-line with a program using Nargs module.
- **fork**: To fork means to divide into two or more branches. `_fork` is an argument definition property that authorizes or denies the argument to have more than one branch.    
- **maintainer**: User in charge of developing and maintaining Nargs software.
- **Host Program**: Program created by developer that imports Nargs as a module.  
- **arguments**: In code arguments are objects from Nargs CliArg class. In definition arguments are tree nodes with properties and children arguments. On the command-line arguments are selected by typing their aliases.   
- **arguments node level**: Arguments are defined with a tree structure where executable (i.e.: `main.py`) is generally the root argument. Nested arguments can be defined at will from the root argument. Each argument is on a node level. Root argument is node level 1, then its children are on node level 2, and node level continues incrementing if more children of children are added.  
- **arguments aliases**: End-user calls arguments on the command-line with arguments' aliases. For a given argument `arg_one` aliases may be `--arg-one, -a, argone, arg-one`. Arguments' aliases are only unique at their node level.  
- **arguments names**: An argument name is a string chosen by developer to identify an argument at the argument's node level in the arguments definition tree. An argument's name is unique at its node level between siblings arguments names. Argument's name is later used in code by developer to set program's logic.  
- **arguments branches**: An argument's branch consists of both the argument and all its children. A new argument's branch consists of both a new instance of the argument and new instances of its children. Argument's branches are independent. It means that when an argument's branch is modified, it does not modify any other branches of the same argument.    
- **command-line**: It is either the end-user's terminal command-line from `sys.argv`, developer providing a command-line string with Nargs get_args `cmd` option, or end-user providing a command-line with Nargs built-in `cmd` argument value.  
- **Nargs Arguments' contexts**:
    - **command-line arguments**: Arguments are provided through the command-line i.e. `program.py --my-argument my_value my_other_value --my-other argument`.
    - **arguments' definition**: Arguments are defined either in a JSON file, YAML file, or a Python dictionary. i.e. `{"args": "arg_one": {"nested_arg":{}}}`
    - **in code arguments**: It generally refers to `main.py` file. It is where developer writes program's logic using arguments. i.e. `if root.arg_one.nested_arg._here:`  
- **Root argument**: It is the command-line's first argument or the calling program name with or without path. It starts the cmd. i.e.: in cmd `dev/prog.py --arg-one` root argument is `dev/prog.py`  

## Nargs Class
```Python
class Nargs():
  def __init__(self,
    args=None,
    auto_alias_prefix="--",
    auto_alias_style="lowercase-hyphen",
    builtins=None, # if None then it is set with ["cmd", "help", "usage", "version"],
    cache_file="nargs-dump.json",
    metadata=None, # if None then it is set with dict(),
    options_file=None,
    only_cache=False,
    path_etc=None,
    pretty_help=True,
    pretty_msg=True,
    substitute=False,
    theme=None, # if None then it is set with dict(),
  ):
    self.args=None

  def get_args(self, 
    cmd=None,
  ):
    return args

  def get_default_theme():
    return dict()

  def get_documentation(self, output, filenpa=None, wsyntax=False, overwrite=False):
    return str

  def get_metadata_template():
    return dict()
```

**WARNING**: Nargs class attributes starting with an underscore are either internal fields or internals functions and developer should ignore them. Internal attributes may be changed at anytime without being considered a breaking change. Internal attributes are also not documented.  

### Nargs \_\_init__

- **args**: This option provides arguments definition to Nargs. `args` accepts a dict (see also [Arguments Definition](#arguments-definition)).
- **auto_alias_prefix**: If developer does not set an alias for an argument in the definition, then the alias is auto-generated. Developer can choose what is the default prefix from this list `["", "+", "-", "--", "/", ":", "_"]` with option `auto_alias_prefix` i.e. `my-alias, +my-alias, -my-alias, --my-alias, /my-alias, :my-alias, _my-alias`.  
- **auto_alias_style**: If the alias is auto-generated from the argument name then several styles are possible for instance for an argument name `my_alias` the following auto-alias style can be provided with option `auto_alias_style`:
    - **camelcase**: i.e. myAlias
    - **camelcase-hyphen**: i.e. my-Alias
    - **lowercase**: i.e. myalias
    - **lowercase-hyphen**: i.e. my-alias
    - **pascalcase**: i.e. MyAlias
    - **pascalcase-hyphen**: i.e. My-Alias
    - **uppercase**: i.e. MYALIAS
    - **uppercase-hyphen**: i.e. MY-ALIAS
- **builtins**: This option allows to select which [built-in arguments](#built-in-arguments) are going to be added to developer program. Developer can add any built-in arguments from list`["cmd", "help", "usage", "version"]`. If `builtins` is None or an empty list built-in arguments are omitted. If only some built-in arguments are selected then only these selected built-in arguments are added to developer's program.  
- **cache_file**: This option provides a file path to cache Nargs options. Default value is `nargs-dump.json`.  Cache file path can be relative or absolute. Relative path is relative to `Nargs()` class caller file path. Developer can choose either `.json` or `.pickle` extension to cache Nargs options once they have been parsed. There are 3 main elements that are checked to recreate the cache file: options provided with Nargs(), gpm.json file for metadata, and an options file. If any of these three elements are modified then the cache file is recreated. If cache file already exists and none of the three elements have been modified then nargs options are extracted from the cache file instead of being parsed with Nargs module. Caching improves speed when parsing because it allows having all the options and arguments definition grammar checked only once. JSON format is the safest and PICKLE format maybe the fastest because unlike JSON cache, arguments definition objects are already stored in the PICKLE cache. However PICKLE file may be compromised.  
- **metadata**: This option accepts a dictionary that helps populating built-in arguments, usage, help, and version. Developer can get common metadata fields with Nargs function `Nargs.get_metadata_template()`. Any metadata field that is null or empty is discarded. Provided fields are trimmed. Program fields `name` and `executable` are mandatory and they need to be provided in metadata parameter i.e. `Nargs(metadata=dict(name="My Program", executable="prog"))`.  (see also [built-in arguments](#built-in-arguments))   
- **only_cache**: This option allows to load the cache_file definition without checking changes on the developer provided definition. Some scenarios may required that functionality. For instance if a developer wants to include multiple Nargs definitions from different programs into the same program. If the cached definition is null Nargs throws an error and prevents the cache_file to be regenerated. If that error happens developer can regenerate the cache by setting only_cache to False.   
- **options_file**: This option allows to provide all the Nargs options from a file. It is the prefered method to provide `args` option. options_file must be a `.json/.yaml` file path (relative or absolute). Relative path is relative to `Nargs()` class caller file path (see also [Arguments Definition](#arguments-definition)). When Nargs is executed options are first read from `Nargs()` options and then if options file is provided then options file options overload previously defined similar options. `options_file` can be omitted. In order to use .yaml options file, developer and end-user needs to `pip install pyyaml`. PyYAML import statement is only triggered if a YAML file is provided. In other words users only using JSON definition file do not need to install PyYAML. Only safe_load is used to parse a YAML options file. YAML file reveals to be 300x times slower to parse using PyYAML 5.4.1 safe_load, than parsing JSON file, according to a quick benchmark test. However Nargs options are cached so a slower parsing time for options YAML file may only appears once before it is cached. YAML is the preferred format to write options file because of its shorter syntax and commenting capabilities. Options can be provided in four ways:  
    - from `Nargs()` in code context (all options).
    - from an option file which path is available through `Nargs option options_file` (all options).
    - from a `.nargs-user.json` or `.nargs-user.yaml` file located in nargs launcher directory (limited user options see [Nargs end-user's documentation](end-user.md)).
    - from a `.nargs-user.json` or `.nargs-user.yaml` file located in nargs path_etc directory if any (limited user options see [Nargs end-user's documentation](end-user.md)).  

The four ways to provide options cascade on top of each other and replace previous similar options. The precendence order from lowest precendence to highest precendence is `Nargs()`, `options_file.json`, `options_file.yaml` (options_file name can be any name), `.nargs-user.json` in launcher directory, `.nargs-user.yaml` in launcher directory, `.nargs-user.json` in path_etc directory, `.nargs-user.yaml` in path_etc directory.  
For options_file, and users file, if they provide both `.json` and `.yaml` files then for each of the location only the `.yaml` file is parsed.  

- **path_etc**: Developer can provide the application configuration directory with this option. If `path_etc` is provided then a builtin `path_etc` is appended to the builtins list. It creates a builtin argument that allows end-user to get the application configuration path i.e. `myprog.py --path-etc`.  
- **pretty_help**: If set to True usage and help are printed with ansi escape sequences formatting in terminal as set by default theme or developer theme.  
- **pretty_msg**: If set to True system message are printed with ansi escape sequences formatting in terminal.  
- **substitute**: This option sets Nargs `substitute` mode to True or False. If `substitute=True` commnand-line strings that match regex `(?:__(?P<input>input|hidden)__|__((?P<input_label>input|hidden)(?::))?(?P<label>[a-zA-Z][a-zA-Z0-9]*)__)` may be substituted either by developer input or environment variables values. Regex rules are:
    - strings start with double underscore
    - strings finish with double underscore
    - After underscore string starts with either a single letter (uppercase or lowercase), the word `input` or the word `hidden`.
    - If string starts with word either input or hidden:
        - end-user is prompted to provide a value and string is substituted on the command-line with typed value.
        - If colon and label is provided after word either input or hidden (i.e. `__input:username__`) then prompted text is going to be set with label value. Label value starts with a single letter then optional next characters are either letters (uppercase or lowercase) or numbers.
    - If string does not start with either input or hidden then string must start with a single letter then optional next characters are either letters (uppercase or lowercase) or numbers. In that case string without underscores is substituted with value of any matching environment variable names if any.
```bash
# developer prompted
> prog.py __input__
input: 
# developer prompted hidden
> prog.py __hidden__
hidden: 
# developer prompted with label
> prog.py __input:username__
username: 
# environment variable substitution
> prog.py __HOME__
# custom environment variable substitution
export WorkSpace="Iceland"
> prog.py __WorkSpace__
```
- **theme**: This option accepts a style dictionary to style both help, usage in the terminal and help when exported to html (see also [Nargs get_default_theme](#nargs-get_default_theme), [Nargs get_documentation](#nargs-get_documentation)).  

### Nargs get_documentation
`Nargs().get_documentation()` allows to get the documentation in multiple formats. `get_documentation()` returns formatted help as a string, excepts for `cmd_usage`, and `cmd_help`. `output` parameter sets the output format and it can have one of the following values:
- "asciidoc": returns help string in ASCIIDOC format.
- "cmd_help": print help to the terminal.
- "cmd_usage": print usage to the terminal.
- "markdown": returns help string in MARKDOWN format.
- "html": returns help string in HTML format.
- "text": returns help string in text format.

If a file path is provided to `filenpa` parameter and output is not `cmd_usage` or `cmd_help` then help is going to be written to that file. If `overwrite=True` and output file already exists then it is overwritten silently. If `overwrite=False` and output file already exists then Nargs throws and error. If `wsyntax=True` then Arguments' help syntax cheat sheet is appended to the help see [Nargs end-user's documentation](end-user.md). The cheat sheet provides end-user a thorough description of Nargs syntax for help and usage. `Nargs().get_documentation()` is also provided through Nargs built-in arguments:  
- `--usage` for `cmd_usage`
- `--help` for `cmd_help`
- `--help --export` with either `asciidoc`, `html`, `markdown` or `text` for the different export formats. i.e.: `prog.py --help --export html --to documentation.html --syntax`  

`Nargs().get_documentation()` provides minimum documentation data even when arguments definition is either empty or disabled.   

### Nargs get_metadata_template
In order to include metadata information in Nargs module developer can provide a dictionary by using `Nargs(metadata=dict())`. A dictionary template of common metadata can be retrieved with `Nargs.get_metadata_template()`. Common fields are:  
- authors: list, optional. program's authors.
- description: string, optional. program's description.
- executable: string, required. program's executable. It is the root argument name used in help and usage.
- licenses: list, optional. program's licenses.
- name: string, required. program's name.
- conf_path: string, optional. program's conf_path.
- uuid4: string, optional. program's uuid4.
- version: string, optional. program's version.
- timestamp: float, optional. program latest version's timestamp.  

Note: metadata `executable` is provided either by the developer, by `gpm.json alias field`, or by `sys.argv[0]` path basename. If developer provides common fields, then common fields type must match. When common fields are provided they populate About section generated by built-in argument `_help_`. Metadata can be retrieved by end-user using the built-in argument `--help --metadata` (see also [Built-in arguments](#built-in-arguments)).  

### Nargs get_default_theme
`Nargs.get_default_theme()` returns default built-in theme dictionary with the following style elements: 
- `about_fields`
- `aliases_text`
- `arg_index`
- `arg_path`
- `examples`
- `examples_bullet`
- `flags`
- `headers`
- `hint`
- `info`
- `nargs_sheet_emphasize`
- `nargs_sheet_headers`
- `square_brackets`
- `values_text`

Each field accepts a dict with the following properties:  
```json
{
  "background": null,
  "bold": false,
  "foreground": null,
  "italic": false,
  "underline": false,
}
```
`Nargs.get_default_theme()` gives developer a complete set of style elements with their properties that can be set by developer.  
Developer can customize help, and usage on the command-line and html export by modifying properties values for the different style elements and providing them to Nargs with `Nargs(theme=user_theme)`. If developer does not provide a theme, then a built-in theme is provided. Built-in theme uses colors from `David Liang wombat256.vim's theme`. If developer wants to style the theme, developer does not need to provide all style elements, nor all the properties. For instance when developer add a style element in its theme dictionary then theme style element is automatically set with non-initialized values. Then for each developer style elements' properties developer's values are set. i.e. developer theme may be:
```json
{
    "user_theme": {
        "examples": {
            "bold": true,
            "foreground": "#123456"
        },
        "headers": {
            "underline": true,
            "background": "123;456;789",
        }
    }
}
```
`bold, italic, and underline` style element properties accept a boolean value.  
`background and foreground` style element properties accept a string value that must be an hexadecimal color (hashpound optional) or a RGB color split with semi-colon.  
`Nargs(theme=dict())` is disabled on the command-line when `Nargs(pretty=False)`.  

Theme is mainly use for output format `cmd_usage` (if pretty is True), `cmd_help` (if pretty is True), `html`. Other formats like `asciidoc`, `markdown`, and `text` do not rely on theme to provide help or usage. html format has also added global CSS rules that are hard-coded and can only be modified manually by the developer in the exported help i.e.:`body { background-color: #2b2b2b;}`.  

### Nargs get_args
`Nargs.get_args()` returns the root command-line argument node for developer to create in code logic.  
**cmd**: It is provided either implicitly from end-user typing arguments on the command-line, explicitly from developer providing Nargs cmd parameter, or implicitly from end-user providing Nargs built-in cmd. When `Nargs().get_args()` cmd parameter is provided either explicitly from developer providing Nargs cmd parameter or implicitly from end-user providing Nargs built-in cmd then root parameter must be provided with one of its argument alias. Argument's aliases are either explicitly provided by developer in arguments definition or implicitly automatically generated by Nargs. In order to know root argument aliases, Usage can be printed by either end-user or developer. When end-user types arguments to the command-line `cmd` is provided implicitly with `sys.argv` and the root argument is the first argument of the command-line. When `cmd` is provided by `sys.argv` then the root argument does not need to match the root argument's alias. In this context root argument matches the name of the executable that launches the program i.e. `program.py`. `Nargs().get_args()` can be used multiple times with different command-lines. If get_args is used more than once then for each new use the arguments tree is reset. If developer modifies the arguments tree when setting-up program's logic in code then unexpected behavior may be triggered when using `get_args()` multiple times.  

For each argument on the command-line Nargs create a CliArg object with `argument children` and `argument properties`.  
```python
# class is defined at "dev/nodes.py"
class CliArg():
  def __init__(self):
    pass

  def _get_cmd_line(self, cmd_line_index=None):
    pass

  def _get_path(self, wvalues=False, keep_default_alias=False):
    pass
```

**Note**: Class properties with underscore notation are not considered internal fields in the CliArg Class context. In other words developer can use these properties. Any future modification for these fields would be considered a Nargs major version change or breaking change. Underscore prefix for `CliArg` provides:  
- a differentiation between `CliArg argument's properties` and `CliArg argument's children`.
- a shorter in code notation for developer. For instance to test the presence on the command-line of a deeply nested argument could be written this way: `rootArg.argOne.nestedArg.nestedNestedArg.nestedNestedNestedArg._here`.

**argument children** are all CliArg class members that allow accessing children arguments. Nargs parses the arguments definition and a CliArg object is created for each child argument. CliArg object children are added dynamically if any. Nargs uses `setattr()` to add children arguments as class members. It allows developer to type arguments in the in code context as if arguments were a nested namespaces. i.e.: `root_arg.arg_one.nested_arg_one._here`. children argument class member names start with either an uppercase letter or a lowercase letter.  

**argument properties** are all CliArg class members that are not a child argument. An argument property starts with an underscore:  
- `self._`: It is a dict that permits dynamic access to argument's children. `self._ dict` is filled with CliArg children arguments names as keys and CliArg children arguments objects addresses as values.
- `self._alias`: It is set with end-user argument's alias as provided on the command-line for latest argument's occurence.
- `self._aliases`: All arguments' aliases set at arguments definition.  
- - `self._branches`: This property returns a list that contains all branches of a command-line argument. At least one arguments branch starting at root argument is generated when `Nargs()` is executed and that tree is regenerated each time `get_args()` more than once. It means that all arguments are already available in code for developers even if they are not present on the command-line. It means that for an argument attribute `_branches` returns at least itself (CliArg object address) even if it is not on the command-line. When an argument is added on the command-line and it is the first time it is added then the argument is `actived`. Activated means that some arguments attributes are set. For instance `self._here` is set to `True`, and its parent if any has its attribute `_args` appended with the added argument object (see `set_arg()` in `src/dev/get_args.py`). If argument definition properties `_fork=True` and `_repeat="append"` then when argument is added on the command-line for the first time the argument branch already exists so it does not need to be created.  For each argument new branch, a new argument is created and all its children too. Then again the argument is activated and the argument object is appended to its property `_branches`. `_branches` property is a list that is shared between all the branches of the same argument. It is important to note that related branches of an argument share the same parent. For instance if argument's parent has also its `_fork` property that is set to True then the same children argument from definition args tree may have a different parent in the command-line args tree and thus the same arguments from definition may have branches that are not related to each other because they don't share the same parent. That is why in order to loop through all the arguments added to the command-line arguments tree it is important to loop through arguments starting from the root argument branches and then for each branch going down to each children branches.  
```python
# branches examples
root_arg=pkg.Nargs(options_file="../definition.yaml")

# simple looping through some arguments children
for branch_arg in root_arg._branches:
    for child_arg in branch_arg._args:
      for child_branch_arg in child_arg._branches:
          print(child_branch_arg._name)

# alternative
for branch_arg in root_arg._branches:
    for child_name in branch_arg._:
        child_arg=branch_arg._[child_name]
        for child_branch_arg in child_arg._branches:
            print(child_branch_arg._name)

# looping through all arguments available on the command-line with recursion
def process_args(arg):
    if arg._here is True:
        print(arg._name)
        for child_name in sorted(arg._):
            child_arg=arg._[child_name]
            for branch_arg in child_arg._branches:
                process_args(branch_arg)
## then call it that way
for branch_arg in arg._root._branches:
    process_args(branch_arg)


# looping through all arguments available on the command-line with recursion (alternative)
def process_args(arg):
    print(arg._name)
    for child_arg in arg._args:
        for branch_arg in child_arg._branches:
            if branch_arg._here is True:
                process_args(branch_arg)
## then call it that way
for child_arg in arg._root._args:
    process_args(child_arg)


# looping through all arguments available or not on the command-line with recursion
def process_args(arg):
    print(arg._name)
    for child_name in sorted(arg._):
        child_arg=arg._[child_name]
        for branch_arg in child_arg._branches:
            process_args(branch_arg)
## then call it that way
for branch_arg in arg._root._branches:
    process_args(branch_arg)

# non related branches for child_arg, child_arg._branches with parent root_arg._branches[0] are not related to child_arg._branches with parent root_arg._branches[1]
root_arg (branch 1)
  child_arg (branch 1)
  child_arg (branch 2)
  child_arg (branch 3)
root_arg (branch 2)
  child_arg (branch 1)
  child_arg (branch 2)
  child_arg (branch 3)
# on the command-line the below structure could be written this way
prog.py --child-arg_1 --child_arg_2 --child_arg_3 --args_2 --child-arg_1 --child_arg_2 --child_arg_3 
```
- `self._args`: It is a list that contains all children arguments that have been provided on the command-line in the order they have been provided. It may be useful to developer for in code context when end-user provided arguments' sorting order matters. When multiple occurences per branch of an arg is allowed with argument's definition properties `_repeat="append"` or `_repeat="replace"` then for each new occurence argument object is removed and appended from parent argument `self._args`. For `_repeat="append"` then the same object is appended and for `_repeat="replace"` then a new argument object is appended.  
- `self._cmd_line`: Only root argument on branch 1 (a.k.a. `root_arg._branches[0]`) has this attribute and it contains the command-line provided to Nargs. To retrieve command-line developer can do `print(arg._root._branches[0]._cmd_line)`.
- `self._cmd_line_index`: It provides the command-line index of the argument location on the command-line for latest argument's occurence. To print command-line for an argument developer can do `print(arg._root._branches[0]._cmd_line[arg._cmd_line_index])`. Implicit argument's command-line index is always the last explicit's argument command-line index (see [Nargs get_args /`_implicit`](#nargs-get_args)).  
- `self._count`: It returns the number of argument's occurences on the command-line per argument's branches. Every-time an argument is added on the command-line `_count` is incremented. The number of allowed occurences is related to argument's property `_repeat` (see [Properties Explained /`_repeat`](#properties-explained)). For each occurence when `_repeat="append"` then `_count` is incremented. For each occurence when `_repeat="replace"` then `_count` is always one.  
- `self._default_alias`: Default alias is automatically generated and it is used either with `_get_path()` function or when adding implicitly a required argument. Default alias is the first alias provided by developer in arguments definition with property `_aliases`.
- `self._dy_indexes`: It provides a dictionary with one key `aliases` and another key `values`. `self._dy_indexes["aliases"]` is a dictionary that have for keys command-line indexes as int and for values arguments aliases. This dictionary allows to know the command-line index and alias used for each occurence of an argument. `self._dy_indexes["values"]` is a list of command-line indexes for each argument values. The main purpose of `self._dy_indexes` is for developers to be able to throw errors with the exact location on the command-line of an argument alias(es) or one of its values. Implicit argument provides the argument's default alias and command-line index is always the last explicit's argument command-line index (see [Nargs get_args /`_implicit`](#nargs-get_args)).     
- `self._here`: It defines if an argument is present on the command-line (a.k.a. activated argument). Nargs generates the whole CliArg arguments tree at once. It means that all command-line arguments are always available to developer for in code logic. However having an argument available does not mean it is present on the command-line. That is why property `_here` is needed to allow determining if an argument is present on the command-line. i.e.: `if root_arg.arg_one._here is True:`  
- `self._implicit`: It is set to True if argument has been added implicitly (see [Properties Explained /`_required`](#properties-explained)). It is set to False if argument has been provided on the command-line.  
- `self._name`: It is the name of the argument as set in the arguments definition.
- `self._is_root`: It tells if current argument is at the root of the arguments tree.  
- `self._parent`: It provides the argument CliArg parent object's address of an argument. It is mainly used for Nargs internal purpose when parsing the command-line.  
- `self._root`: It provides the first branch of root argument to any arguments.
- `self._value`: It returns `None` if argument has no values on the command-line, or a value if the argument have one or more values. If argument has multiple values `self.value` returns the first value.  
- `self._values`: It returns an empty list if argument has no values on the command-line, otherwise it returns a list of values. For instance, if argument has only one value then `_values` returns a list that contains only the value.   

**_get_cmd_line**: It is a method that provides current argument command-line. It is the same as `print(arg._root._branches[0]._cmd_line[arg._cmd_line_index])`. A command-line index can be provide to print a different command-line. Note that for implicit arguments, `_get_cmd_line` can't return the command-line path of the current argument because implicit arguments have been added implicitly and they don't exist on the command-line. Instead `_get_cmd_line` returns the last explicit argument from where implicit arguments have been added. In order to print the path of implicit arguments in in-code context developer can use `self._get_path()` (see also [Nargs get_args /`_implicit`](#nargs-get_args)). Developer may use `self._implicit` to know when to use `_get_cmd_line` or when to use `_get_path` to print arguments' path.   

**_get_path**: argument `_get_path()` returns all parent aliases joined with spaces. For each returned alias, alias is returned with index notation if the alias related argument has multiple branches .i.e: `--arg-one_1 --arg-one_2`. Explicit notation is set when an alias conflict with parents aliases or children aliases. If `wvalues=True` then only the values of the argument are returned after the argument alias. When `Nargs` throw an error to end-user, `_get_path` is used to provide the argument's full path. Arguments aliases are provided by end-user through command-line but sometimes developer may want to get an argument's path that is not present on the command-line. In this context, `_get_path()` returns argument and parent arguments default aliases see [Properties Explained _aliases](#properties-explained). Path can also be forced to be printed with arguments default aliases by using option `keep_default_alias=True`. `_get_path` is different than `_get_cmd_line` because it gives the shortest path to an argument in the arguments tree whereas `_get_cmd_line` provides the whole command-line until the end of the selected argument alias is reached.      

Argument's aliases are set in `_aliases` property that is either set by developer or set by auto-alias function. Auto-alias function kicks in when developer does not provide an alias to argument in arguments definition with property `_aliases`. 

## Arguments Definition
Developer can write arguments definition either as a Python dictionary, a YAML file or a JSON file. It is a tree structure and its first node is the root argument. If Nargs definition is empty and Nargs builtins option is an empty list then `Nargs().get_args()` returns None. Argument's properties start with an underscore. Argument's children names start with a letter.    

`@` is a special notation for argument name in arguments definition that can duplicate an argument and its nested arguments to a different location in the arguments tree. Nargs triggers an error for infinite recursion if any when using `@` duplicate notation. `@` is useful to duplicate similar nested arguments. This notation is only needed when developer sets definition in a JSON file or a Python dictionary. `@` is not needed for definition in a YAML file because arguments can be duplicated with existing YAML syntax `node anchors (&) and references (*)`. Built-in arguments with aliases starting with a colon can't be duplicated.  
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
### Arguments Properties with Default Values:
For each argument in definition file, all the properties below can be set. If these properties are not set then their default values are set. None of these properties need to be set, they are all optional.  
To set a property means that property is present in argument's definition and property value is not null. An property with a null value is considered not set and this property is automatically set with its default value.  

In arguments definition, argument's properties starts with an underscore and argument's children arguments do not. The first argument or root argument is set like any other arguments. All other arguments are children of the root argument. Developer can infinitely nest arguments. Arguments' name must match regex `[a-zA-Z][a-zA-Z0-9_]*`. Developer will generally not be using a lot of argument's properties. Developer will probably rely on default argument properties. For instance when developer writes a small arguments definition like `dict(prog=dict(my_arg=dict()))`,  developer already have:  
- argument aliases automatically created. `prog.py --my-arg` or `prog.py -m`
- all the built-in arguments' aliases are available.

#### Properties Default Values
```python
{
  "_aliases": None,
  "_allow_parent_fork": True,
  "_allow_siblings": True,
  "_default": None,
  "_enabled": True,
  "_examples": None,
  "_fork": False,
  "_hint": None,
  "_in": None,
  "_info": None,
  "_label": None,
  "_need_child": False,
  "_repeat": "replace",
  "_required": False,
  "_show": True,
  "_type": None,
  "_values": None,
  "_xor": None,
}
```

#### Properties Types
**_aliases**: null, string (comma split), or list of strings.  
**_allow_parent_fork**: null, or boolean.  
**_allow_siblings**: null, or boolean.  
**_default**: null, or same type as defined in `_type`.  
**_enabled**: null, or boolean.  
**_examples**: null, string, or list of strings.  
**_fork**: null, or boolean.  
**_hint**: null, or string.  
**_in**: null, string (comma split), list of strings, or dictionary.  
**_info**: null, or string.  
**_label**: null, or string.  
**_need_child**: null, or boolean.  
**_repeat"**: null, or string.  
**_required**: null, or boolean.  
**_show**: null, or boolean.  
**_type**: null, or string.  
**_values**: null, or string.  
**_xor**: null, string (comma split), list of strings (comma split).

#### Properties Explained
**_aliases**: Set aliases for argument. Each argument can have no aliases or unlimited number of aliases. If no aliases are provided or `_aliases=None` then Nargs auto-alias inner function is triggered and create an argument alias automatically. For instance for arg_one, auto-alias is going to set alias `--arg-one` with `Nargs()` option auto_alias_prefix set to `--` and option auto_alias_style set to `lowercase-hyphen`. Arguments' aliases are used on the command-line and arguments' names are used in the code. A valid argument needs to have at least one alias otherwise an error is thrown. If at least one alias is set manually for an argument then auto-alias won't apply to this argument. During alias setup a `default alias` is automatically set. `default alias` is used in a special case [Nargs get_args _get_path](#nargs-get_args). Aliases prefix can any prefix from `"", "+", "-", "--", "/", ":", "_"`. Then alias text must follow regex `[a-zA-Z0-9][a-zA-Z0-9\-_]*?(?<!\-|_)`. The previous regex means:  
- Required next char must be either a lowercase letter, an uppercase letter, or an integer.
- Optional next chars can be any char from lowercase letter, uppercase letter, integer, underscore or hyphen.
- Last optional char can't be an underscore or a hyphen.  

One char alias with or without prefix are a special type of alias that can be set as a flag if conditions are met (see [Concatenated Flag Aliases](#concatenated-flags-aliases)).
```python
# aliases syntax is a string where are aliases are split with a comma
"aliases": "-a,--arg,arg"
"aliases": ["-a" ,"--arg", "arg"]
```

**_allow_parent_fork**: Property allows or denies argument's parent to have more than one branch. If `_allow_parent_fork=False` then Nargs throws an error if argument is present on the command-line and its parent as at least two branches. The property is used for most of the built-in arguments. i.e. for command `prog.py --version`, `prog.py` can be forked when `--version` is present even if `prog.py` has property `fork=True`. This property has not effect on root argument and it is always set to true for root argument.  

**_allow_siblings**: Property allows or denies to use siblings arguments. If `_allow_siblings=False` then Nargs throws an error if argument is present on the command-line and at least one of argument's siblings is present. The property is used for most of the built-in arguments. i.e. when end-user types `prog.py --version`, end-user can't provide any other arguments. This property has not effect on root argument and it is always set to true for root argument.  

**_default**: Property sets argument's default value(s). If `_default` is set and `_type` is None, then `_type` is set to `str`. If `_default` is set and `_values` is None then `_values` is set with number of `_default` values. `_default` type and number of values must match both `_type` and `_values` when `_type` and `_values` have already been set. If `_default` is `None` then it is ignored. If `_values` has been set and minimum of argument's values is optional then Nargs throws an error. If argument is provided on the command-line without a value then the argument default value(s) is/are added automatically. `_default` value(s) must also match `_in` values if `_in` is set. `_default` values must matches any type from `bool`, `float`, `int`, `str`. `_default` values must match type `str` when property `_type` is either `dir`, `file`, `path`, or `vpath`. `_default` can't be set when property `_type` is either `.json`, or `json`, otherwise Nargs throws an error.  

**_enabled**: Property defines if argument and its children arguments are parsed. If set to False then the argument is disabled and not visible in the help. Also all its nested arguments are disabled. If root argument is disabled then Nargs will silently discard end-user command-line arguments and `Nargs.get_args()` will return `None`.  

**_examples**: Property provides argument's command examples. It accepts a string or a list of string. Developer can provide command examples for a particular argument. Argument examples are then printed on the screen if any when end-user types either `--help`, `--examples` or `--usage --examples`.  

**_fork**: Property provides argument's the possibility to duplicate the argument. At start the command-line arguments tree is fully created, then when end-user types an argument on the command-line the argument is activated. To activate an argument means adding it on the command-line (see function activate_arg in get_args.py file for implementation). If argument's property `_fork=True` then argument can be duplicated using argument's branch index notation. `Argument's branch index notation` applies on the command-line and it consists of using the argument alias followed by underscore and an optional index. If only underscore is used, it means create an argument's branch. If index is used then end-user can accurately select a particular instance of an argument. For instance two branches have been created for `arg_one` with command `prog.py --arg-one --arg-one_`. End-user can provide `Argument's branch notation` to get the same result i.e. `prog.py --arg-one_1 --arg-one_2`. Then if end-user wants to go back to first branch it can uses notation underscore with index .i.e. `prog.py --arg-one --arg-one_ --arg-one_1 --arg-one_2`. Here `--arg-one_` means create another branch and `--arg-one_1` means goes back to the first `--arg-one` argument and `--arg-one_2` to the second `--arg-one_` argument. The highest index that can be use is equal to `branches length + 1`. If the highest index is used then a new branch is created. It means that `--arg-one_1` will always work but `--arg-one_2` or greater may not work. `_fork` property applies may also be set to True to root argument. It means that end-user will be able to branch the whole program as many times as needed. i.e.:  
```bash
# here --args is root argument alias
# explicit
prog.py - --arg-one + --args_ - --arg-one + --args_1 - --arg-one
# implicit
prog.py --arg-one --args_ --arg-one --args_1 --arg-one
```

To create a branch means to create a copy of an argument and then to create all its children argument. The duplicated argument is then activated. An argument's branch is composed of an argument and all its children arguments. An argument's branch is not the same as an argument's occurence. An argument's occurence is when an argument is used multiple times in the same branch (see [Properties Explained / `_repeat`](#properties-explained)). i.e. argument's branches can be typed as `prog.py --arg-one_ --arg-one_ or prog.py --arg-one_1 --arg-one_2`. Argument's occurences can be typed as `prog.py --arg-one --arg-one or prog.py --arg-one_1 --arg-one_1 or prog.py --arg-one_2 --arg-one_2`.  

**_hint**: Property provides a short description of the argument's purpose. It accepts a string or a list of strings. `_hint` length is limited to 100 char.  

**_in**: Property sets a list of authorized values for an argument. If `_in` is set and `_type` is None, then `_type` is set to `str`. If `_in` is set and `_values` is None then `_values` is set to 1. `_in` accepts either a list, a string, or a dict:   
- If `_in` is a list then all list values must match argument's `_type`.
- If `_in` is a string then string is comma split to create a list and all list values are cast to match argument's `_type`.
- If `_in` is a dict then dictionary keys must be of type string and they are cast to match argument's `_type`. Dictionary values are labels that must be of type string and are shown in help and usage for end-user. Dictionary keys are returned to the program.  

`_in` can't be set when property `_type` is either `.json`, or `json`, otherwise Nargs throws an error. `_in` matching type is string for `_in` list of values or `_in` dictionary keys when argument's type is either `dir`, `file`, `path`, or `vpath`.  

```python
# _in property syntax
## comma split string
"_in": "building,house",
## list
"_in": [0,1],
## dictionary
"_in": {
  "0": "min",
  "1": "max",
}
## dictionary
"_in": {
  "0": "True",
  "1": "False",
}
```  
**_info**: Property provides the argument's purpose full description. `_info` accepts either a string or a list of strings. `_info` has no length limit.  

**_label**: Property provides a label for argument's values. Label is printed with help or usage commands. `_label` must be a string or null. Label is put to uppercase when set. i.e. if `labels:"fruit"` for argument items with aliases --item then help may print `[--item [<str:FRUIT>]]`. `_label` can't be set when `_in` is present. If `_label` is set:  
- if `_values` is not set, then `_values` is set to 1.
- if `_type` is not set, then `_type` is set to `str`.

**_need_child**: Property defines if usage is printed when children arguments are not provided. If `_need_child` is set to True and argument has children arguments then Nargs throws an error and print usage if argument is present on the command-line and none of its children are present. `_need_child` is set to True by default for root argument only. For other arguments `_need_child` is set to False by default.  

**_repeat**: Property defines argument behavior when end-user types multiple occurences of an argument on the command-line. Unlike `_fork` property that is related to argument's branches number, `_repeat` property is related to argument's occurences number per argument's branches. `_repeat` default value is `replace`. Each time an occurence is added on the command-line the argument property `_count` is incremented (see [Nargs get_args / argument properties / `self._count`](#nargs-get_args)). There are 3 actions for `_repeat` property:  
- **append**: It means that only one argument is kept and each repeated argument's values are appended to a list of values for the argument. In this context, `arg._alias` is set with the latest alias developer input in the terminal.  
- **error**: It means that an error is triggered if the argument has more than one occurence.  
- **replace**: It means that only one argument is kept but for each argument's occurence then argument's values replace the previous argument's occurence values. In this context, the last alias used is the one kept for the argument. If nested arguments have already been selected on the command-line with previous argument's occurence, then nested arguments are cleared. .i.e.: `_repeat:"replace"` means that basically you re-create an argument branch as if it has not already been selected on the command-line.  

**_required**: Property defines if argument is required when end-user adds argument's parent to command-line. If end-user types an argument that has a child argument with property `_required` set to True and end-user does not type the child argument then there are two scenarios:
    - If omitted a required argument is added implicitly with its default alias either:
      -  if argument has no values
      -  if argument has default value(s). In that case default value(s) is/are set.
    - If an omitted required argument has required value(s) with no set default value(s) then an error is thrown.

`_required` property is set to True for root argument only and it can't be changed for root argument. Root argument is always required. `_required` property is set to False by default for all the other arguments.

Argument with property `_required=True` follows certain rules to prevent runtime error due to arguments definition:
- if `_required=True` and argument's name is present in parent `_xor` property then Nargs throws an error.
- if `_required=True` and argument's property `_allow_parent_fork=False` then Nargs throws an error.
- if `_required=True` and argument's property `_allow_siblings=False` then Nargs throws an error.
- if `_required=True` and argument's property `_need_child=True` then Nargs throws an error (This rule does not apply to root argument.).

For an omitted required argument the two scenarios process repeat recursively. It means that an omitted argument is added implicitly and required arguments are searched in added implicit argument's children until no more children are available or no more required arguments are found in children.  

**_show**: Property defines if argument is printed in help, usage and documentation. If set to False end-user and developer can still use the argument but argument won't show either in help, usage, or documentation.  

**_type**: Property sets type argument's value(s). If property `_type` is set and property `_values` is not set, then property `_values` is set to 1. Argument's values are cast to the different types. Multiple types are supported:  

- **bool**: Argument value(s) expected must be of type boolean. Bool is generally a string that is case insensitive and is equal to 'true' or 'false'. If 1 is given then it is interpreted as true. If 0 is given then it is interpreted as false.
- **float**: Argument value(s) expected must be of type float.
- **int**: Argument value(s) expected must be of type integer.
- **str**: Argument value(s) expected must be of type str.
- **dir**: Argument value(s) expected is a relative or absolute path to an existing directory.
- **file**: Argument value(s) expected is a relative or absolute path to an existing file.
- **path**: Argument value(s) expected is a relative or absolute path to either an existing directory or an existing file.
- **vpath**: Argument value(s) expected is a relative or absolute path to an existing or non-existing directory or file.
- **json**: Argument value(s) expected is a JSON/YAML string. String may be single-quoted.
- **.json**: Argument value(s) expected is either a .json/.yaml file or JSON/YAML string that may be single-quoted.
- In types `dir`, `file`, `path`, and `vpath`, relative paths are resolved according to terminal current directory.
- JSON strings can be single-quoted.
- YAML strings or YAML files are discarded if PyYAML has not been installed.

**_values**: Property sets the number of argument's values. An argument's values are first either required or optional and second they have a minimum and a maximum number of values. `_values` can be expressed as:  
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
- if argument's `_default` property is set then values are implicitly added from `_default` property.
- if argument's `_default` property is not set then Nargs throws an error.

**_xor**: Property defines arguments group for current argument children's arguments. Each group contains at least two argument names from current argument's children. `_xor` a.k.a. `exclusive or` allows Nargs to trigger an error when two arguments from the same group are present on the command-line at the same time. Multiple groups can be created. An child argument can't be both in a `_xor` group and have its `_required` property set to `True` at the same time.  
`_xor` notations are:  
```json
    // one group notation
    "_xor": "arg_one,arg_two,arg_three",
     // or one group alternate notation
    "_xor":[
        "arg_one",
        "arg_two",
        "arg_three"
    ],
    // or multiple groups notation
    "_xor":[
        "arg_one,arg_two,arg_three",
        "arg_three,arg_four"
    ],
    // or multiple groups alternate notation
    "_xor":[
        [
            "arg_one",
            "arg_two",
            "arg_three"
        ],
        [
            "arg_three",
            "arg_four"
        ],
    ], 
```

## Built-in Arguments
Nargs provides end-user built-in arguments. Built-in arguments definition is available in Nargs source code at file `src/dev/get_node_dfn.py` in function `add_builtins()`.  

Built-in arguments are available at node level 2. Built-in arguments aliases are set according to Nargs options `auto_alias_prefix` and `auto_alias_style`. It means when developer change these two options then built-in arguments aliases are also modified to match developer aliases style. Some built-in arguments also have a one char alias added programmatically when Nargs parses arguments definition. Built-in one char aliases also match auto_alias_prefix and auto_alias_style. When developer set arguments with same aliases as built-in arguments at node level 2 then built-in arguments aliases are removed silently. A built-in argument that had all its aliases removed silently is also removed from the arguments' tree. It is a way to remove built-in arguments by overloading their aliases. Another way is to provide an empty list or a list without the built-in argument(s) at `Nargs() builtins` option.  

`_cmd_` built-in argument allows end-user to write command-line arguments in a file with newlines, empty lines, indentation, and comments using '#'. `cmd` goal is to overcome terminal command length limitation and/or to allow developer to write commands in a readable way. When command-line is provided through built-in argument `cmd` then the root argument must match its argument's alias(es). Root argument's alias is provided in the arguments definition either implicitly by Nargs auto-alias generation or explicitly by developer through arguments definition. Root argument alias equals `--args` when provided implicitly.  

`_help_` built-in argument generates host program minimum help from Nargs arguments definition and metadata. Users and end-users can print help to terminal with `prog.py --help` or export it in 4 different formats `asciidoc`, `html`, `markdown`, and `text`. A file path can also be provided. i.e.: `prog.py --help --export html --to ../userpath.html`. Help can be printed or exported with arguments `syntax` explained. `--help --syntax` gives end-user the essential information to understand how to read and use Nargs Notation. Help has multiple sections:  
- About Section: It provides metadata information from the program. Metadata is provided implicitly with `gpm.json` and/or explicitly by developer with `Nargs metadata` parameter. The printed fields are all the metadata keys provided to Nargs.
- Usage Section: It provides program's usage. 
- Help Section: It provides program's help.
- Examples Section: It provides all program's examples.
- Nargs Argument Syntax Section. It contains:
    - Nargs module metadata.
    - How to read Nargs syntax.
    - How to type arguments and values in the terminal.

`--help --metadata` prints all program's metadata provided by developer. In order to import metadata Nargs searches first a `gpm.json` file in the program executable root directory. If `gpm.json` file is found then it is used as a based dictionary for Nargs metadata. If `gpm.json` file is not found then Nargs metadata starts with an empty dictionary. Developer can also provide a dictionary through `Nargs(metadata=dict())` parameter and this dictionary is merged into Nargs based metadata dictionary. In other words, Nargs metadata comes first from a gpm.json file if any and then developer metadata is merged into that dictionary and developer metadata overloads any previous similar dictionary key. `--help --metadata` prints metadata keys and values to terminal. Selected key(s) may be provided.  

`_path_etc_` only exists if developer sets `Nargs()` option `path_etc` value. It provides the configuration path of the program.  

`_version_` returns program version if it has been provided into metadata. If not provided into metadata then Nargs throws an error whenever built-in version argument is used.  

`_usage_` built-in argument prints all the arguments in a tree structure with Nargs notation. The nested argument `from_` selects the starting argument and it can be either the current argument or a parent. The printed nested arguments depth can be set with nested argument `depth`. For each printed arguments the following data can be provided: `examples`, `flags`, `hint`, `info`, `path`, and `properties`. For instance end-user can type `prog.py @u@eFhipr`, `prog.py --usage --examples --flags --hint --info --path --properties` or `prog.py --help --usage --depth 1 --from 0 @eFhipr`. Built-in argument `_usage_` is the only built-in argument that can use question mark `?` as an alias. Question mark is very useful but it has a limitation on some systems. For instance on bash terminals, question mark is a bash wildcard and it is going to be replaced by the name of a file or a directory if any directory or file has only one char for name in the current directory.  

## Arguments Explicit Implicit Notation
In order to navigate through the arguments tree, end-user can provide arguments on the command-line by using two notations **explicit notation** and **implicit notation**. There is always a reference argument when using explicit or implicit notation. The reference argument is the current argument. For instance when Nargs starts parsing the command-line the first reference argument is the root argument. Then any other argument provided on the command-line becomes reference argument one after the other following `Nargs().get_args()` parsing the command-line from left to right.  

### Explicit Notation
Explicit notation describes exactly the arguments position in the arguments tree using `+`, `=`, and `-` symbols. Explicit notation is used to exactly select one alias argument from multiple same alias located at different node levels. Explicit notation is optional most of the time and it can be mixed with implicit notation. Explicit notation is required when either:  
- An alias is found multiple times in argument's parents' children.
- An alias is found both in one argument's parent's children and argument's children.  
Explicit notation uses the following syntax before an argument:  
**dash symbol `-`**: It goes down one node level (node level increments). Only one dash symbol can be used before an argument.  
**equal symbol `=`**: It stays on the same level as current arguments for siblings. Only one equal symbol can be used before an argument.
**plus symbol `+`**: It goes up one node level (node level decrements). Unlike `-` and `=` notation, multiple `+` characters can be concatenated for instance `++` or `++++` until the node level reaches 1 maximum (`++` means go up 2 node levels). `+` notation also accepts a positive integer instead of concatenation i.e. `+4` permits to go up four node levels at time.  
After an explicit notation end-user has to provide an argument otherwise Nargs throws an error. When end-user navigates in the arguments tree, end-user goes either up to reach root argument or down to access nested arguments. However node level starts at 1 for the root argument and the node level is incremented for each nested arguments level. Thus there is an inverse relationship between the end-user navigation direction and the node level incrementation.

**Explicit notation pros**:  
- notation describes exactly each argument location in the argument's tree.
- No matter the current argument's location in the arguments tree, all other arguments are reachable on the command-line with explicit notation.

**Explicit notation cons**:  
- It is verbose and thus hard to read.

### Implicit Notation
Implicit notation allows to navigate through the arguments tree without using **dash**, **equal**, or **plus** symbols. Arguments' aliases are searched implicitly in the arguments tree. For instance the root argument does not need to use the `-` symbol for its nested arguments because root argument is the only sibling at level 1. Then for lower node level, explicit notation may be needed. Implicit notation is optional and can be mixed with explicit notation. For a given argument's alias in the terminal, implicit notation follows the rules:  
- Alias is searched in explicit aliases which means current argument's children arguments' aliases.
- Alias is also searched in implicit aliases which means current argument's siblings' aliases, current argument's parents' aliases, and current argument's parents' first children's aliases.
- If the same alias is found multiple times in the search scope then Nargs throws an alias conflict error and ask end-user to explicitly select desired alias.
- For instance end-user needs explicit notation to select chosen alias when chosen alias is both located in current argument's parent argument's aliases and in current argument's child's aliases.
**Implicit notation pros**:  
- Shorter notation.
- Closer to command-line arguments "standard syntax". 
- Developer could set arguments definition for a program where alias never conflict and thus explicit notation may not be needed.
**Implicit notation cons**:  
- It is hard to read even if it is less verbose than explicit notation.
- It is limited because end-user still needs to use explicit notation in specific scenarios.

### Note
Both explicit notation and implicit notation are hard to read for long command-line. It is not specific to Nargs but to any program that accepts command-line. To improve terminal commands readability, Nargs use the following features:  
- [Built-in argument cmd](#built-in-arguments).
- Nargs `cmd` parameter.

### Examples
For definition:  
```yaml
args:
  arg_one:
    _aliases: "-a,--arg-one"
    nested_arg_one: 
      _aliases: "-n,--nested-arg-one"
      nested_nested_arg_one:
        _aliases: "-n,--nested-nested-arg-one"
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

# explicit
main.py - --arg-one = --arg-two
# implicit
main.py --arg-one --arg-two

# explicit notation is needed in some scenarios. 
# implicit creates a conflict here
main.py -a -n -b # -b may be arg_two or nested_arg_two
# explicit 
main.py -a -n + -b # -b selects arg_two
```

## Command-line Values Notation
More information on command-line syntax is available at [Nargs end-user documentation](end-user.md).  

For definition:  
```yaml
args:
  _values: "?"
  arg_one:
    _aliases: "-a,--arg-one"
    _values: "+"
    nested_arg_one:
      _aliases: "-n,--nested-arg-one"
      nested_nested_arg_one:
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
main.py --arg-one=value
main.py --arg-one='value1 value2 "this is value3"'
main.py -a:"value"
main.py -a:'value1 value2 "this is value3"'
main.py --arg-one:value
main.py --arg-one:"value"
main.py --arg-one:'value1 value2 "this is value3"'
```

### Concatenated Flags Aliases

Flags aliases are one char flags aliases with or without prefix that can be used with the at symbol `@` as prefix. i.e. `prog.py @abc` where `a`, `b`, and `c` are different aliases that can be from the same or different arguments.  
Concatenated flags aliases are also called flags set and are always related to a particular argument. Each argument may have its own flags set.  
Related to an argument flags candidates must be implicit arguments or explicit arguments of the reference argument. Flags are defined by the alias char and not the prefix i.e. in alias `/a` only `a` define the flag.  
If two aliases have the same one char and are on the same node level then alias prefix that comes first in the following list `['+', '-', '', '/', ':', '_', '--']` has precedence over the other and it is set as a flag. For instance for two aliases `/a` and `a`. alias `a` is selected has a flag because its prefix `''` comes before `'/'` in the previous list.  
If two aliases have the same one char and are not on the same not level then alias that has the higher node level has precedence over the other alias. It means that explicit arguments' aliases have always higher precedence to be set as a flag than implicit arguments' aliases.  
Flags can be retrieved through built-in usage argument for each argument. Flags can be in any order (except if developer has set a particular sorting order in code.) and they can be added several times. In fact flags are still related to their argument and when typed the same rule applies as if the entire argument was typed. i.e. `prog.py @chu` may be equal to `prog.py -c -h -u`. So it means that some arguments can still exit when typed or values may be required. Or flag argument may not be allowed to be repeated. It all depends on arguments definition. That is why developer should set char aliases in a way that makes sense and that is intuitive for end-user to use them as flags.  
The main purpose of flags is to typed arguments in the shortest way possible. It is really powerfull for developers that type the same command hundreds of times.
Flags are context-sensitive because they are gathered as a set related to the current arg. So it means that the combinations are endless because arguments nesting is virtually endless with Nargs.  
Only the latest flag typed on a set can have values. Not all arguments from the pool of explicit and implicit arguments are available because flags are set according to rules define above.  
Flags does not allow explicit notation so it is not possible to navigate explicitly with that notation.  
Flags does not allow index notation except for the latest flag. So it is not possible to navigate between different occurences of the same argument with flag notation.  
The argument located before the flags set is the reference argument. Flags are defined according to this argument in the arguments tree. When all the flags have been processed the location in the arguments tree is the location of the argument of the latest flag used.  
Flags may be intuitive and easy to remember depending on arguments definition.  
Flags can be located on any node level so flags on lower level may be available to all arguments.  
Multiple at symbols maybe add in a flags set. For instance with command `prog.py @u@pr` there are two flags sets. First flags set is `@u` and is related to `prog.py`. Second flags set is `@pr` and is related to first flags set's last flag `u`. The command could be written like this `prog.py @u @pr` or `prog.py -u -p -r` or `prog.py --usage --properties --path`. Multiple at symbols allows to nest flags set.  

## Nargs Errors Contexts
- **Nargs in definition**: error comes from developer arguments' definition context.
- **Nargs on the command-line**: error comes from end-user command-line arguments context.
- in code arguments context errors are not managed. These errors should be mainly class attributes error. i.e.: `AttributeError: 'CliArg' object has no attribute`.  

## How to Implement Nargs Global Arguments
A global argument is an argument that is available on all node levels of the arguments tree. There is no global arguments in Nargs. Built-in arguments are only available on arguments node level 2. However developer can simulate a global argument by using arguments' implicit notation. For instance starting at current argument if another argument alias is located at node level 2 and no other arguments have the same alias in current argument children or current argument parents then developer can provide argument alias located at node level 2 and it is going to be called as if it was a global argument. Simulating a global argument does not necessarily happens on node level 2, because arguments definition is a tree structure. Thus simulating global arguments can happen on any node level that is higher than current argument or at children node level.  

## How to Implement a Nargs Radio Button Like Argument
A radio button like argument is an argument that provides multiple option and only one can be selected at a time. There are three ways:
- with values using `_in` property. i.e.: `_in="logout,reboot,shutdown,suspend"
- with argument's aliases using `_aliases` property. i.e.: `_aliases="--logout,--reboot,--shutdown,--suspend"`
- with argument's aliases using `_xor` property. i.e.: `_xor="home_server,work_server"

In Definition:  
```yaml
prog.py:
  home_server:
    _in: "logout,reboot,shutdown,suspend"
  work_server:
    leave:
      _aliases: "--logout,--reboot,--shutdown,--suspend"
```

In code for developer:  
```python
# for _in property
if prog.home_server._here:
  if prog.home_server._value == "logout":
    pass
  elif prog.home_server._value == "reboot":
    pass
  elif prog.home_server._value == "shutdown":
    pass
  elif prog.home_server._value == "suspend":
    pass

# for _aliases property
if prog.work_server.leave._here:
  if prog.work_server.leave._alias == "--logout":
    pass
  elif prog.work_server.leave._alias == "--reboot":
    pass
  elif prog.work_server.leave._alias == "--shutdown":
    pass
  elif prog.work_server.leave._alias == "--suspend":
    pass

# for _xor property
if prog.work_server._here:
    pass
elif prog.home_server._here:
    pass
```

On the command-line for end-user:
```shell
# _in property
prog.py --home-server logout

# _aliases property
prog.py --work-server --logout

# _xor property
prog.py --work-server
# or 
prog.py --home-server
```

## Arguments combination logical rules

`_allow_parent_fork`, `_allow_siblings`, `_need_child`, `_repeat`, `_required`, `_xor`

Logical rules for arguments' combinations are enforced first because of the arguments tree structure. Tree structure allows different arguments to share same aliases and still they can't overlap each other. Then there are multiple arguments definition properties that define logical rules: 
- `_allow_parent_fork` prevents or authorize the parent argument to branch when argument is present on the command-line.  
- `_allow_siblings` prevents or authorize argument's siblings when argument is present on the command-line.  
- `_need_child` forces end-user to add at least one children argument when argument is present on the command-line.  
- `_required` main purpose is to allow having arguments added implicitly depending on their values. An argument that has its property `_required` set to false does not necessarily means that the argument is optional. Nargs only defines a tiny subset of most used logical arguments' combinations. Developer is the one who codes the program arguments logical rules in code section. When a `_required=False` argument is still mandatory in code's logic then developer may add that information in the `_info` property of the argument to let end-user knows about it.  
- `_repeat` defines the behavior of multiple argument's occurences on the command-line.  
- `_xor` main purpose is to be able to simply let the end-user knows that only one argument or another can be present at the same time.

Nargs can't describe all arguments logical rules, if it could it would be too verbose to display on terminal or in a documentation and it would probably be a duplicate of developer arguments in code implementation. Developers do not need to rely on arguments definition's properties to set the logic of the application. All the logic can be set in code context. Logical rules are syntactyc sugar that provides a rapid development solution for most of the cases.   
