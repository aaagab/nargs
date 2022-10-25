# NARGS DEVELOPER DOCUMENTATION

There are two documentation files:
- [Nargs developer's documentation](developer.md) is for developers who create programs that use Nargs as a module. 
- [Nargs end-user's documentation](end-user.md) describes Nargs command-line syntax to interact with programs using Nargs as a module.

## Table of Contents
- [Specifications](#specifications)
- [Why Nargs?](#why-nargs)
- [Get Started](#get-started)
- [Glossary](#glossary)
- [Nargs Class](#nargs-class)
    - [Nargs \_\_init__](#nargs-init)
    - [Nargs Class Members](#nargs-class-members)
        - [Nargs dfn](#nargs-dfn)
            - [NodeDfn Class Members Explained:](#nodedfn-class-members-explained)
        - [Nargs get_documentation](#nargs-getdocumentation)
        - [Nargs get_metadata_template](#nargs-getmetadatatemplate)
        - [Nargs get_default_theme](#nargs-getdefaulttheme)
        - [Nargs get_args](#nargs-getargs)
    - [Developer Custom Help and Usage](#developer-custom-help-and-usage)
- [Arguments Definition](#arguments-definition)
    - [Arguments Properties with Default Values:](#arguments-properties-with-default-values)
        - [Properties Summary](#properties-summary)
        - [Properties Explained](#properties-explained)
- [Built-in Arguments](#built-in-arguments)
- [Arguments Explicit Implicit Notation](#arguments-explicit-implicit-notation)
    - [Explicit Notation](#explicit-notation)
    - [Implicit Notation](#implicit-notation)
    - [Note](#note)
    - [Examples](#examples)
- [Command-line Values Notation](#command-line-values-notation)
    - [Concatenated Flag Aliases](#concatenated-flag-aliases)
- [How to Implement Nargs Global Arguments](#how-to-implement-nargs-global-arguments)
- [How to Implement a Nargs Radio Button Like Argument](#how-to-implement-a-nargs-radio-button-like-argument)
- [Arguments combination logical rules](#arguments-combination-logical-rules)
- [Loading Definition Performance](#loading-definition-performance)

## Specifications
- Nargs has 3 contexts: 
  - Arguments' definition, command-line arguments, and in code arguments.
- Arguments' definition is set with a JSON file, a Python dictionary, or a YAML file.
  - JSON definition file and Python dictionary can have their nodes arguments duplicated with `@` notation.
  - Definition is cached to JSON file to improve Nargs arguments' definition loading.
  - Definition can also be retrieved from cache only.
- Built-in command-line Arguments (cmd, help, path_etc, usage, version).
- Built-in arguments usage and help are color themeable.
- Multiple arguments aliases prefixes: `"", "+", "-", "--", "/", ":", "_"`.
- Concatenated flag aliases i.e. `-123aAbBcC`. 
- Flags are context-sensitive.
- Built-in usage argument can provide details on available flags for each argument.
- Command-line arguments form a tree where each node may have multiple branches.
- Arguments branches may be duplicated with branch index notation i.e. `prog.py --arg+ --nested --arg+ --nested`
- Arguments aliases are automatically set if not defined according to default prefix and default alias style.
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
  - explicit: `main.py + --arg = --sibling-arg`
  - implicit: `main.py --arg --nested-arg --sibling-arg`
  - explicit: `main.py + --arg + --nested-arg - --sibling-arg`
- Multiple same argument occurrences may be defined:
  - `_repeat="append"` appends values to the same argument when repeated.
  - `_repeat="error"` triggers an error when argument is repeated.
  - `_repeat="replace"` resets and replace previous argument's branch and values if any.
- In code Nargs returns a CliArg class object that has for members argument properties and nested arguments objects. Arguments can then be accessed:
  - Dynamically with their name in a dictionary
  - With their name as a class member.
  - From a list that follows the order they have been selected.
- In code all arguments are available to developer, even the ones non provided on the command-line.
- On the command-line Nargs allows variable placeholders that may be substituted by environment variables.
- Auto-generated documentation from definition file, that can be printed to the terminal or exported in the following formats: asciidoc, html, markdown, and text.
- Auto-generated documentation may include [Nargs end-user's documentation](end-user.md).
- Typed argument's values:
  - Standard types: `bool, float, int, str`.
  - File types: `dir, file, path, vpath`.
  - JSON/YAML types: `.json, json`
- Logical rules may be set to arguments by using arguments' definition properties `_allow_parent_fork`, `_allow_siblings`, `_need_child`, `_repeat`, `_required`, `_xor`.

## Why Nargs?
- Nargs prevents end-users from guessing program arguments' combinations. A descriptive error is triggered for each wrong argument or each wrong argument's values.
- Nargs auto-generated documentation, built-in help, and built-in usage ensure that program's core documentation is provided out of the box.
- Nargs empowers users by providing them a notation for infinite arguments nesting.
- Nargs notation follows command-line arguments' notation standard practice with its implicit arguments' notation.  
- Nargs can be used to easily wrap existing command-line programs. It provides them all the Nargs bells and whistles from auto-generated documentation, arguments error checking, auto-aliases, multiple-forms aliases, ...
- Nargs built-in arguments ensure that programs provide a consistent argument set for program identification with cmd, help, usage and version.

## Get Started
**Context: Arguments' definition. Developer creates arguments' definition with either**:  
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
```

In arguments' definition, argument's properties start with underscore and argument's children start with either an uppercase letter or a lowercase letter.  

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
args=Nargs(options_file="nargs.yaml", metadata=dy).get_args()
# or
args=Nargs(options_file="nargs.json", metadata=dy).get_args()
# or
args=Nargs(args=args, metadata=dy).get_args()

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
program.py + --arg-one + --nested-arg-one
program.py + --arg-two + --nested-arg-two value1 value2 "value 3" - --arg-one
program.py + --arg-two="value1 value2 \"value 3\"" + --nested-arg-two

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
- **arguments**: In code arguments are objects from Nargs CliArg class. In definition arguments are tree nodes with properties and child arguments. On the command-line arguments are selected by typing their aliases.  
- **arguments node level**: Arguments are defined with a tree structure where executable (i.e.: `main.py`) is generally the root argument. Nested arguments can be defined at will from the root argument. Each argument is on a node level. Root argument is node level 1, then its children are on node level 2, and node level continues incrementing if more children of children are added.  
- **arguments aliases**: End-user calls arguments on the command-line with arguments' aliases. For a given argument `arg_one` aliases may be `--arg-one, -a, argone, arg-one`. Arguments' aliases are only unique at their node level.  
- **arguments names**: An argument name is a string chosen by developer to identify an argument at the argument's node level in the arguments' definition tree. An argument's name is unique at its node level between siblings' arguments names. Argument's name is later used in code by developer to set program's logic.  
- **arguments branches**: An argument's branch consists of both the argument and all its children. A new argument's branch consists of both a new instance of the argument and new instances of its children. Argument's branches are independent. It means that when an argument's branch is modified, it does not modify any other branches of the same argument.  
- **command-line**: It is the end-user's terminal command-line from `sys.argv`, developer providing a command-line string with Nargs get_args `cmd` option, or end-user providing a command-line with Nargs built-in `cmd` argument value.  
- **Nargs Arguments' contexts**:
    - **command-line arguments**: Arguments are provided through the command-line i.e. `program.py --my-argument my_value my_other_value --my-other argument`. Any command-line syntax errors trigger Nargs exception `EndUserError`.
    - **arguments' definition**: Arguments are defined in a JSON file, YAML file, or a Python dictionary. i.e. `{"args": {"arg_one": {"nested_arg":{}}}}`. Any definition syntax errors trigger Nargs exception `DeveloperError`.
    - **in code arguments**: It generally refers to `main.py` file. It is where developer writes program's logic using arguments. i.e. `if root.arg_one.nested_arg._here:`. Common developer errors are wrong argument names that do not match definition. i.e. class attributes error `AttributeError: 'CliArg' object has no attribute`.
- **Root argument**: It is the command-line's first argument or the calling program name with or without path. It starts the cmd. i.e.: in cmd `dev/prog.py --arg-one` root argument is `dev/prog.py`  
- **options** and **properties**: Options are related to Nargs class `__init__` keyword arguments. Options are parameters that developers can change in order to modify Nargs default global options. Properties are related to arguments. Properties can be related to CliArg class (command-line arguments) or NodeDfn class (arguments' definition). For CliArg class properties are CliArg class members that are not functions. For NodeDfn class properties are mainly listed in the class member `dy` that returns a properties dictionary.
- **Current argument**: Current argument is a command-line argument `CliArg`. Every time end-user types a command-line argument then this argument becomes the current argument. Current argument defines what other arguments or values can be added on the command-line. For instance when Nargs throws a command-line syntax error current argument is the reference argument to locate and to describe the issue.

## Nargs Class
```python
class Nargs():
  def __init__(self,
    args=None,
    auto_alias_prefix="--",
    auto_alias_style="lowercase-hyphen",
    builtins=None, # if None then it is set with dict(cmd=None, help=None, path_etc=None, usage=None, version=None),
    cache=True,
    cache_file="nargs-cache.json",
    metadata=None, # if None then it is set with dict(),
    options_file=None,
    only_cache=False,
    path_etc=None,
    pretty_help=True,
    pretty_msg=True,
    raise_exc=False,
    substitute=False,
    theme=None, # if None then it is set with dict(),
  ):
    self.dfn

  def get_args(self, 
    cmd=None,
  ):
    return args

  def get_default_theme():
    return dict()

  def get_documentation(self, output, filenpa=None, wsyntax=None, overwrite=False, only_syntax=False):
    return str

  def get_metadata_template():
    return dict()
```

**WARNING**: Nargs class attributes starting with an underscore are either internal fields or internals functions and developer should ignore them. Internal attributes may be changed at any time without being considered a breaking change. Internal attributes are also not documented.  

### Nargs \_\_init__

- **args**: This option provides arguments' definition to Nargs. `args` accepts a dict (see also [Arguments Definition](#arguments-definition)).
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
- **cache_file**: This option provides a file path to cache Nargs options. Default value is `nargs-dump.json`.  Cache file path can be relative or absolute. Relative path is relative to `Nargs()` class caller file path. Developer can choose either `.json` or `.pickle` extension to cache Nargs options once they have been parsed. There are 3 main elements that are checked to recreate the cache file: options provided with Nargs(), gpm.json file for metadata, and an options file. If any of these three elements are modified then the cache file is recreated. If cache file already exists, and none of the three elements have been modified then Nargs options are extracted from the cache file instead of being parsed with Nargs module. Caching improves speed when parsing because it allows having all the options and arguments' definition grammar checked only once. JSON format is the safest (1.5 to 2 times faster) and PICKLE format is the fastest because unlike JSON cache, arguments' definition objects are already stored in the PICKLE cache. However PICKLE files may be compromised, and arguments' definition tree size is limited to approximately 850 nodes before throwing a `Recursion Error`.  
- **metadata**: This option accepts a dictionary that helps populating built-in arguments, usage, help, and version. Developer can get common metadata fields with Nargs function `Nargs.get_metadata_template()`. Any metadata field that is null or empty is discarded. Provided fields are trimmed. Program fields `name` and `executable` are mandatory, and they need to be provided in metadata parameter i.e. `Nargs(metadata=dict(name="My Program", executable="prog"))`. Nargs class member metadata is set and available to developer with `Nargs().metadata`  (see also [built-in arguments](#built-in-arguments))   
- **only_cache**: This option allows to load the cache_file definition without checking changes on the developer provided definition. Parsing speed should be the fastest when only_cache is set to True. If the cached definition returns null Nargs throws an error and prevents the cache_file to be regenerated. If that error happens developer can regenerate the cache by either manually deleting the cache file or by setting only_cache to False.  
- **options_file**: This option allows to provide all the Nargs options from a file. It is the preferred method to provide `args` option. options_file must be a `.json/.yaml` file path (relative or absolute). Relative path is relative to `Nargs()` class caller file path (see also [Arguments Definition](#arguments-definition)). When Nargs is executed, options are first read from `Nargs()` options and then if options file is provided then options file options overload previously defined similar options. `options_file` can be omitted. In order to use `.yaml` options file, developer and end-user needs to `pip install pyyaml`. PyYAML import statement is only triggered if a YAML file is provided. In other words users only using JSON definition file do not need to install PyYAML. Only safe_load is used to parse a YAML options file. YAML file parsing is much slower (at least 4 times) using PyYAML 5.4.1 safe_load, than parsing JSON file, according to a performance's tests. However Nargs options are cached so a slower parsing time for options YAML file only appears once before it is cached. YAML is the preferred format to write options file because of its shorter syntax and commenting capabilities. Options can be provided in four ways:  
    - from `Nargs()` in code context (all options).
    - from an option file which path is available through `Nargs option options_file` (all options).
    - from a `.nargs-user.json` or `.nargs-user.yaml` file located in nargs launcher directory (limited user options see [Nargs end-user's documentation](end-user.md)).
    - from a `.nargs-user.json` or `.nargs-user.yaml` file located in nargs path_etc directory if any (limited user options see [Nargs end-user's documentation](end-user.md)).  

The four ways to provide options cascade on top of each other and replace previous similar options. The precedence order from lowest precedence to highest precedence is `Nargs()`, `options_file.json`, `options_file.yaml` (options_file name can be any name), `.nargs-user.json` in launcher directory, `.nargs-user.yaml` in launcher directory, `.nargs-user.json` in path_etc directory, `.nargs-user.yaml` in path_etc directory.  
For options_file, and users file, if they provide both `.json` and `.yaml` files then for each of the location only the `.yaml` file is parsed.  

- **path_etc**: Developer can provide the application configuration directory with this option. If `path_etc` is provided and it is also present in `builtins` then a built-in argument `path_etc` is created to allow end-user to get the application configuration path i.e. `myprog.py --path-etc`.  
- **pretty_help**: If set to True usage and help are printed with ANSI escape sequences formatting in terminal as set by default theme or developer theme.  
- **pretty_msg**: If set to True system message are printed with ANSI escape sequences formatting in terminal.  
- **raise_exc**: If set to True Nargs raise Exception for each known errors. If set to False Nargs print an error message for each known errors and exit. `raise_exc=True` may be useful when testing Nargs software or if developer creates custom help and usage commands. There are two custom exceptions returned by Nargs:
    - `EndUserError`: Only happens when a command-line is provided to `get_args` either through `sys.argv` or `get_args cmd option`. These errors are not Nargs errors, but they are command syntax errors provided on the command-line by end-user.
    - `DeveloperError`: Only happens when developer either provides syntax errors on Nargs options or syntax errors on arguments tree definition.  
    - All other exceptions are not expected and may be due to Nargs bugs, cache tampering, or modifications of the Nargs NodeDfn objects when using multiple get_args call. Nargs have multiple tests that covers all the expected errors and most the implementation. Tests are only available with the Nargs sources. Tests are not included for production releases. Tests files are listed in `src/__init__.py`.  

- **substitute**: This option sets Nargs `substitute` mode to True or False. If `substitute=True` command-line strings that match regex `(?:__(?P<input>input|hidden)__|__((?P<input_label>input|hidden)(?::))?(?P<label>[a-zA-Z][a-zA-Z0-9]*)__)` may be substituted either by developer input or environment variables values. Regex rules are:
    - strings start with double underscore
    - strings finish with double underscore
    - After underscore string starts with a single letter (uppercase or lowercase), the word `input` or the word `hidden`.
    - If string starts with word either input or hidden:
        - end-user is prompted to provide a value and string is substituted on the command-line with typed value.
        - If colon and label is provided after word either input or hidden (i.e. `__input:username__`) then prompted text is going to be set with label value. Label value starts with a single letter then optional next characters are either letters (uppercase or lowercase) or numbers.
    - If string does not start with either input or hidden then string must start with a single letter then optional next characters are either letters (uppercase or lowercase) or numbers. In that case string without underscores is substituted with value of any matching environment variable names if any without underscores.
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
- **theme**: This option accepts a style dictionary to style command-line help, command-line usage and help documentation when exported to html (see [Nargs get_default_theme](#nargs-getdefaulttheme), [Nargs get_documentation](#nargs-getdocumentation)).  

### Nargs Class Members

#### Nargs dfn
`Nargs.dfn` is the arguments tree definition root node. It is an instance of NodeDfn class. Each argument on the command-line is an instance of CliArg class. A CliArg instance always have a `self._dfn` member that comes from `Nargs.dfn`. `Nargs.dfn` is mainly used internally to create Nargs help and usage, and it is only needed if developer wants to create its own help and usage or if developer wants to retrieve arguments properties.  
```python
class NodeDfn():
    def __init__(self):
        self.current_arg
        self.dy
        self.dy_nodes
        self.dy_xor
        self.explicit_aliases
        self.implicit_aliases
        self.is_root
        self.level
        self.location
        self.name
        self.nodes
        self.parent
        self.root

    def get_dy_flags():
        return self._dy_flags
```
##### NodeDfn Class Members Explained:
- `self.current_arg`: This member returns the default CliArg object for the definition node. Nargs always creates at least one CliArg object for each definition node. It allows developer to check any command-line argument i.e. `nargs.dfn.current_arg._here is False` (check for CliArg root argument) or `nargs.dfn.current_arg.dy_nodes['child_arg']._here is False` (check for child argument with name `child_arg`).  
- `self.dy`: This member returns a dictionary with all the arguments property. All the properties are generated from the arguments' definition tree provided by developer (see [Arguments Definition](#arguments-definition) and [Properties Summary at column NodeDfn().dy keys](#properties-summary)).
- `self.dy_nodes`: This member returns a dictionary with child argument names as keys and child argument NodeDfn object instance as value.
- `self.dy_xor`: This member returns a dictionary with child NodeDfn object instances as keys and for values xor group numbers with the other child xor nodes i.e.:
```python
{<src.dev.nodes.NodeDfn object at 0x7f94d49863c8>: {'1': [<src.dev.nodes.NodeDfn object at 0x7f94d4f05898>],
                                                    '2': [<src.dev.nodes.NodeDfn object at 0x7f94d4a52e10>]},
 <src.dev.nodes.NodeDfn object at 0x7f94d4a52e10>: {'2': [<src.dev.nodes.NodeDfn object at 0x7f94d49863c8>]},
 <src.dev.nodes.NodeDfn object at 0x7f94d4f05898>: {'1': [<src.dev.nodes.NodeDfn object at 0x7f94d49863c8>]}}
```
- `self.explicit_aliases`: It returns a dictionary with explicit arguments' aliases as keys and their related NodeDfn instance as values. i.e. for root argument:
```python
{'?': <src.dev.nodes.NodeDfn object at 0x7f312fed1f98>,
 'arg1': <src.dev.nodes.NodeDfn object at 0x7f3130001978>,
 'arg2': <src.dev.nodes.NodeDfn object at 0x7f3130370240>,
 'arg3': <src.dev.nodes.NodeDfn object at 0x7f312fed1ef0>,
 'u': <src.dev.nodes.NodeDfn object at 0x7f312fed1f98>,
 'usage': <src.dev.nodes.NodeDfn object at 0x7f312fed1f98>}
```
- `self.implicit_aliases`: It returns a dictionary with explicit arguments' aliases as keys and for each key a NodeDfn instance is provided as value. Implicit alias is searched in current parent child, then it goes up one parent and repeat the process until reaching root node. i.e. for root argument's child argument arg1:
```python
{'?': <src.dev.nodes.NodeDfn object at 0x7f8d8dfbe9e8>,
 'arg1': <src.dev.nodes.NodeDfn object at 0x7f8d8df78e80>,
 'arg2': <src.dev.nodes.NodeDfn object at 0x7f8d8e0dd550>,
 'arg3': <src.dev.nodes.NodeDfn object at 0x7f8d8dfbefd0>,
 'args': <src.dev.nodes.NodeDfn object at 0x7f8d8dfbeb38>,
 'u': <src.dev.nodes.NodeDfn object at 0x7f8d8dfbe9e8>,
 'usage': <src.dev.nodes.NodeDfn object at 0x7f8d8dfbe9e8>}
```
- `self.is_root`: It returns if NodeDfn node is at the top of the arguments' definition tree.  
- `self.level`: It returns the arguments tree node level. It starts at 1 for root argument then it increments by 1 for each child.  
- `self.location`: It returns all the argument name plus all its parents name separated by `>` i.e. "args > arg1 > nested". It is mainly used when checking definition error when generating the cache.  
- `self.name`: It returns the argument name.
- `self.nodes`: It returns argument's child NodeDfn instances.
- `self.parent`: It returns argument's parent NodeDfn instance.  
- `self.root`: It returns arguments tree definition root node.
- `def get_dy_flags()`: It returns a dictionary with for keys one char flag and for values a dictionary with the related NodeDfn object and the related char alias. i.e.:
```python
{'?': { 'node':<src.dev.nodes.NodeDfn object at 0x7f3fd0fbfcf8>, 'alias': '?'},
 'u': { 'node':<src.dev.nodes.NodeDfn object at 0x7f3fd0fbfcf8>, 'alias': '-u'}}
```

#### Nargs get_documentation
`Nargs().get_documentation()` allows to get the documentation in multiple formats. `get_documentation()` returns formatted help as a string, excepts for `cmd_usage`, and `cmd_help`. `output` parameter sets the output format, and it can have one of the following values:
- "asciidoc": returns help string in ASCIIDOC format.
- "cmd_help": print help to the terminal.
- "cmd_usage": print usage to the terminal.
- "markdown": returns help string in MARKDOWN format.
- "html": returns help string in HTML format.
- "text": returns help string in text format.

If a file path is provided to `filenpa` parameter and output is not `cmd_usage` or `cmd_help` then help is going to be written to that file. If `overwrite=True` and output file already exists then it is overwritten silently. If `overwrite=False` and output file already exists then Nargs throws and error. If `wsyntax=True` then Arguments' help syntax cheat sheet is appended to the help see [Nargs end-user's documentation](end-user.md). If `wsyntax` is None then it is set to False. The cheat sheet provides end-user a thorough description of Nargs syntax for help and usage. `Nargs().get_documentation()` is also provided through Nargs built-in arguments:  
- `--usage` for `cmd_usage`
- `--help` for `cmd_help`
- `--help --export` with `asciidoc`, `html`, `markdown` or `text` for the different export formats. i.e.: `prog.py --help --export html --to documentation.html --syntax`  
If `only_syntax=True` then get_documentation return only [Nargs end-user's documentation](end-user.md).  
`Nargs().get_documentation()` provides minimum documentation data even when arguments' definition is either empty or disabled.  

#### Nargs get_metadata_template
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

Note: metadata `executable` is provided by the developer, by `gpm.json alias field`, or by `sys.argv[0]` path basename. If developer provides common fields, then common fields type must match. When common fields are provided they populate About section generated by built-in argument `_help_`. Metadata can be retrieved by end-user using the built-in argument `--help --metadata` (see also [Built-in arguments](#built-in-arguments)).  

#### Nargs get_default_theme
`Nargs.get_default_theme()` returns default built-in theme dictionary.  

Each dictionary key is an element name that can be themed. Each element name accepts a dict with the following properties:  
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
Developer can customize command-line help, command-line usage and html exported help by modifying properties values for the different style elements and providing them to Nargs with `Nargs(theme=user_theme)`. If developer does not provide a theme, then a built-in theme is provided. Built-in theme uses colors from `David Liang wombat256.vim's theme`. If developer wants to style the theme, developer does not need to provide all style elements, nor all the properties. For instance when developer add a style element in its theme dictionary then theme style element is automatically set with non-initialized values. Then for each developer style elements' properties developer's values are set. i.e. developer theme may be:
```json
// "user_theme"
{
    "examples": {
        "bold": true,
        "foreground": "#123456"
    },
    "headers": {
        "underline": true,
        "background": "123;456;789",
    }
}
```
`bold, italic, and underline` style element properties accept a Boolean value.  
`background and foreground` style element properties accept a string value that must be a hexadecimal color (hash pound optional) or a RGB color split with semi-colon.  
`Nargs(theme=dict())` is disabled on the command-line when `Nargs(pretty=False)`.  

Theme is only used for output format `cmd_usage` (if pretty is True), `cmd_help` (if pretty is True), `html`. Other formats like `asciidoc`, `markdown`, and `text` do not rely on theme. `html` format has global CSS rules that are hard-coded and can only be modified manually by the developer in the exported help i.e.:`body { background-color: #2b2b2b;}`.  

#### Nargs get_args
`Nargs.get_args()` returns the root command-line argument node for developer to create in code logic.  
**cmd**: It is provided implicitly from end-user typing arguments on the command-line, explicitly from developer providing Nargs cmd parameter, or implicitly from end-user providing Nargs built-in cmd. When `Nargs().get_args()` cmd parameter is provided either explicitly from developer providing Nargs cmd parameter or implicitly from end-user providing Nargs built-in cmd then root parameter must be provided with one of its argument alias. Argument's aliases are either explicitly provided by developer in arguments' definition or implicitly automatically generated by Nargs. In order to know root argument aliases, usage can be printed by either end-user or developer. When end-user types arguments on the command-line, `cmd` is provided implicitly with `sys.argv` and the root argument is the first argument of the command-line. When `cmd` is provided by `sys.argv` then the first occurrence of root argument does not need to match the root argument's alias. In this context root argument matches the name of the executable that launches the program i.e. `program.py`. `Nargs().get_args()` can be used multiple times with different command-lines. If get_args is called more than once then for each new call the arguments tree is reset. If developer modifies the arguments tree when setting-up program's in code logic then unexpected behavior may happen when using `get_args()` multiple times.  

For each argument on the command-line Nargs create a CliArg object with `argument's children` and `argument's properties`.  
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
- a shorter in code notation for developer. For instance to test the presence on the command-line of a deeply nested argument could be written this way: `rootArg.nestedArg.nestedArg.nestedArg.nestedArg._here`.

**argument children** are all CliArg class members that allow accessing child arguments. Nargs parses the arguments' definition and a CliArg object is created for each child argument. CliArg object children are added dynamically if any. Nargs uses `setattr()` to add child arguments as class members. It allows developer to type arguments in code context as if arguments were a nested namespaces. i.e.: `root_arg.arg_one.nested_arg_one._here`. child arguments class member names start with either an uppercase letter or a lowercase letter. child arguments class member always returns the first branch of the related child argument.  

**argument properties** are all CliArg class members that are not a child argument. An argument property starts with an underscore:  
- `self._`: It is a dict that permits dynamic access to argument's children. `self._ dict` is filled with CliArg child arguments names as keys and CliArg child arguments objects addresses as values. `self._` always returns the first branch of a child argument.  
- `self._alias`: It is set with end-user argument's alias as provided on the command-line for latest argument's occurrence.
- `self._aliases`: All arguments' aliases set in argument's definition.  
- `self._args`: It is a list that contains all child arguments that have been provided on the command-line in the order they have been provided. It may be useful to developer for in code context when end-user provided arguments' sorting order matters. When multiple occurrences per branch of an arg is allowed with argument's definition properties `_repeat="append"` or `_repeat="replace"` then for each new occurrence argument object is removed from `self._args` and appended again in `self._args` from parent argument. For `_repeat="append"` then the same object is appended and for `_repeat="replace"` then a new argument object is appended.  
- `self._branches`: This property returns a list that contains all branches of a command-line argument. At least one arguments branch starting at root argument is generated when `Nargs()` is executed, and that tree is regenerated each time `get_args()` is called more than once. It means that all arguments are already available in code for developers even if they are not present on the command-line. For instance argument's attribute `_branches` returns at least itself (CliArg object address) even if it is not on the command-line. When an argument is added on the command-line and it is the first time it is added then the argument is `activated`. Activated means that some arguments attributes are set. For instance `self._here` is set to `True`, and its parent if any has its attribute `_args` appended with the added argument object (see `set_arg()` in `src/dev/get_args.py`). If argument definition properties `_fork=True` and `_repeat="append"` then when argument is added on the command-line for the first time the argument branch already exists, so it does not need to be created.  For each argument new branch, a new argument is created and all its children too. Then again the argument is activated, and the argument object is appended to its property `_branches`. `_branches` property is a list that is shared between all the branches of the same argument. It is important to note that related branches of an argument share the same parent. For instance if argument's parent has also its `_fork` property that is set to True then the same child arguments from definition args tree may have a different parent in the command-line args tree and thus the same arguments from definition may have branches that are not related to each other because they don't share the same parent. That is why in order to loop through all the arguments added to the command-line arguments tree it is important to loop through arguments starting from the root argument branches and then for each branch going down to each children branches.  
```python
# branches examples
root_arg=pkg.Nargs(options_file="../definition.yaml")

# simple looping through some child arguments available on the command-line
for branch_arg in root_arg._branches:
    for child_arg in branch_arg._args:
        print(child_arg._name)

# alternative
for branch_arg in root_arg._branches:
    for child_name in branch_arg._:
        child_arg=branch_arg._[child_name]
        if child_arg._here is True:
            for child_branch_arg in child_arg._branches:
                print(child_branch_arg._name)

# looping through all arguments available on the command-line with recursion
def process_args(arg):
    print(arg._name)
    for child_name in sorted(arg._):
        child_arg=arg._[child_name]
        if child_arg._here is True:
            for branch_arg in child_arg._branches:
                process_args(branch_arg)
## then call it that way
for branch_arg in arg._root._branches:
    process_args(branch_arg)

# looping through all arguments available on the command-line with recursion (alternative)
def process_args(arg):
    print(arg._name)
    for child_arg in arg._args:
        process_args(branch_arg)
## then call it that way
for branch_arg in arg._root._branches:
    process_args(branch_arg)

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

# looping through all arguments' definition
def process_dfn(dfn):
    print(dfn.name)
    for child_dfn in dfn.nodes:
        process_dfn(child_dfn)
## then call it that way
process_dfn(arg._root._dfn)

# nonrelated branches for child_arg, child_arg._branches with parent root_arg._branches[0] are not related to child_arg._branches with parent root_arg._branches[1]
root_arg (branch 1)
  child_arg (branch 1)
  child_arg (branch 2)
  child_arg (branch 3)
root_arg (branch 2)
  child_arg (branch 1)
  child_arg (branch 2)
  child_arg (branch 3)
# on the command-line the below structure could be written this way
prog.py --child-arg+1 --child_arg+2 --child_arg+3 --args+2 --child-arg+1 --child_arg+2 --child_arg+3
# note (according to previous command-line):
## in code
args.child_arg # always returns args.child_arg._branches[0]
args._["child_arg"] # always returns args.child_arg._branches[0]
### other branches can be accessed with notations:
args.child_arg[1] # for second branch
args._["child_arg"][3] # for third branch

```
- `self._cmd_line`: Only root argument on branch 1 (a.k.a. `root_arg._branches[0]`) has this attribute and it contains the command-line provided to Nargs. To retrieve command-line developer can do `print(arg._root._branches[0]._cmd_line)`.
- `self._cmd_line_index`: It provides the command-line index of the argument location on the command-line for latest argument's occurrence. To print command-line for an argument developer can do `print(arg._root._branches[0]._cmd_line[arg._cmd_line_index])`. Implicit argument's command-line index is always the last explicit argument command-line index (see [Nargs get_args /`_implicit`](#nargs-getargs)). The command-line index number represents the last index of the argument alias plus one. It allows to print the alias related argument command-line with `print(arg._root._branches[0]._cmd_line[:arg._cmd_line_index])`.  
- `self._count`: It returns the number of argument's occurrences on the command-line per argument's branches. It is related to argument's property `_repeat` (see [Properties Explained /`_repeat`](#properties-explained)).  
- `self._default_alias`: Default alias is automatically generated, and it is used either with `_get_path()` function or when adding implicitly a required argument. Default alias is the first alias provided by developer in arguments' definition with property `_aliases`.
- `self._dy_indexes`: It provides a dictionary with one key `aliases` and another key `values`. `self._dy_indexes["aliases"]` is a dictionary that have for keys command-line indexes as int and for values arguments aliases. This dictionary allows to know the command-line index and alias used for each occurrence of an argument. `self._dy_indexes["values"]` is a command-line indexes list for each argument values. The main purpose of `self._dy_indexes` is for developers to be able to throw errors with the exact location on the command-line of an argument alias(es) or one of its values. Implicit argument provides the argument's default alias, and command-line index is always the last explicit argument command-line index. Implicit argument default values are added implicitly but no indexes are added to `self._dy_indexes["values"]` (see [Nargs get_args /`_implicit`](#nargs-getargs)).  
- `self._here`: It defines if an argument is present on the command-line (a.k.a. activated argument). Nargs generates the whole CliArg arguments tree at once. It means that all command-line arguments are always available to developer for in code logic. However having an argument available does not mean it is present on the command-line. That is why property `_here` is needed to allow determining if an argument is present on the command-line. i.e.: `if root_arg.arg_one._here is True:`  
- `self._implicit`: It is set to True if argument has been added implicitly (see [Properties Explained /`_required`](#properties-explained)). It is set to False if argument has been provided on the command-line.  
- `self._name`: It is the name of the argument as set in the arguments' definition.
- `self._dfn`: This is the related definition node for the current command-line argument node. This node gives access to the arguments' definition tree. `NodeDfn` class is available at `src/dev/nodes.py`. Most of Nargs internals rely on that definition tree. Developers maybe want to use the NodeDfn class attribute `dy` to access all the CliArg properties i.e.: `pprint(args._dfn.dy)`. Other class members may be useful if developer wants to generate its own help and usage. In order to overload the built-in help and usage, developer must set Nargs option `raise_exc` to `True` and he or she must disable at least help and usage built-in arguments with Nargs option `builtins`. Then developers is going to create the needed arguments in a definition file. Then developer is going to be able to filter Nargs exceptions `EndUserError` and `DeveloperError`. Most of developers will probably want to rely on built-in help and usage and thus they may want to ignore `self._dfn`. For developers who want to overload help and usage, they may read the `src/dev/help.py` sources as a reference. Creating help and usage, consists in recursively looping through the definition tree and to display information mainly with `node_dfn.dy` (see also [Properties Explained /`_is_usage`](#properties-explained) to set the usage node for custom usage or [Developer custom Help and Usage](#developer-custom-help-and-usage) for an example).  
- `self._previous_dfn`: This attribute is set to None for all arguments except if argument has property `_is_usage` set to True. When argument has property `_is_usage` set to True and argument is provided on the command-line then its attribute `_previous_dfn` holds previous command-line argument `NodeDfn` object. This is useful when developers create his or her own custom usage so that previous node before usage argument on the command-line can be identified easily.  
- `self._is_root`: It tells if current argument is at the root of the arguments tree.  
- `self._parent`: It provides the argument CliArg parent object's address of an argument. It is mainly used for Nargs internal purpose when parsing the command-line.  
- `self._root`: It provides the first branch of root argument to any arguments.
- `self._value`: It returns `None` if argument has no values on the command-line, or a value if the argument have one or more values. If argument has multiple values `self.value` returns the first value.  
- `self._values`: It returns an empty list if argument has no values on the command-line, otherwise it returns a values list. For instance, if argument has only one value then `_values` returns a list that contains only the value.   

**_get_cmd_line**: It is a method that provides current argument command-line. It is the same as `print(arg._root._branches[0]._cmd_line[arg._cmd_line_index])`. A command-line index can be provided to print a different command-line. `_get_cmd_line` is used most of the time when to print the exact argument's path when Nargs throws an error. Note that for implicit arguments, `_get_cmd_line` can't return the command-line path of the current argument because implicit arguments have been added implicitly and they don't exist on the command-line. Instead `_get_cmd_line` returns the last explicit argument from where implicit arguments have been added. In order to print implicit arguments paths in code context developer can use `self._get_path()` (see also [Nargs get_args /`_implicit`](#nargs-getargs)).  

**_get_path**: argument `_get_path()` returns all parent aliases joined with spaces. For each returned alias, alias is returned with index notation if the alias related argument has multiple branches i.e. `--arg-one+1 --arg-one+2`. Explicit notation is set when an alias conflict with parents' aliases or children' aliases. If `wvalues=True` then argument's values are returned after the argument alias. `_get_path` is provided to developer for custom use, it is also used in help or sometimes when nargs throws an error to give arguments paths. Arguments aliases are provided by end-user through command-line but sometimes developer may want to get an argument's path that is not present on the command-line. In this context, `_get_path()` returns argument and parent arguments default aliases see [Properties Explained _aliases](#properties-explained). Path can also be forced to be printed with arguments default aliases by using option `keep_default_alias=True`. `_get_path` is different than `_get_cmd_line` because it gives the shortest path to an argument in the arguments tree whereas `_get_cmd_line` provides the whole command-line until the end of the selected argument alias is reached.  

### Developer Custom Help and Usage
This is a very basic example on how to implement custom help and usage in order to overload built-in help and usage.
```python
args="""
    arg1:
        narg:
    arg2:
        narg:
            nnarg:
    usage:
        _aliases: usage,?
        _is_usage: true
    help:
        _is_custom_builtin: true
"""

try:
    nargs=Nargs(metadata=dy_metadata, args=yaml.safe_load(args), auto_alias_prefix="", builtins=dict(), raise_exc=True)
    args=nargs.get_args("args")

    if args.usage._here:
        if args.usage._previous_dfn is None:
            msg.error('args.usage._previous_dfn is None', trace=True, exit=1)
            print("Custom help for '{}'".format(args.usage._previous_dfn.name))
            sys.exit(0)

    if args.help._here:
        def process_dfn(dfn):
            print(dfn.name)
            print(dfn.level)
            pprint(dfn.dy)
            for child_dfn in dfn.nodes:
                process_dfn(child_dfn)
        process_dfn(args._dfn)
        sys.exit(0)
    
    if args.arg1._here is True:
        print("implement logic for arg1")
        if args.arg1.narg._here:
            print("implement logic for arg1 narg")

    if args.arg2._here is True:
        print("implement logic for arg2")
        if args.arg2.narg._here:
            print("implement logic for arg2 narg")
            if args.arg2.narg.nnarg._here:
                print("implement logic for arg2 narg nnarg")

except DeveloperError as e:
    print("Managed DeveloperError \"{}\"".format(e))
    sys.exit(1)
except EndUserError as e:
    print("Managed EndUserError \"{}\"".format(e))
    sys.exit(1)
```

## Arguments Definition
Developer can write arguments' definition as a Python dictionary, as a YAML file or as a JSON file. It is a tree structure, and its first node is the root argument. If Nargs definition is empty and Nargs builtins option is an empty dictionary then `Nargs().get_args()` returns None. Argument's properties start with an underscore. Argument's children names start with a letter.  
```python
# arguments' definition basic structure
Nargs(args=dict(
    # root argument name is not provided only its properties
    _root_property=value,
    _root_property=value,
    nested_argument=dict(
        _nested_property=value,
        _nested_property=value,
        nested_nested_argument=dict(
            _nested_nested_property=value,
            _nested_nested_property=value,
        ),
    ),
    sibling_argument=dict(
        _sibling_property=value,
        _sibling_property=value,
    ),
))
```

`@` is a special notation for argument name in arguments' definition that can duplicate an argument and its nested arguments to a different location in the arguments tree. Nargs triggers an error for infinite recursion if any when using `@` duplicate notation. `@` is useful to duplicate similar nested arguments. This notation is only needed when developer sets definition in a JSON file or a Python dictionary. `@` is not needed for definition in a YAML file because arguments can be duplicated with existing YAML syntax `node anchors (&) and references (*)`. Built-in arguments with aliases starting with a colon can't be duplicated.  
```json
// "@" notation duplicates nodes
{
    "arg_one":{
        "nested_arg_one": {
        "nested_nested_arg": {}
        },
        "nested_arg_two": {
        "nested_nested_arg": {}
        }
    },
    "arg_two": {
        // notation one (a string for one node)
        "@": "arg_one.nested_arg_one",
        // or notation two (a string with commas to split multiple nodes)
        "@": "arg_one.nested_arg_one,arg_one.nested_arg_two",
        // or notation three (a nodes list)
        "@": [
        "arg_one.nested_arg_one",
        "arg_one.nested_arg_two"
        ]
    }
}
```
### Arguments Properties with Default Values:
In definition file each argument can have any of the properties listed at [Properties Summary](#properties-summary). Any omitted property is set with its default value. In other words these properties need to be set, they are all optional.  
To set a property means that property is present in argument's definition and property value is not null. A property with a null value is considered not set and this property is automatically set with its default value.  

In arguments' definition, argument's properties start with an underscore and nested arguments start with a letter. The first argument or root argument is set like any other arguments except for its name that is automatically set. Root argument name is `args`. All other arguments are root argument's children. Arguments nesting limit is set according to JSON parser, YAML parser, or memory if arguments are provided with a Python dictionary. Arguments' name must match regex `[a-zA-Z][a-zA-Z0-9_]*`. Most of the time Developer won't be using many argument's properties and he or she will rely on arguments' default properties. For instance developer can write a very small program with command `Nargs(metadata=dict(name="research program", executable="research"), args=dict(analyze=dict()))` and Nargs will generate the following program entry point:    
```shell
research: --args ?huv
  [--analyze]
  [--cmd <file>]
 *[--help, -h]
 *[--usage, ?, -u]
  [--version, -v]
```

#### Properties Summary
Property | Default Value | Allowed Types | Information | NodeDfn().dy keys
-------- | ------------- | ------------- | ----------- | -----------------
`_aliases` | null | null, string (comma split), or strings list | Argument's aliases. Alias automatically set if property is null | aliases, aliases_info, default_alias, is_auto_alias
`_allow_parent_fork` | true | null, or bool | Allow/Deny parent argument to branch | allow_parent_fork
`_allow_siblings` | true | null, or bool | Allow/Deny argument's siblings on the command-line | allow_siblings
`_default` | null | null, string (comma split), or strings list | argument's default value(s) | default
`_enabled` | true | null, or bool | Enable/Disable argument | enabled
`_examples` | null | null, string, or strings list | Argument's examples | examples
`_fork` | false | null, or bool | Allow/Deny argument to fork | fork
`_hint` | null | null, or string | Argument's short description | hint
`_in` | null | null, string (comma split), strings list, or dictionary | Argument's list of authorized values  | in, in_labels
`_info` | null | null, or string | Argument's long description | info
`_is_custom_builtin` | false | null, or bool | Argument's internal field for developer when creating custom built-in arguments | is_custom_builtin
`_is_usage` | false | null, or bool | Define if argument is usage argument (only one per definition) | is_usage
`_label` | null | null, or string | Argument's values label for usage | label
`_need_child` | false | null, or bool | Set if argument needs at least one child on the command-line | need_child
`_repeat` | "replace" | null, or string | Define argument's multiple occurrences behavior | repeat
`_required` | false | null, or bool | Set if argument is required when parent argument is present | required, required_children
`_show` | true | null, or bool | Show/Hide argument in usage and help | show
`_type` | null | null, or string | Argument's values type | type
`_values` | null | null, or string | Argument's number of values | values_authorized, values_max, values_min, values_required
`_values` | null | null, or string | Argument's number of values | values_authorized, values_max, values_min, values_required
`_xor` | null | null, string (comma split), strings list (comma split) | Set 'exclusive or' groups for child arguments | xor, xor_groups

#### Properties Explained

**_aliases**: Set aliases for argument. Each argument can have no aliases or unlimited number of aliases. If no aliases are provided or `_aliases=None` then Nargs auto-alias inner function is triggered and create an argument alias automatically. For instance for arg_one, auto-alias is going to set alias `--arg-one` with `Nargs()` option auto_alias_prefix set to `--` and option auto_alias_style set to `lowercase-hyphen`. Arguments' aliases are used on the command-line and arguments' names are used in the code. A valid argument needs to have at least one alias otherwise an error is thrown. If at least one alias is set manually for an argument then auto-alias won't apply to this argument. During alias setup a `default alias` is automatically set. `default alias` is used in a special case [Nargs get_args _get_path](#nargs-getargs). Aliases prefix can be any prefix from prefix list `"", "+", "-", "--", "/", ":", "_"`. Alias's text must follow regex `[a-zA-Z0-9\?][a-zA-Z0-9\-_]*?`. The previous regex means:  
- Required next char must be a lowercase letter, an uppercase letter, an integer.
- Required next char can also be a question mark, if argument property '_is_usage' is set to True. In that case no other chars are accepted.
- Optional next chars can be any char from lowercase letter, uppercase letter, integer, underscore or hyphen.

One char aliases with or without prefix can be set as flag aliases if conditions are met (see [Concatenated Flag Aliases](#concatenated-flag-aliases)).
```json
{
    //  aliases provided as a string
    "_aliases": "-a,--arg,arg"
    //  aliases provided as a list
    "_aliases": ["-a" ,"--arg", "arg"]
}
```
`_aliases` creates the two `NodeDfn().dy` dictionary keys:  
- `aliases`: It returns all the argument's aliases
- `aliases_info`: It returns added info for each alias `{'args': {'is_flag': False, 'prefix': '', 'text': 'args'}}`.
- `default_alias`: It returns the default alias that is the first alias provided by developer in the aliases list.
- `is_auto_alias`: It returns True if alias has been set automatically.

**_allow_parent_fork**: Property allows or denies argument's parent to have more than one branch. If `_allow_parent_fork=False` then Nargs throws an error if argument is present on the command-line and its parent as at least two branches. The property is used for most of the built-in arguments. i.e. for command `prog.py --version`, `prog.py` can be forked when `--version` is present even if `prog.py` has property `fork=True`. This property has not effect on root argument and it is always set to true for root argument.  
`_allow_parent_fork` creates the `NodeDfn().dy` dictionary key: `allow_parent_fork`.  

**_allow_siblings**: Property allows or denies to use siblings' arguments. If `_allow_siblings=False` then Nargs throws an error if argument is present on the command-line and at least one of argument's siblings is present. The property is used for most of the built-in arguments. i.e. when end-user types `prog.py --version`, end-user can't provide any other arguments. This property has not effect on root argument and it is always set to true for root argument.  
`_allow_siblings` creates the `NodeDfn().dy` dictionary key: `allow_siblings`.  

**_default**: Property sets argument's default value(s). If `_default` is `None` then it is ignored. If argument is provided on the command-line without a value then the argument default value(s) is/are added automatically. `_default` values must match any type from `bool`, `float`, `int`, `str` otherwise Nargs throws an error. `_default` value(s) must also match `_in` values if `_in` is set. If `_values` is set then `_default` must match `_values` minimum and maximum number of values. If `_values` is set and `_default` is set then `_values` must be required otherwise Nargs throws an error. More information on `_default` property when `_values` is not set is available at [Properties Explained / `_values` / `Values implicit logic` ](#properties-explained).  
`_default` creates the `NodeDfn().dy` dictionary key: `default`.  

**_enabled**: Property defines if argument and its child arguments are parsed. If set to False then the argument is disabled and not visible in the help. Also all its nested arguments are disabled. If root argument is disabled then Nargs will silently discard end-user command-line arguments and `Nargs.get_args()` will return `None`.  
`_enabled` creates the `NodeDfn().dy` dictionary key: `enabled`.  

**_examples**: Property provides argument's command examples. It accepts a string or a strings list. Developer can provide command examples for a particular argument. Argument examples are then printed on the screen if any when end-user types `--help`, `--examples` or `--usage --examples`.  
`_examples` creates the `NodeDfn().dy` dictionary key: `examples`.  

**_fork**: Property defines if argument can be duplicated. At start the command-line arguments tree is fully created, then when end-user types an argument on the command-line the argument is activated. To activate an argument means adding it on the command-line (see function activate_arg in get_args.py file for implementation). If argument's property `_fork=True` then argument can be duplicated using argument's branch index notation. `Argument's branch index notation` applies on the command-line and it consists of the argument alias followed by a plus sign and an optional index. If only the plus sign is used, it means create an argument's branch. If index is used then end-user can accurately select a particular instance of an argument. For instance two branches have been created for `arg_one` with command `prog.py --arg-one --arg-one+`. End-user can provide `Argument's branch notation` to get the same result i.e. `prog.py --arg-one+1 --arg-one+2`. If end-user wants to provide a second argument's occurrence of argument's first branch then end-user uses notation plus sign with index i.e. `prog.py --arg-one --arg-one+ --arg-one+1 --arg-one+2`. Here `--arg-one+` means create another branch and `--arg-one+1` means goes back to the first `--arg-one` argument (aka: `--arg-one` first branch second occurrence) and `--arg-one+2` to the second `--arg-one+` argument. In branch index notation the highest index that can be use is equal to `number of existing branches length plus one`. If the highest index is used then a new branch is created. It means that `--arg-one+1` will always work but `--arg-one+2` or greater may not work. `_fork` property can also be set for root argument. It means that end-user will be able to branch the whole program as many times as needed. i.e.:  
```bash
# here --args is root argument alias
# explicit
prog.py + --arg-one - --args+ + --arg-one - --args+1 + --arg-one
# implicit
prog.py --arg-one --args+ --arg-one --args+1 --arg-one
```

To create a branch means to duplicate an argument with all its child arguments. Thus an argument's branch is composed of an argument and all its child arguments. The duplicated argument is then activated. An argument's branch is different than an argument's occurrence. An argument's occurrence is when an argument is used multiple times at the same branch (see [Properties Explained / `_repeat`](#properties-explained)). i.e. argument's branches can be typed as `prog.py --arg-one+ --arg-one+ or prog.py --arg-one+1 --arg-one+2`. Argument's occurrences can be typed as `prog.py --arg-one --arg-one or prog.py --arg-one+1 --arg-one+1 or prog.py --arg-one+2 --arg-one+2`.  

`_fork` creates the `NodeDfn().dy` dictionary key: `fork`.  

**_hint**: Property provides a short description of the argument's purpose. It accepts a string or a strings list. `_hint` length is limited to 100 char.  
`_hint` creates the `NodeDfn().dy` dictionary key: `hint`.  

**_in**: Property sets an authorized values list for an argument. `_in` accepts a list, a string, or a dict:   
- If `_in` is a list then all list values must match argument's `_type`. `_type` property may be any type from `bool`, `float`, `int`, or `str`.  
- If `_in` is a string then string is comma split to create a list and all list values are cast to match argument's `_type`. `_type` property may be any type from `bool`, `float`, `int`, or `str`.
- If `_in` is a dict then dictionary keys type must match property `_type`. Dictionary keys are casted into the related type i.e. they can be written as a string and they will be converted to `int` if `_type` is set to `int`. Dictionary values can be any type from `bool`, `float`, `int`, `str`, or `null`. Dictionary values are just used as label for help or usage. Dictionary keys are returned to the program when end-user typed the relative dictionary key on the command-line.  
- More information on `_in` property when `_values` is not set is available at [Properties Explained / `_values` / `Values implicit logic` ](#properties-explained).  
`_in` creates the `NodeDfn().dy` dictionary keys:   
- `in`: It returns a list of accepted values.  
- `in_labels`: It returns a list of accepted values related labels if `_in` has been provided has a dictionary.  

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

**_info**: Property provides the argument's purpose full description. `_info` has no length limit.  
`_info` creates the `NodeDfn().dy` dictionary key: `info`.  


**_is_custom_builtin**: Property defines if argument `is_custom_builtin`. The main use for this attribute is when developer creates special arguments like usage and help. Argument with `is_custom_builtin=True` do not trigger parent error if parent is root argument, argument `need_child` is True, no child arguments are provided and all child arguments have `is_custom_builtin=True`.  
`_is_custom_builtin` creates the `NodeDfn().dy` dictionary key: `is_custom_builtin`.  

**_is_usage**: Property sets the usage argument for the arguments' definition tree. It is only useful if developer disables built-in usage in order to create his or her own usage. `_is_usage` can only be assigned to one argument and this argument has to be on node level 2. In order to set a usage node the following node properties are enforced: `allow_parent_fork=True, allow_siblings=True, is_custom_builtin=True, fork=False, repeat="replace", required=False`. When `_is_usage` is set to True, argument can have an alias with a question mark and any of the authorized alias's prefixes i.e. `?, +?, -?, --?, /?, :?, _?`. The usage argument has its CliArg attribute `_previous_dfn` set with the previous NodeDfn argument used before the usage argument (see also [Nargs get_args /`_dfn`](#nargs-getargs) to have more information on how to set custom help and usage).  
`_is_usage` creates the `NodeDfn().dy` dictionary key: `is_usage`.  

**_label**: Property provides a label for argument's values. Label is printed with help or usage commands i.e. for `label: FRUIT` help prints `[--item [<str:FRUIT>]]`. `_label` must be a string or null. `_label` can't be set when property `_in` is set. More information on `_label` property when `_values` is not set is available at [Properties Explained / `_values` / `Values implicit logic` ](#properties-explained).  
`_label` creates the `NodeDfn().dy` dictionary key: `label`.  

**_need_child**: Property defines if Nargs throws an error when child arguments are not provided. If `_need_child` is set to True argument is present on the command-line and none of its children are present then Nargs throws an error. For root argument `_need_child` is set to False if definition child arguments are only built-in arguments. `_need_child` is set to True by default for root argument only. For other arguments `_need_child` is set to False by default.  
`_need_child` creates the `NodeDfn().dy` dictionary key: `need_child`.  

**_repeat**: Property defines argument behavior when end-user types multiple occurrences of an argument on the command-line. Unlike `_fork` property that is related to argument's branches number, `_repeat` property is related to argument's occurrences number per argument's branches. `_repeat` default value is `replace`. `_repeat` property is also related to command-line argument property `_count` (see [Nargs get_args / argument properties / `self._count`](#nargs-getargs)). There are 3 actions for `_repeat` property:  
- **append**: It means that only one argument is kept, and each repeated argument's values are appended to a values list for the argument. In this context, `arg._alias` is set with the latest alias developer input in the terminal. CliArg `_count` property is incremented each time a new argument's occurrence is added.    
- **error**: It means that an error is triggered if the argument has more than one occurrence. CliArg `_count` property is always equal to 1.  
- **replace**: It means that only one argument is kept but for each argument's occurrence then argument's values replace the previous argument's occurrence values. In this context, the last alias used is the one kept for the argument. If nested arguments have already been selected on the command-line with previous argument's occurrence, then nested arguments are cleared. i.e.: `_repeat:"replace"` means that basically you re-create an argument branch as if it has not already been selected on the command-line. CliArg `_count` property is always equal to 1.

`_repeat` creates the `NodeDfn().dy` dictionary key: `repeat`.  

**_required**: Property defines if argument is required when end-user adds argument's parent to command-line. If end-user types an argument that has a child argument with property `_required` set to True and end-user does not type the child argument then there are two scenarios:
    - If omitted a required argument is added implicitly with its default alias either:
      -  if argument has no values
      -  if argument has default value(s). In that case default value(s) is/are set.
    - If an omitted required argument has required value(s) with no set default value(s) then an error is thrown.

For an omitted required argument, the two scenarios process repeats recursively. It means that an omitted argument is added implicitly and required arguments are searched in added implicit argument's children until no more children are available or no more required arguments are found in children.  

`_required` property is always set to True for root argument because root argument is always required. `_required` property is set to False by default for all the other arguments.

Arguments with property `_required=True` follow certain rules to prevent runtime error due to arguments' definition:
- if `_required=True` and argument's name is present in parent `_xor` property then Nargs throws an error. Reason: if an argument is both required and present in parent xor property then the other arguments from the xor groups can never be added to the command-line because one of the required argument is always needed.
- if `_required=True` and argument's property `_allow_parent_fork=False` then Nargs throws an error. Reason: if an argument is required and don't allow parent fork, then a parent argument with `_fork=True` will never be able to fork.  
- if `_required=True` and argument's property `_allow_siblings=False` then Nargs throws an error. Reason: if an argument is required and it does not allow siblings, then siblings can never be added.  
- if `_required=True` and argument's property `_need_child=True` then Nargs throws an error (This rule does not apply to root argument.). Reason: Some required argument may be added implicitly but if `_need_child=True` then implicitly added arguments may trigger an error. Implicitly added argument should never triggers an error and end-user should only have to solve errors that he or she triggers.  

`_required` creates the `NodeDfn().dy` dictionary keys: 
- `required`: It returns if an argument is required or not.  
- `required_children`: Each time an argument is required, argument's name is added to its parent list `required_children`.  

**_show**: Property defines if argument is printed in help, usage and documentation. If set to False end-user and developer can still use the argument but argument aliases and flags won't show in help, usage, or documentation.  
`_show` creates the `NodeDfn().dy` dictionary key: `show`.  

**_type**: Property sets type argument's value(s). Argument's values are cast to the different types. Multiple types are supported:  
`_type` creates the `NodeDfn().dy` dictionary key: `type`.  

- **bool**: Argument expected value(s) must be of Boolean type. Bool is generally a string that is case insensitive and is equal to 'true' or 'false'. If 1 is given then it is interpreted as true. If 0 is given then it is interpreted as false.
- **float**: Argument expected value(s) must be of type float.
- **int**: Argument expected value(s) must be of type integer.
- **str**: Argument expected value(s) must be of type str.
- **dir**: Argument expected value(s) is a relative or absolute path to an existing directory.
- **file**: Argument expected value(s) is a relative or absolute path to an existing file.
- **path**: Argument expected value(s) is a relative or absolute path to either an existing directory or an existing file.
- **vpath**: Argument expected value(s) is a relative or absolute path to an existing or non-existing directory or file.
- **json**: Argument expected value(s) is a JSON/YAML string. String may be single-quoted.
- **.json**: Argument expected value(s) is either a .json/.yaml file or JSON/YAML string that may be single-quoted.
- In types `dir`, `file`, `path`, and `vpath`, relative paths are resolved according to terminal current directory.
- JSON strings can be single-quoted.
- YAML strings or YAML files are discarded if PyYAML has not been installed.
- More information on `_type` property when `_values` is not set is available at [Properties Explained / `_values` / `Values implicit logic` ](#properties-explained).

**_values**: Property sets the number of argument's values. An argument's values are first either required or optional and second they have a minimum and a maximum number of values. `_values` can be expressed as:  
- a positive integer: number of values is set as `required`.
- a string that matches regex `r"^(?P<star>\*)|(?P<plus>\+)|(?P<qmark>\?)|(?P<min>[1-9][0-9]*)(?:\-(?P<max>(?:[1-9][0-9]*|\*)))?(?P<optional>\?)?$"` with rules:
  - If string equals '*' it means that values are optional, and number of values can range from 1 to infinite.
  - If string equals '+' it means values are required, and number of values must range from 1 to infinite.
  - If string equals '?' it means values are optional, and number of values can be 1.
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

`_values` creates the `NodeDfn().dy` dictionary keys:
- `values_authorized`: It returns if argument accepts values or not.
- `values_max`: It returns maximum number of values if any.
- `values_min`: It returns minimum number of values if any.
- `values_required`: It returns if argument values are required or optional.

**Values implicit logic**: When `_values` property is set then it is set explicitly. When `_values` property is not set then if any properties from `_default`, `_in`, `_label`, or `_type` is set then `_values` is set implicitly. The logic behind this behavior is that all these properties are related to `_values` so when one of these properties is present and `_values` is not set then `_values` is set implicitly. The implementation of implicitly set `_values` is defined in `src/dev/set_dfn.py` at function `implement_implicit_logic()`. The general rules are:  
- If `_type` is not set and one of the properties `_default`, `_in`, `_label`, or `_values` is set then `_type` is set to `str`.
- If `_default` is set and `_values` is not set then values are set to required and minimum values and maximum values are equal to `_default` list length.
- If `_in` is set and `_values` is not set then values are set to required and minimum values and maximum values are equal to '1'. 
- If `_label` is set and properties `_default`, `_in`, `_type`, and `_values` are not set then values are set to required and minimum values and maximum values are equal to '1'. 
- If `_type` is set and properties `_default`, `_in`, `_label`, and `_values` are not set then values are set to required, minimum values is equal to '1', and maximum values is equal to '1'.

**_xor**: Property defines arguments group for current argument children's arguments. Each group contains at least two argument names from current argument's children. `_xor` a.k.a. `exclusive or` allows Nargs to trigger an error when two arguments from the same group are present on the command-line at the same time. Multiple groups can be created. A child argument can't be both in a `_xor` group and have its `_required` property set to `True` at the same time.  
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

According to arguments' definition:
```yaml
_xor: 
    - arg1,arg2
    - arg2,arg3
arg1: 
arg2:
arg3:
```
`_xor` creates the `NodeDfn().dy` dictionary keys:  
- `xor`: It returns a dictionary of child argument names with groups numbers and other argument names from the same xor groups. i.e.:
```python
'xor': {'arg1': {'1': ['arg2']},
         'arg2': {'1': ['arg1'], '2': ['arg3']},
         'arg3': {'2': ['arg2']}},
```
- `xor_groups`: It returns a list of xor group numbers that argument belongs to on its node level i.e.: `nargs.dfn.dy_nodes["arg1"].dy["xor_groups"]` returns `[1]`.


## Built-in Arguments
Nargs provides end-user built-in arguments. Built-in arguments' definition is available in Nargs source code at file `src/dev/get_node_dfn.py` in function `add_builtins()`.  

Main built-in arguments are available at node level 2. Built-in arguments aliases are set according to Nargs options `auto_alias_prefix` and `auto_alias_style` (except if end-user provided the aliases through `Nargs builtins` option). If developer change `auto_alias_prefix` and `auto_alias_style` options then built-in arguments aliases are also modified to match developer aliases style.  

`_cmd_` built-in argument allows end-user to write command-line arguments in a file with newlines, empty lines, indentation, and comments using '#'. `cmd` goal is to overcome terminal command length limitation and/or to allow developer to write commands in a readable way. When command-line is provided through built-in argument `cmd` then the root argument must match its argument's alias(es). Root argument's alias is provided in the arguments' definition either implicitly by Nargs auto-alias generation or explicitly by developer through arguments' definition. Root argument alias equals `--args` when provided implicitly by default options.  

`_help_` built-in argument generates host program minimum help from Nargs arguments' definition and metadata. Users and end-users can print help to terminal with `prog.py --help` or export it in 4 different formats `asciidoc`, `html`, `markdown`, and `text`. A file path can also be provided. i.e.: `prog.py --help --export html --to ../userpath.html`. Help can be printed or exported with arguments `syntax` explained. `--help --syntax` gives end-user the essential information to understand how to read and use Nargs Notation. Help has multiple sections:  
- About Section: It provides metadata information from the program. Metadata is provided implicitly with `gpm.json` and/or explicitly by developer with `Nargs metadata` parameter. The printed fields are all the metadata keys provided to Nargs.
- Usage Section: It provides program's usage. 
- Help Section: It provides program's help.
- Examples Section: It provides all program's examples.
- Nargs Argument Syntax Section. It contains:
    - Nargs module metadata.
    - How to read Nargs syntax.
    - How to type arguments and values in the terminal.

`--help --metadata` prints all program's metadata provided by developer. In order to import metadata Nargs searches first a `gpm.json` file in the program executable root directory. If `gpm.json` file is found then it is used as a based dictionary for Nargs metadata. If `gpm.json` file is not found then Nargs metadata starts with an empty dictionary. Developer can also provide a dictionary through `Nargs(metadata=dict())` option and this dictionary is merged into Nargs based metadata dictionary. In other words, Nargs metadata comes first from a gpm.json file if any and then developer metadata is merged into that dictionary and developer metadata overloads any previous similar dictionary key. `--help --metadata` prints metadata keys and values to terminal. Selected key(s) may be provided.  

`--help --examples` prints all program's examples.  

`_path_etc_` only exists if developer sets `Nargs()` option `path_etc` value. It provides the program's configuration path.    

`_usage_` built-in argument prints all the arguments in a tree structure with Nargs notation. The nested argument `from_` selects the starting argument and it can be either the current argument or a parent. The printed nested arguments depth can be set with nested argument `depth`. For each printed arguments the following data can be provided: `examples`, `flags`, `hint`, `info`, `path`, and `properties`. For instance end-user can type `prog.py -ueFhipr`, `prog.py --usage --examples --flags --hint --info --path --properties` or `prog.py --help --usage --depth 1 --from 0 -eFhipr`. Built-in argument `_usage_` is the only built-in argument that can use question mark `?` as an alias. Question mark is useful, but it has limited on some systems. For instance on bash terminals, question mark is a bash wildcard, and it is going to be replaced by the name of a file or a directory if any directory or file has only one char for name in the current directory.  

`_version_` returns program version if it has been provided into metadata. If not provided into metadata then Nargs throws an error whenever built-in version argument is used.  

**Note**: When modifying `auto_alias_prefix` there are two implicit rules that apply to built-in arguments only:
- For prefix `--` Built-in argument flag alias are set with `-` i.e. `_version_` aliases are `-v, --version` with `auto_alias_prefix='--'`.
- `auto_alias_prefix` does not affect question mark alias for built-in `_usage_` argument. i.e. `_usage_` aliases are `?, /u, /usage` with `auto_alias_prefix='/'`.

Developer can overload these rules by setting built-in arguments aliases manually with Nargs `builtins` option.  

## Arguments Explicit Implicit Notation
In order to navigate through the arguments tree, end-user can provide arguments on the command-line by using two notations **explicit notation** and **implicit notation**. There is always a reference argument when using explicit or implicit notation. The reference argument is the current argument. For instance when Nargs starts parsing the command-line the first reference argument is the root argument. Then any other argument provided on the command-line becomes reference argument one after the other following `Nargs().get_args()` parsing the command-line from left to right.  

### Explicit Notation
Explicit notation describes exactly the arguments position in the arguments tree using `+`, `=`, and `-` symbols. Explicit notation is used to exactly select one alias argument from multiple other argument with same alias located at different node levels. Explicit notation is optional most of the time and it can be mixed with implicit notation. Explicit notation is required when either:  
- An alias is found multiple times in argument's parents' children and end-user wants to reach a node at a lower level.
- An alias is found both in one argument's parent's children and argument's children and end-user wants to reach the node in parent's children.  

Explicit notation uses the following syntax before an argument:  
**plus symbol `+`**: It stays at the same node level but it only searches aliases in current argument's children and search for flags available in current argument's flag set. Only one plus symbol can be used before an argument.  
**equal symbol `=`**: It goes up one level and it only searches aliases in current argument's parent's children and search for flags available in current argument's parent's flag set. It means basically that it only searches aliases and flags in current argument and current argument's siblings. Only one equal symbol can be used before an argument.  
**dash symbol `-`**: It goes up two node levels if only one dash symbol is provided. It goes up three node levels if two dash symbols are provided and so on. Unlike `+` and `=` notation, multiple `-` characters can be concatenated for instance `--` or `----` until the node level reaches 0 maximum (`--` means go up 2 node levels). `-` notation also accepts a positive integer instead of concatenation i.e. `-4` permits to go up four node levels at time. When node level reaches 0, it means that the targeted argument is the root argument only. Level 0 is the same that when `Nargs.get_args()` is called just before the root argument is parsed. Level 0 searches only in root argument own aliases for aliases and flags. In usage and help if root node aliases start with a flag set then that flag set is the one available at level 0.   
After an explicit notation end-user has to provide an argument otherwise Nargs throws an error. When end-user navigates in the arguments tree, node level starts at 1 for the root argument and the node level is incremented for each nested arguments level.  

**Explicit notation pros**:  
- notation describes exactly each argument location in the argument's tree.
- No matter the current argument's location in the arguments tree, all other arguments are reachable on the command-line with explicit notation.

**Explicit notation cons**:  
- It is verbose and thus hard to read.

### Implicit Notation
Implicit notation allows to navigate through the arguments tree without using **dash**, **equal**, or **plus** symbols. Arguments' aliases are searched implicitly in the arguments tree. For instance the root argument does not need to use the `+` symbol for its nested arguments because root argument is the only sibling at level 1. Then for higher node level, explicit notation may be needed. Implicit notation is optional and can be mixed with explicit notation. For a given argument's alias in the terminal, implicit notation follows the rules:  
- Alias is searched in explicit aliases which means current argument's child arguments' aliases.
- Alias is also searched in implicit aliases. Implicit aliases are all the current argument's parents' aliases and parent arguments' direct child arguments' aliases. Search starts at the first parent and once an argument is found then the implicit argument is selected and search stops. In other words there is only one or none implicit argument per alias for current argument.

**Implicit notation pros**:  
- Shorter notation.
- Closer to command-line arguments "standard syntax". 
- Developer can define arguments aliases in such a way that they never conflict on the command-line and thus explicit notation is not be needed.
**Implicit notation cons**:  
- It is hard to read even if it is less verbose than explicit notation.
- It is limited because end-user might still need to use explicit notation depending on arguments' definition.

### Note
Both explicit notation and implicit notation are hard to read for long command-line. It is not specific to Nargs but to any program that accepts command-line. To improve terminal commands readability, Nargs use the following features:  
- [Built-in argument cmd](#built-in-arguments).
- Nargs `cmd` parameter.
- Multiple alias prefixes

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
main.py + --arg-one + --nested-arg-one + --nested-nested-arg-one - --nested-arg-two - --arg-two
# semi explicit/implicit (both notation can be mixed together)
main.py --arg-one --nested-arg-one + --nested-nested-arg-one - --nested-arg-two --arg-two
# implicit
main.py --arg-one --nested-arg-one --nested-nested-arg-one --nested-arg-two --arg-two

# explicit
main.py + --arg-one = --arg-two
# implicit
main.py --arg-one --arg-two

# explicit notation is needed in some scenarios.
main.py -a -n -b # -b selects nested_arg_two
# explicit 
main.py -a -n - -b # -b selects arg_two
```

## Command-line Values Notation
More information on command-line syntax is available at [Nargs end-user documentation](end-user.md).  

For definition:  
```yaml
  _values: "?"
  arg_one:
    _aliases: "-a,--arg-one"
    _values: "+"
```

Values Notations are:  
```bash
main.py value
main.py -a value
main.py -a value1 value2 "this is value3"
main.py -a value1 value2 'this is value3'
main.py -a=value
main.py -a="value"
main.py -a='value'
main.py -a='value1 value2 "this is value3"'
main.py -a="value1 value2 'this is value3'"
main.py -a:value
main.py -a:"value"
main.py -a:'value'
main.py -a:'value1 value2 "this is value3"'
main.py -a:"value1 value2 'this is value3'"
main.py --arg value
main.py --arg value1 value2 "this is value3"
main.py --arg value1 value2 'this is value3'
main.py --arg=value
main.py --arg="value"
main.py --arg='value'
main.py --arg='value1 value2 "this is value3"'
main.py --arg="value1 value2 'this is value3'"
main.py --arg:value
main.py --arg:"value"
main.py --arg:'value'
main.py --arg:'value1 value2 "this is value3"'
main.py --arg:"value1 value2 'this is value3'"
```

### Concatenated Flag Aliases

Flags aliases are one char aliases that can be used concatenated. The first flag must use its prefix and the other concatenated flags do not use their prefixes. i.e. `prog.py /abc` where `a`, `b`, and `c` are different aliases that can come from the same argument or from different arguments.  
Concatenated flag aliases are also called flag set. Each argument may have its own flag set.  
Flag set are not shown by default on command-line usage. Flag set can be seen if any when using built-in usage argument with command-line `prog.py --usage --flags` or when printing the help with built-in help argument.  
In arguments' definition a flag set is all the flags available for a particular argument.  
On the command-line a flag set is all the concatenated flags typed by end-user after a one char alias that may not have a prefix.   
Flag's candidates are implicit arguments or explicit arguments of the reference argument. A flag is defined by an alias char without the alias prefix i.e. in alias `/a` only `a` defines the flag.  
For each argument there is only one argument per char alias that is kept to generate the definition flag set for that argument. The rules to determine which argument is kept when multiple arguments aliases share the same char alias are:
- If two aliases sharing the same char alias come from the same argument then the kept alias for flag is the alias with alias prefix that comes first in the list `['+', '-', '', '/', ':', '_', '--']`.  
- If two aliases sharing the same char alias do not come from the same argument:
    - If arguments do not have the same value for property `_show`:
        - Argument with property `show=True` has precedence over the other argument.
    - Else if arguments are on the same node level:
        - Aliases are compared and precedence goes to the argument that alias prefix comes first in the list `['+', '-', '', '/', ':', '_', '--']`.
    - Else if arguments are not on the same node level:
        - Argument with higher node level has precedence over the other argument.   

Flags can be retrieved through built-in usage argument for each argument. Flags can be typed in any order (except if developer has set a particular sorting order in code) and they can be added several times. In fact flags are still related to their argument and when typed the same rule applies as if the entire argument was typed. i.e. `prog.py -chu` may be equal to `prog.py -c -h -u` or `prog.py -c /h u` depending on the arguments definition. So it means that some arguments can still exit when typed, argument's values may be required, or flag argument may throw an error if multiple occurrences are provided. Flags are arguments and they depend on arguments' definition. Developer should set char aliases in a way that is intuitive for end-user to use them as flags.  
The main purpose of flags is to typed arguments with the shortest syntax possible. It is really convenient for developers that type the same command hundreds of times.
Flags are context-sensitive because they are gathered as a set related to the current arg. So it means that flags combinations are not limited because arguments nesting is virtually endless with Nargs.  
Only the latest flag typed on a set can have values. Not all arguments from the pool of explicit and implicit arguments are available because flags are set according to rules define above.  
Flags does not allow explicit notation, so it is not possible to navigate explicitly with that notation.  
Flags does not allow branch index notation except for the latest flag. So it is not possible to navigate between different argument branches of the same argument within flags notation.  
The current argument is always the latest flag parsed so the flags set available may change when typing more flags on the command-line.  When all the flags have been parsed the current command-line argument is the argument of the latest parsed flag.  
Flags may be intuitive and easy to remember depending on arguments' definition.  
Flags can be located on any node level so flags on lower level may be available to all arguments.  

## How to Implement Nargs Global Arguments
A global argument is an argument that is available on all node levels of the arguments tree. There is no global arguments in Nargs per say. Built-in arguments are only available on arguments node level 2. However developer can simulate a global argument by using arguments' implicit notation. For instance starting at current argument if another argument alias is located at node level 2 and no other arguments have the same alias in current argument explicit aliases or implicit aliases then developer can provide argument alias located at node level 2 and it is going to be called as if it was a global argument. If an argument is not located at node level 1 or node level 2 it may still be pseudo-global to certain branches of the arguments tree.  

## How to Implement a Nargs Radio Button Like Argument
A radio button like argument is an argument that provides multiple options and only one can be selected at a time. There are three ways:
- with values using `_in` property. i.e.: `_in="logout,reboot,shutdown,suspend"
- with argument's aliases using `_aliases` property. i.e.: `_aliases="--logout,--reboot,--shutdown,--suspend"`
- with argument's aliases using `_xor` property. i.e.: `_xor="home_server,work_server"

In Definition:  
```yaml
prog.py:
    _xor: home_server,work_server
    home_server:
        _in: logout,reboot,shutdown,suspend
    work_server:
        leave:
            _aliases: --logout,--reboot,--shutdown,--suspend
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

Logical rules for arguments' combinations are enforced first because of the arguments tree structure. Tree structure allows different arguments to share same aliases and still they can't overlap each other. There are also the branch index notation that allows any argument to be forked. So each branch 
Then there are multiple arguments' definition properties that enforce basic logical rules: 
- `_allow_parent_fork` prevents or authorize the parent argument to branch when argument is present on the command-line.  
- `_allow_siblings` prevents or authorize argument's siblings when argument is present on the command-line.  
- `_fork` with branch index notation allows any argument to be duplicated. It creates a whole branch with the duplicated argument because all of the nested children are also recreated.   
- `_need_child` forces end-user to add at least one child argument when argument is present on the command-line.  
- `_repeat` defines the behavior of multiple argument's occurrences on the command-line.  
- `_required` main purpose is to allow having arguments added implicitly depending on their values. An argument that has its property `_required` set to false does not necessarily means that the argument is optional. Nargs only defines a tiny subset of most used logical arguments' combinations. Developer is the one who codes the program arguments logical rules in code section. When a `_required=False` argument is still mandatory in code's logic then developer may add that information in the `_info` property of the argument to let end-user knows about it.  
- `_xor` main purpose is to be able to simply let the end-user knows that only one argument or another can be present at the same time.

Nargs can't describe all arguments logical rules, it would be too verbose to display on terminal or in a documentation and it would probably be a duplicate of developer arguments logic in code implementation. Developers do not need to rely on arguments' definition's properties to set the logic of the application. All the logic can be set in code context. Logical rules from argument properties are helpers that provide rapid development solutions for most of the cases.  

## Loading Definition Performance

A performance summary is available at `src/performance.csv`. The file to generate performance summary is located at `src/tests/performance.py`. The performance test consists in generating an arguments' definition tree with a defined number of nodes and then to test different scenarios on that arguments tree. The final result is a duration time according to the number of nodes and the scenario tested. The number of nodes start at 50 nodes and is incremented by 50 until reaching 1000 nodes and then it is incremented by 1000 until reaching 100000 nodes and then it is incremented by 10000 until reaching 100000 nodes. The different scenarios when loading the definition tree:  
1. a Python dictionary with no cache file generated.
2. a JSON file with no cache file generated.
3. a JSON cache file with integrity check (only_cache=False).
4. a JSON cache file without integrity check (only_cache=True).
5. a YAML file with no cache file generated.
6. a Pickle cache file with integrity check (only_cache=False).
7. a Pickle cache file without integrity check (only_cache=True).  

The cache file on scenario 3, 4, 6, and 7 may be generated from a Python dict, a JSON file or a YAML file. A cache file is generated when Nargs option cache is set to True. Pickle cache file is limited because Python throws error `RecursionError: maximum recursion depth exceeded while pickling an object` when trying to `pickle.dump` an arguments tree of 872 nodes.  
**Performance conclusion:**  
- The result is the same when using a Python dictionary without cache or when using a JSON file without cache.
- The fastest scenario is when definition is read from a cache file (with or without integrity check). There are no noticeable differences when integrity is checked and when integrity is not checked. Pickle cache file is also 1.5 to 2 times faster than JSON cache file.
- The slowest scenario is when definition is read from YAML without cache. Using a YAML file without cache produces loading time 4 times slower than other scenarios. However if developer enables cache for YAML file then loading definition reaches fastest speed once the cache has been generated.
- The speed difference between using a cache file and not using one is roughly 1.5 to 2 times faster for a JSON file.
- Performance test results show that loading a definition file with 250 nodes and without cache gives a parsing time of less than 20ms. This result drops to 9ms with cache enabled. It takes 1s to load a definition file of 20000 nodes with cache enabled.
- Performance tests do not include tests on command-line parsing speed.
