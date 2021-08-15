# NARGS END-USER DOCUMENTATION
## NARGS ARGUMENTS SYNTAX
### About Nargs
`alias:` nargs<br>
`authors:` 'Gabriel Auger'<br>
`deps:` cf09346e-b436-4259-b6dd-e56516b508a5|message|8.1.2|gpm<br>
`description:` Command-line Arguments Parser<br>
`filen_main:` main.py<br>
`installer:` gpm<br>
`licenses:` MIT<br>
`marc:` {"harry": {}, "tom": {}}<br>
`name:` Nested Arguments<br>
`timestamp:` 1620747900.8213155<br>
`uuid4:` 89d8676a-6b02-43fa-8694-e97de5680cd0<br>
`version:` 0.1.0<br>

### Nargs Modes Explained
- `cached_dfn:` When 'enabled' arguments definition is cached to enable faster arguments parsing.
- `pretty:` When 'enabled' Nargs messages, usage, and help are themed.
- `substitute:` When 'enabled' strings on the command line with syntax \_\_input\_\_, \_\_hidden\_\_, \_\_input:label\_\_, \_\_hidden:label\_\_ trigger user prompt and strings are substituted with user input. Label must start with a letter and can only have letters or numbers. If only labels are provided then strings are substituted with values of matching environment variable names if any. i.e. \_\_input\_\_, \_\_input:username\_\_, \_\_USER\_\_, \_\_Session1\_\_ .
- `usage_on_root:` When 'enabled' Nargs throws usage when only root argument is provided.
- `yaml_syntax:` When 'enabled' means PyYAML is installed and yaml can be provided for arguments values types `.json` and `json`.

### Argument Aliases Types
- `built-in aliases` i.e. :argument. Start with a colon, accept index notation and accept value(s).
- `concatenated aliases` i.e. -abcd. Start with a dash, each char represents one short alias argument. They don't accept value(s) and they don't accept index notation. All arguments must have the same parent.
- `default alias` i.e. --info. . Each argument has a default alias. Default alias is the alias that ends with a dot when aliases are listed in help or usage. Dot symbol is not part of the alias. It is just to identify the default alias. Dot is not added for argument with only one alias.
- `dashless aliases` i.e. argument. Start with a letter or a number, accept index notation and accept value(s).
- `long aliases` i.e. --argument. Start with double dashes, may have multiple chars, accept index notation and accept value(s).
- `short aliases` i.e. -a. Start with single dash, have only one char, accept index notation and accept value(s).

### Argument Aliases State
- required: -m, --mount.
- optional:  **[**-m, --mount **]**
- available nested arguments: `*`  **[**-m, --mount **]** or `*` -m, --mount.
- When a required argument is omitted and argument accepts either no value(s), optional value(s), or required value(s) with default value(s) set then required argument is added implicitly and the selected alias set is the default alias.
- When a required argument with required value(s) is omitted and argument has not default value(s) set then an error is thrown.
- Omitted required argument process is repeated recursively on implicitly added argument's required children.

### Repeated Argument's option
- (`a`)ppend values: -m, --mount. &a
- (`e`)xit if repeated: -m, --mount. &e
- (`f`)ork new argument is created: -m, --mount. &f
- (`r`)eplace previous argument and reset children (implicit): -m, --mount.

### Arguments Navigation
- Implicit navigation uses only aliases and values.
- Explicit navigation uses explicit notation with command-line symbols `+` and `-`.
- Explicit navigation searches for aliases only in children arguments.
- Implicit navigation searches aliases in children' arguments, parents' arguments and parents' arguments' children.
- Command-line symbols `+` and `-` help to explicitly navigate arguments' tree.
- Explicit navigation with command-line symbols `+` and `-` may be omitted most of the time.
- Explicit navigation is required for an alias when selected alias is also present either in children's arguments, parents' arguments, or parents' children arguments.
- Command-line `+` symbol may be concatenated `+++` or used with a multiplier `+3`.
- Explicit navigation allows faster arguments parsing.
- Explicit notation only select an argument relative siblings level that is why an argument's alias is required after explicit notation.
- i.e.(implicit): > prog :help --export html --to file.html.
- i.e.(explicit): > prog `-` :help `-` --export html `+` --to file.html.
- Explicit navigation allows end-user to go back and forth to selected arguments in order to add values or nested arguments.

### Arguments Index Notation
- Argument's index notation allows selecting a specific argument's occurence.
- Index notation consists in adding to argument's alias an underscore and an index number starting at one.
- Index notation's index is the argument occurence number.
- Argument with repeat option set to 'fork' allows to have an index greater than 1
- Argument with repeat option set to either 'append', 'exit', or 'replace' only allows to have the index equals to 1.
- Index notation examples: prog :help_1 --export_1 or prog --arg_1 + --arg_2
- Explicit notation and index notation allows to select accurately an argument's occurence in the arguments tree.

### Argument Values
- required:  *`<str>`*
- optional:  **[** *`<str>`* **]**
- default:  *`<str> (=default_value)`* or  *`<int:VALUE> (=1, 3, 4, 5)`*
- preset:  *`{str:1, 2, 3}`*
- preset with label:  *`{str:1(value1),2(value2),3(value3)}`*
- label:  *`<type:label>`* i.e.  *`<str:PATH>`*
- standard types:  *`str`*,  *`bool`*,  *`int`*, and  *`float`*
- Boolean argument's value(s) can be either case-insensitive string  *`true`*, case-insensitive string  *`false`*,  *`0`*, or  *`1`* where  *`0`* is False and  *`1`* is True. i.e.  *`prog.py true True 1 0 False falsE`*
-  Required value(s) are added implicitly when argument's default values are set and argument is either present or required.

### Argument Special Values Types
-  *`dir`*: existing directory.
-  *`file`*: existing file.
-  *`path`*: existing directory or file.
-  *`vpath`*: existing or non-existing directory or file.
-  *`json`*: JSON/YAML string.
-  *`.json`*: .json/.yaml/.yml file or JSON/YAML string.
- Relative paths are resolved in types dir, file, path, vpath, and .json.
- JSON strings can be single quoted.

### Aliases Equals Values Notation
- `long aliases`, `short aliases`, and `dashless aliases` arguments accept equals values notation.
- i.e. --argument=' *`value1 value2 "this is value3"`*'
- i.e. --argument=" *`value1 value2 'this is value3'`*"
- i.e. -a=" *`value1 value2 'this is value3'`*"
- i.e. argument=" *`value1 value2 'this is value3'`*"
- i.e. argument= *`value1`*
- Values notation is useful to prevent values to be mistaken for aliases.
- Values notation also increases command-line parsing speed.

### Argument Number of Values
- required 1 value:  *`<str>`* 
- optional 1 value:  **[** *`<str>`* **]**
- required int value:  *`<str> 5`*
- optional int value:  **[** *`<str> 3`* **]**
- required min int to max int:  *`<str> 2..3`*
- optional min int to max int:  **[** *`<str> 4..5`* **]**
- required min 1 to max infinite:  *`<str> ...`*
- optional min 1 to max infinite:  **[** *`<str> ...`* **]**
- required min int to max infinite:  *`<str> 7...`*
- optional min int to max infinite:  **[** *`<str> 8...`* **]**
- required min 1 to int:  *`<str> ...3`*

### Argument Help Syntax Examples
-  **[**-m, --mount &e **]**
- -m, --mount.  *`<str:PATH> 1... (=mycustompath)`*
-  **[**-m, --mount  **[** *`<str:PATH> ...5 (=mycustompath)`* **]** &a **]**
- -m, --mount.  *`<str:{option1,option2,option3}> 2 (=option1, option2)`*

