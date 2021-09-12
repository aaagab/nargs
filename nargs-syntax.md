# NARGS END-USER DOCUMENTATION
## NARGS ARGUMENTS SYNTAX
### About Nargs
`alias:` nargs<br>
`authors:` Gabriel Auger<br>
`deps:` cf09346e-b436-4259-b6dd-e56516b508a5|message|8.1.2|gpm<br>
`description:` Command-line Arguments Parser<br>
`filen_main:` main.py<br>
`installer:` gpm<br>
`licenses:` MIT<br>
`name:` Nested Arguments<br>
`timestamp:` 1620747900.8213155<br>
`uuid4:` 89d8676a-6b02-43fa-8694-e97de5680cd0<br>
`version:` 0.1.0<br>

### Nargs Options Explained
- `pretty_help:` When 'enabled' Nargs usage, and help are themed.
- `pretty_msg:` When 'enabled' Nargs system messages are themed.
- `substitute:` When 'enabled' strings on the command line with syntax \_\_input\_\_, \_\_hidden\_\_, \_\_input:label\_\_, \_\_hidden:label\_\_ trigger user prompt and strings are substituted with user input. Label must start with a letter and can only have letters or numbers. If only labels are provided then strings are substituted with values of matching environment variable names if any. i.e. \_\_input\_\_, \_\_input:username\_\_, \_\_USER\_\_, \_\_Session1\_\_ .
- `verbose:` None
- `yaml_syntax:` When 'enabled' means PyYAML is installed and yaml can be provided for arguments values types `.json` and `json`.

### User Option Files
- The following Nargs options can be modified with a user file: `pretty_help`, `pretty_msg`, `substitute`, `theme`.
- A '`.nargs-user.json`' or '`.nargs-user.yaml`' user file can be placed in either the application executable directory or the application configuration path as set by path_etc argument if any i.e. --path-etc.
- If both '`.nargs-user.json`' and '`.nargs-user.yaml`' are present then only '`.nargs-user.yaml`' is selected.
- If user option file is located at executable directory then user options overload matching program's options. If user option file is also located at application configuration then options overload any previously set matching options.
- `pretty_help`, `pretty_msg`, and `substitute` are boolean options. `theme` is a dictionary. In order to set `theme`'s keys and values, please read Nargs developer's documentation at section 'get_default_theme'.

### Argument Aliases Types
- Arguments' aliases can have any prefixes from list `['', '+', '-', '--', '/', ':', '_']`. i.e. `arg`, `+arg`, `-arg`, `--arg`, `/arg`, `:arg`, and `_arg`.
- Arguments' aliases accept index notation and may accept value(s).
- Each argument has a default alias. Default alias notation is only shown for required arguments that have at least two aliases. Default alias notation surrounds alias with single-quotes i.e.: `-a, '--arg'`. Single quotes are not part of the alias. 
- One char only aliases may be selected as flags. i.e. `a`, `+a`, `-a`, `--a`, `/a`, `:a`, and `_a`.
- A flag is an argument with at least a one char alias that is selected according to rules defined in Nargs developer's documentation at section 'Concatenated Flags Aliases'.
- A flags set is a group of flag related to a particular argument. Each argument may have a different flags set. Some arguments may not have a flags set depending on arguments definition.
- A flags set start with 'at symbol' and contains at least one char. i.e. `@chuv` where 'c' is cmd, 'h' is 'help', 'u' is 'usage' and 'v' is 'version'.
- A flag may be repeated in a flags set depending on argument's definition. Flags order does not matter.
- Only the latest flag of a flags set may accept a value and may have index notation.
- A flag does not accept explicit notation. A flags set does accept explicit notation.
- Flags set information details is only available through 'usage' argument.
- To see what flags set is available for an argument, user can type: '`prog.py --arg --usage`' or '`prog.py --arg --usage --flags`' for information on each flag.
- Only the the current argument's flags set information is available at a time.

### Argument Aliases States
- Required: -m, '--mount'
- Optional:  **[**-m, --mount **]**
- Asterisk symbol means that nested arguments are available: `*`  **[**-m, --mount **]** or `*` -m, '--mount'
- When a required argument is omitted and argument accepts either no value(s), optional value(s), or required value(s) with default value(s) set then required argument is added implicitly and the selected alias set is the default alias.
- When a required argument with required value(s) is omitted and argument has not default value(s) set then an error is thrown.
- Omitted required argument process is repeated recursively on implicitly added argument's required children.
- An optional argument may still be required in-code by developer. Nargs only represents a small subset of arguments' logical rules.

### Repeated Argument's options
- (`a`)ppend values: -m, '--mount' &a
- (`e`)rror if repeated: -m, '--mount' &e
- (`f`)ork new argument is created: -m, '--mount' &f
- (`r`)eplace previous argument and reset children (implicit): -m, '--mount'

### XOR Group Notation
- When argument has notation: -m, --mount ^1^3
- It means that argument is part of two '`exclusive either (XOR)`' groups: group 1 and group 3. An argument can belong to multiple XOR groups.
- XOR groups define siblings arguments' groups where any argument from a group can't be present at the same time on the command-line with any other siblings' arguments of the same group.
- i.e. sibling argument with notation '-u, --unmount ^3' can't be present at the same time with argument '-m, --mount ^1^3'.

### Arguments Tree Vocabulary
- Arguments tree structure related to --self argument:
&nbsp;&nbsp;&nbsp;&nbsp;--root-arg<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--ancestor<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--grand-parent<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--parent<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`--self`<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--child<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--sibling<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--uncle<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--grand-uncle<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--ancestor-uncle<br>
- `--self` is the current argument.
- All `--self`'s parents may be called ancestors. The oldest ancestor is the root argument.

### Arguments Navigation
- Implicit navigation uses only aliases and values.
- Explicit navigation uses explicit notation with command-line symbols `+`, `=`, and `-`.
- Explicit navigation searches for aliases only in children arguments.
- Explicit navigation can reaches any argument described in arguments tree vocabulary.
- Implicit navigation searches aliases in children' arguments, parents' arguments and parents' arguments' children.
- Command-line symbols `+`, `=`, and `-` help to explicitly navigate arguments' tree.
- Explicit navigation with command-line symbols `+`, `=`, and `-` may be omitted most of the time.
- Explicit navigation is required for an alias when selected alias is also present either in children's arguments, parents' arguments, or parents' children arguments.
- Command-line `+` symbol may be concatenated `+++` or used with a multiplier `+3`.
- Explicit navigation allows faster arguments parsing.
- Argument's alias is always required after explicit notation.
- i.e.(implicit): > 'prog --self --child --sibling --grand-parent --grand-uncle --ancestor-uncle'.
- i.e.(explicit): > 'prog --self `-` --child `+` --sibling `++` --grand-parent `=` --grand-uncle `+` --ancestor-uncle'.
- 'prog --self `-` --child'.
- 'prog --self `=` --sibling'.
- 'prog --self `+` --parent'.
- 'prog --self `+` --uncle'.
- 'prog --self `++` --grand-parent'.
- 'prog --self `++` --grand-uncle'.
- 'prog --self `+++` --ancestor'.
- 'prog --self `+++` --ancestor-uncle'.
- 'prog --self `++++` --root-arg'.
- 'prog --self `+4` --root-arg'.
- Explicit navigation allows end-user to go back and forth to selected arguments in order to add values or nested arguments.

### Arguments Index Notation
- Argument's index notation allows selecting a specific argument's occurence.
- Index notation consists in adding to argument's alias an underscore and an index number starting at one.
- Index notation's index is the argument occurence number.
- Argument with repeat option set to 'fork' allows to have an index greater than 1.
- Argument with repeat option set to either 'append', 'error', or 'replace' only allows to have the index equals to 1.
- Index notation examples: 'prog --help_1 --export_1' or 'prog --arg_1 --arg_2' or 'prog --arg_1 = --arg_2'.
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
- Required value(s) are added implicitly when argument's default values are set and argument is either present or required.

### Argument Special Values Types
-  *`dir`*: existing directory.
-  *`file`*: existing file.
-  *`path`*: existing directory or file.
-  *`vpath`*: existing or non-existing directory or file.
-  *`json`*: JSON/YAML string.
-  *`.json`*: .json/.yml/.yaml file or JSON/YAML string.
- Relative paths are resolved for types dir, file, path, vpath, and .json.
- JSON strings can be single quoted.

### Aliases Equal/Colon Values Notation
- All arguments's aliases accept equal/colon values notation.
- i.e. --argument=' *`value1 value2 "this is value3"`*'
- i.e. --argument=" *`value1 value2 'this is value3'`*"
- i.e. -a=" *`value1 value2 'this is value3'`*"
- i.e. argument=" *`value1 value2 'this is value3'`*"
- i.e. argument= *`value1`*
- i.e. --argument:' *`value1 value2 "this is value3"`*'
- i.e. --argument:" *`value1 value2 'this is value3'`*"
- i.e. -a:" *`value1 value2 'this is value3'`*"
- i.e. argument:" *`value1 value2 'this is value3'`*"
- i.e. argument: *`value1`*
- Values notation is useful to prevent values to be mistaken for aliases.
- Values notation allows faster command-line parsing.

### Argument Number of Values
- required 1 value:  *`<str>`* 
- optional 1 value:  **[** *`<str>`* **]**
- required int value(s):  *`<str> 5`*
- optional int value(s):  **[** *`<str> 3`* **]**
- required min int to max int:  *`<str> 2..3`*
- optional min int to max int:  **[** *`<str> 4..5`* **]**
- required min 1 to max infinite:  *`<str> ...`*
- optional min 1 to max infinite:  **[** *`<str> ...`* **]**
- required min int to max infinite:  *`<str> 7...`*
- optional min int to max infinite:  **[** *`<str> 8...`* **]**
- required min 1 to int:  *`<str> ...3`*

### Argument Help Syntax Examples
-  **[**-m, --mount &e **]**
- -m, '--mount'  *`<str:PATH> 1... (=mycustompath)`*
-  **[**-m, --mount  **[** *`<str:PATH> ...5 (=mycustompath)`* **]** &a **]**
- -m, '--mount'  *`<str:{option1,option2,option3}> 2 (=option1, option2)`*

