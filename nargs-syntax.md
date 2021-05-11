# NARGS END-USER DOCUMENTATION
## Table of Contents
- [NARGS ARGUMENTS SYNTAX](#nargs-arguments-syntax)
    - [About Nargs](#about-nargs)
    - [Nargs Modes Explained](#nargs-modes-explained)
    - [Argument Aliases Types](#argument-aliases-types)
    - [Argument Aliases State](#argument-aliases-state)
    - [Arguments Navigation](#arguments-navigation)
    - [Argument Values](#argument-values)
    - [Argument Special Values Types](#argument-special-values-types)
    - [Aliases Equals Values Notation](#aliases-equals-values-notation)
    - [Argument Number of Values](#argument-number-of-values)
    - [Repeated Argument](#repeated-argument)
    - [Argument Examples](#argument-examples)
    - [Either Arguments](#either-arguments)
    - [Single Arguments](#single-arguments)
    - [Special Commands](#special-commands)

## NARGS ARGUMENTS SYNTAX
### About Nargs
`Name:` Nested Arguments<br>
`UUID4:` 89d8676a-6b02-43fa-8694-e97de5680cd0<br>
`Version:` 0.0.1<br>
`Date:` 03/06/2021 19:49:39<br>
`Authors:` Gabriel Auger<br>
`Licenses:` MIT<br>
`Description:` Command-line Arguments Parser<br>

### Nargs Modes Explained
- `cached_dfn:` When 'enabled' arguments definition is cached to enable faster arguments parsing.
- `explicit:` When 'enabled' argument navigation needs to be explicit only.
- `substitute:` When 'enabled' string in the command-line with syntax \_\_name\_\_ are substituted with same 'name' environment variable if any.
- `usage_on_root:` When 'enabled' Nargs throws usage when only root argument is provided.
- `yaml_syntax:` When 'enabled' means PyYAML is installed and yaml can be provided for arguments values types `.json` and `json`.

### Argument Aliases Types
- `long aliases` i.e. **--argument**. They may accept value(s).
- `short aliases` i.e. **-a**. They may accept value(s) and may be concatenated.
- `concatenated aliases` i.e. **-abcd**. Each char represents one short alias argument. Values can't be provided with this notation. All arguments must have the same parent.
- `dashless aliases` i.e. **argument**. They may accept value(s).

### Argument Aliases State
- required: **-m, --mount**
- optional: `[`**-m, --mount**`]`
- available nested arguments: `»` `[`**-m, --mount**`]` or `»` **-m, --mount**

### Arguments Navigation
- Implicit navigation uses only aliases and values.
- Explicit navigation uses command-line symbols `+` and `-`.
- Explicit navigation searches for aliases only in children arguments.
- Implicit navigation searches first aliases in children arguments and if not found it searches aliases in parent arguments until root argument is reached.
- Command-line symbols `+` and `-` help to explicitly navigate arguments' tree.
- Explicit navigation with command-line symbols `+` and `-` may be omitted.
- Command-line `+` symbol may be concatenated `+++` or used with a multiplier `+3`.
- Explicit navigation is needed to select one alias that is both in parent and children arguments.
- Explicit navigation allows faster arguments parsing.
- Alias is needed after explicit navigation.
- i.e.(implicit): » prog --help --export html --to file.html.
- i.e.(explicit): » prog `-` --help `-` --export html `+` --to file.html.

### Argument Values
- required: *`<str>`*
- optional: `[`*`<str>`*`]`
- default: *`<str> (=default_value)`* or *`<int:VALUE> (=1, 3, 4, 5)`*
- preset: *`{str:value1, value2, value3}`*
- preset return values: *`{str:value1 (1), value2 (2), value3 (3)}`*
- label: *`<type:label>`* i.e. *`<str:PATH>`*
- standard types: *`str`*, *`bool`*, *`int`*, and *`float`*
- Boolean argument's value(s) can be either case-insensitive string *`true`*, case-insensitive string *`false`*, *`0`*, or *`1`* where *`0`* is False and *`1`* is True. i.e. *`prog.py true True 1 0 False falsE`*

### Argument Special Values Types
- *`dir`*: existing directory.
- *`file`*: existing file.
- *`path`*: existing directory or file.
- *`vpath`*: existing or non-existing directory or file.
- *`json`*: JSON/YAML string.
- *`.json`*: .json/.yaml/.yml file or JSON/YAML string.
- Relative paths are resolved in types dir, file, path, vpath, and .json.
- JSON strings can be single quoted.

### Aliases Equals Values Notation
- `long aliases`, `short aliases`, and `dashless aliases` arguments accept equals values notation.
- i.e. **--argument**='*`value1, value2, "this is value3"`*'
- i.e. **--argument**="*`value1, value2, 'this is value3'`*"
- i.e. **-a**="*`value1, value2, 'this is value3'`*"
- i.e. **argument**="*`value1, value2, 'this is value3'`*"
- This values notation is mainly use when a value is mistaken for an alias and end-user wants to explicitly add it as a value.

### Argument Number of Values
- required 1 value: *`<str>`* 
- optional 1 value: `[`*`<str>`*`]`
- required int value: *`<str> 5`*
- optional int value: `[`*`<str> 3`*`]`
- required min int to max int: *`<str> 2..3`*
- optional min int to max int: `[`*`<str> 4..5`*`]`
- required min 1 to max infinite: *`<str> ...`*
- optional min 1 to max infinite: `[`*`<str> ...`*`]`
- required min int to max infinite: *`<str> 7...`*
- optional min int to max infinite: `[`*`<str> 8...`*`]`
- required min 1 to int: *`<str> ...3`*
- optional min 1 to int: `[`*`<str> ...2`*`]`

### Repeated Argument
- (`a`)ppend values: **-m, --mount :a**
- (`c`)reate new argument fork: **-m, --mount :c**
- (`e`)xit if repeated: **-m, --mount :e**
- (`r`)eplace previous argument and reset children (implicit): **-m, --mount**

### Argument Examples
- `[`**-m, --mount :e**`]`
- **-m, --mount** *`<str:PATH> 1... (=mycustompath)`*
- `[`**-m, --mount** `[`*`<str:PATH> ...5 (=mycustompath)`*`]` **:a**`]`
- **-m, --mount** *`<str:{option1, option2, option3}> 2 (=option2)`*

### Either Arguments
- Either Arguments belong to one or multiple either groups.
- Either groups are noted with a vertical bar and an index.
- i.e. one group **-m, --mount |1**
- i.e. two groups **-m, --mount |1|2**
- Each either group argument can't be selected on the command-line if another argument from the same either group is present already.
- Either exclusion scope is per arguments siblings' level.

### Single Arguments
- Single Arguments are singleton at their siblings' level.
- Any other arguments at the same siblings' level throw an error.
- Single arguments are noted with a dot.
- i.e. **-m, --mount •**
- i.e. `[`**-m, --mount •**`]`

### Special Commands
- Special commands are related to current command-line argument.
- Special commands start with either '`:`' for usage or '`@`' for path.
- Both '`:`' and '`@`' can be used at the same time.
- '`:`' and '`@`' can be repeated three times each for verbosity.
- '`:`': Print argument's usage, and first nested arguments.
- '`::`': Print argument's usage, nested arguments and sub-nested arguments.
- '`:::`': Print argument's usage, and all nested arguments.
- '`@`': Print argument's path.
- '`@@`': Print argument's path with values.
- '`@@@`': Print argument's path with values and explicit notation.
- Parameters can be added: '`e`' for examples, '`h`' for hint, '`i`' for info.
- Examples: '`@:ehi`', '`::@h`', '`@@@:eh`', '`:::@@@he`', '`:i`'

