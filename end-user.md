# NARGS END-USER DOCUMENTATION

## Table of Contents
- [NARGS ARGUMENTS SYNTAX](#nargs-arguments-syntax)
    - [About Nargs](#about-nargs)
    - [Nargs Options State](#nargs-options-state)
    - [Nargs Options Explained](#nargs-options-explained)
    - [User Option Files](#user-option-files)
    - [Argument Aliases Types](#argument-aliases-types)
    - [Argument Aliases States](#argument-aliases-states)
    - [Arguments Tree Vocabulary](#arguments-tree-vocabulary)
    - [Arguments Navigation](#arguments-navigation)
    - [Arguments' Logical Properties](#arguments-logical-properties)
    - [Argument Values](#argument-values)
    - [Argument Special Values Types](#argument-special-values-types)
    - [Aliases Equal/Colon Values Notation](#aliases-equalcolon-values-notation)
    - [Argument Number of Values](#argument-number-of-values)
    - [Argument Usage Full Syntax Examples](#argument-usage-full-syntax-examples)
    - [Arguments Syntax Pitfalls](#arguments-syntax-pitfalls)

## NARGS ARGUMENTS SYNTAX
### About Nargs
`alias:` nargs<br>
`authors:` Gabriel Auger<br>
`deps:` cf09346e-b436-4259-b6dd-e56516b508a5|message|9.0.0|gpm<br>
`description:` Command-line Arguments Parser<br>
`filen_main:` main.&#65279;py<br>
`installer:` gpm<br>
`licenses:` MIT<br>
`name:` Nested Arguments<br>
`timestamp:` 1670271546.655436<br>
`uuid4:` 89d8676a-6b02-43fa-8694-e97de5680cd0<br>
`version:` 4.0.0<br>

### Nargs Options State
- pretty_help: `enabled`
- pretty_msg: `enabled`
- substitute: `disabled`
- yaml_syntax: `enabled`

### Nargs Options Explained
- `pretty_help:` When 'enabled' Nargs usage, and help are themed.
- `pretty_msg:` When 'enabled' Nargs system messages are themed.
- `substitute:` When 'enabled' strings on the command line with syntax \_\_input\_\_, \_\_hidden\_\_, \_\_input:label\_\_, \_\_hidden:label\_\_ trigger user prompt and strings are substituted with user input. Label must start with a letter and can only have letters or numbers. If only labels are provided then strings are substituted with values of matching environment variable names if any. i.e. \_\_input\_\_, \_\_input:username\_\_, \_\_USER\_\_, \_\_Session1\_\_ .
- `yaml_syntax:` When 'enabled' means PyYAML is installed and YAML can be provided for arguments values types `.json` and `json`.

### User Option Files
- The following Nargs options can be modified with a user file: `pretty_help`, `pretty_msg`, `substitute`, `theme`.
- A '`.nargs-user.json`' or '`.nargs-user.yaml`' user file can be placed in either the application executable directory or the application configuration path as set by path_etc argument if any i.e. --path-etc.
- If both '`.nargs-user.json`' and '`.nargs-user.yaml`' are present then only '`.nargs-user.yaml`' is selected.
- If user option file is located at executable directory then user options overload matching program's options. If user option file is also located at application configuration path then options overload any previously set matching options.
- `pretty_help`, `pretty_msg`, and `substitute` are Boolean options. `theme` is a dictionary. In order to set `theme`'s keys and values, please read Nargs developer's documentation at section 'get_default_theme'.

### Argument Aliases Types
- Arguments' aliases can have any prefixes from list `['', '+', '-', '--', '/', ':', '_']`. i.e. `arg, +arg, -arg, --arg, /arg, :arg, _arg`.
- Arguments' aliases accept branch index notation and may accept value(s).
- Each argument has a default alias. Default alias is the first alias on the argument's aliases list as shown in help or in usage.
- One char only aliases may be selected as flags. i.e. `a, +a, -a, --a, /a, :a, _a`.
- A flag is an argument with at least a one char alias that is selected according to rules defined in Nargs developer's documentation at section 'Concatenated Flag Aliases'.
- In order to see available flag sets end-user can provide command-line '`prog.py --usage --flags`'
- A flag set is a group of flags related to a particular argument. Each argument may have a different flag set. Some arguments may not have a flag set depending on arguments definition.
- A flag set starts with a one char alias and its prefix if any and it contains at least another char. i.e. '`-huv`' where '`h`' is 'help', '`u`' is 'usage' and '`v`' is 'version'.
- Root argument aliases may start with a flag set. In that case this flag set is the one available on first command-line argument or when explicit notation reaches level 0.
- A flag may be repeated in a flag set depending on argument's definition. Flags order may not matter.
- Only the latest flag of a flag set may accept a value and may have branch index notation.
- 'at symbol' may be repeated to nest multiple flag sets. i.e.: '`prog.py` `-uhip`' is the same as '`prog.py --usage --hint --info --path`'.
- A flag does not accept explicit notation. Explicit notation can only be applied to first flag of the set. Then all other flags are selected are part of the flags set of the previous flag.
- End-user can rely on usage argument to get flag information i.e.: '`prog.py` `-u?`', or '`prog.py` `-uh?`', or '`prog.py` `-uhiu`'.

### Argument Aliases States
- Required: `--mount, -m`
- Optional:  **[**`--mount, -m` **]**
- Asterisk symbol means that nested arguments are available: `*`  **[**--mount, -m **]** or `*` --mount, -m
- When a required argument is omitted and argument accepts either no value(s), optional value(s), or required value(s) with default value(s) set then required argument is added implicitly and the selected alias set is the default alias.
- When a required argument with required value(s) is omitted and argument has not default value(s) set then an error is thrown.
- Omitted required argument process is repeated recursively and argument's required children may be added implicitly.
- An optional argument may still be required in-code by developer. Nargs only represents a small subset of arguments' logical rules.

### Arguments Tree Vocabulary
- Arguments tree structure related to --self argument:<br>&nbsp;&nbsp;&nbsp;&nbsp;--root<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--ancestor<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--gd-parent<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--parent<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`--self`<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--child<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--sibling<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--uncle<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--gd-uncle<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--ancestor-uncle<br>
- `--self` is the current argument.
- All `--self`'s parents may be called ancestors. The oldest ancestor is the root argument.
- Arguments may be duplicated in multiple branches.
- Each argument's branch has its own subset of child arguments.
- Arguments may have multiple occurrences per branch.
- Arguments branches and occurrences described for command-line '--parent --self --child --self --child --self --child --sibling':<br>&nbsp;&nbsp;&nbsp;&nbsp;--parent<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`--self (branch 1)`<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--child (relates only to branch 1)<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`--self (branch 2)`<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--child (relates only to branch 2)<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`--self (branch 3)`<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--child (relates only to branch 3)<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--sibling<br>

### Arguments Navigation
- Implicit navigation uses only aliases and values.
- Explicit navigation uses explicit notation with command-line symbols `-`, `=`, and `+`.
- Explicit navigation searches for aliases only in children arguments.
- Explicit navigation can reach any argument described in arguments tree vocabulary.
- Implicit navigation searches aliases in children' arguments, parents' arguments and parents' children.
- Command-line symbols `-`, `=`, and `+` help to explicitly navigate arguments' tree.
- Explicit navigation with command-line symbols `-`, `=`, and `+` may be omitted most of the time.
- Explicit navigation is needed for an alias when selected alias is also present either in children's arguments, parents' arguments, or parents' children arguments and is not available implicit navigation.
- For similar aliases implicit notation will search first in the children and if not found it will stop at the younger ancestor child alias that matches.
- Explicit navigation can reach ancestors with `-`, siblings with `=`, and children with `+`.
- Command-line `-` symbol may be concatenated `---` or used with a multiplier `-3`.
- Explicit navigation allows faster arguments parsing.
- Argument's alias or flag set is always required after explicit notation.
- i.e.(implicit): > 'prog --ancestor --gd-parent --parent --self --child --sibling --gd-parent --gd-uncle --ancestor-uncle'.
- i.e.(explicit): > 'prog `+` --ancestor `+` --gd-parent `+` --parent `+` --self `+` --child `-` --sibling `--` --gd-parent `=` --gd-uncle `-` --ancestor-uncle'.
- 'prog --ancestor --gd-parent --parent --self `+` --child'.
- 'prog --ancestor --gd-parent --parent --self `=` --sibling'.
- 'prog --ancestor --gd-parent --parent --self `-` --parent'.
- 'prog --ancestor --gd-parent --parent --self `-` --uncle'.
- 'prog --ancestor --gd-parent --parent --self `--` --gd-parent'.
- 'prog --ancestor --gd-parent --parent --self `--` --gd-uncle'.
- 'prog --ancestor --gd-parent --parent --self `---` --ancestor'.
- 'prog --ancestor --gd-parent --parent --self `---` --ancestor-uncle'.
- 'prog --ancestor --gd-parent --parent --self `----` --root'.
- 'prog --ancestor --gd-parent --parent --self `-4` --root'.
- Explicit navigation allows end-user to go back and forth to selected arguments in order to add values or nested arguments.

### Arguments' Logical Properties
- An argument logical properties can be shown with usage argument. i.e.: '`prog.py --arg --usage --properties`'
- '`allow_parent_fork`' property is a bool that describes if argument's parent may have fork(s) when argument is present.
- '`allow_siblings`' property is a bool that describes if argument's siblings may be present when argument is present.
- '`need_child`' property is a bool that describes if at least one argument's child must be provided when argument is present.
- '`preset`' property is a bool that defines if an argument is a preset argument. A preset argument is added implicitly if only its parent is present with no children.
- '`repeat`' property is a string set with one option from '`append, error, fork, replace`'. Property defines multiple argument's occurrences behavior.
- '`repeat=append`' means multiple argument's occurrences are allowed and for each occurrence the same argument is kept but argument's '`_count`' internal property is incremented and new argument's values are appended to argument's values list.
- '`repeat=error`' means only one argument's occurrence is allowed otherwise Nargs throws an error.
- '`repeat=fork`' means that argument's forks are allowed. To fork means to divide into two or more branches.
- '`repeat=replace`' means multiple argument's occurrences are allowed and for each occurrence a new argument is created, and the previous argument is replaced, and all the previous argument's children are removed. Argument's '`_count`' internal property is not incremented and new argument's values start a new argument's values list.
- '`required`' property is a bool that describes if argument's must be present when argument's parent is present. '`required`' property has also been described in 'Argument Aliases States'.
- '`xor_groups`' property is a list of integers where each integer represents a group. Argument's siblings arguments with the same '`xor`' group can't be present at the same time on the command-line with any other argument from that group. It is the definition of '`xor`' which means '`exclusive or`'. Siblings arguments have the same parent argument. Group scope is at the node level on argument's branch, it means that the same group name is not related if it is located on argument's parents or argument's children or if on same argument but on a different branch.

### Argument Values
- required: *`<str>`*
- optional:  **[***`<str>`* **]**
- default: *`<str> (=default_value)`* or *`<int> (=1, 3, 4, 5)`*
- preset: *`{str:1, 2, 3}`*
- preset with label: *`{str:1(value1),2(value2),3(value3)}`*
- label: *`<type:label>`* i.e. *`<str:PATH>`*
- standard types: *`str`*, *`bool`*, *`int`*, and *`float`*
- Boolean argument's value(s) can be either case-insensitive string *`true`*, case-insensitive string *`false`*, *`0`*, or *`1`* where *`0`* is False and *`1`* is True. i.e. *`prog.py true True 1 0 False falsE`*
- Required value(s) are added implicitly when argument's default values are set, and argument is either present with no given values or required and added implicitly.

### Argument Special Values Types
- *`dir`*: existing directory.
- *`file`*: existing file.
- *`path`*: existing directory or file.
- *`vpath`*: existing or non-existing directory or file.
- *`json`*: JSON/YAML string.
- *`.json`*: .json/.yml/.yaml file or JSON/YAML string.
- Relative paths are resolved according to terminal current path for types dir, file, path, vpath, and .json.
- JSON strings can be single quoted.

### Aliases Equal/Colon Values Notation
- All arguments' aliases accept equal/colon values notation. (Warning: external single quotes trigger error on Windows CMD terminal)
- i.e. --argument`='value1 value2 "this is value3"'`
- i.e. --argument`="value1 value2 'this is value3'"`
- i.e. -a`="value1 value2 'this is value3'"`
- i.e. argument`="value1 value2 'this is value3'"`
- i.e. argument`=value1`
- i.e. --argument`:'value1 value2 "this is value3"'`
- i.e. --argument`:"value1 value2 'this is value3'"`
- i.e. -a`:"value1 value2 'this is value3'"`
- i.e. argument`:"value1 value2 'this is value3'"`
- i.e. argument`:value1`
- Values notation is useful to prevent values to be mistaken for aliases.
- Values notation allows faster command-line parsing.
- Last flag on a flag set can also accepts values i.e. `-chu:value`

### Argument Number of Values
- required 1 value: *`<str>`* 
- optional 1 value:  **[***`<str>`* **]**
- required int value(s): *`<str> 5`*
- optional int value(s):  **[***`<str> 3`* **]**
- required min int to max int: *`<str> 2..3`*
- optional min int to max int:  **[***`<str> 4..5`* **]**
- required min 1 to max infinite: *`<str> ...`*
- optional min 1 to max infinite:  **[***`<str> ...`* **]**
- required min int to max infinite: *`<str> 7...`*
- optional min int to max infinite:  **[***`<str> 8...`* **]**
- required min 1 to int: *`<str> ...3`*

### Argument Usage Full Syntax Examples
-  **[**--mount, -m **]**
- --mount, -m *`<str:PATH> 1... (=mycustompath)`*
-  **[**--mount, -m  **[***`<str:PATH> ...5 (=mycustompath)`* **]**  **]**
- --mount, -m *`<str:{option1,option2,option3}> 2 (=option1, option2)`*

### Arguments Syntax Pitfalls
- If an alias or flags notation is mistyped on the command-line, it may be use as a value if previous argument accept values.
- If a flags notation turns-out to be the same as a reachable alias, then the alias is going to be selected instead of the flags notation.
- If multiple same aliases are present and user uses implicit notation on the command-line, the argument selected may be different than what the argument expected.
- Question mark alias '`?`' from usage may be misinterpreted by Bash as wildcard operator. If that happens end-user may want to use any other aliases provided for usage argument.
- For values notation on Windows CMD terminal emulator, command-line `prog.py --arg='value value value'` single quotes trigger shlex `ValueError: No closing quotation`. Instead end-user must type `prog.py --arg="value value value"` or `prog.py --arg="value1 value2 'value 3'"`.
- Note: Basic overview of Nargs arguments parsing sequence: 'explicit notation' else 'alias notation' else 'flags notation' else 'value' else 'unknown input'. If 'alias notation' then 'known alias' else 'flags notation' else 'value' else 'unknown input'. If 'flags notation' then flag set chars are tested as arguments (see Nargs /dev/get_args.py for detailed implementation).

