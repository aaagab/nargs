# NARGS END-USER DOCUMENTATION
## NARGS ARGUMENTS SYNTAX
### About Nargs
`alias:` nargs<br>
`authors:` Gabriel Auger<br>
`deps:` cf09346e-b436-4259-b6dd-e56516b508a5|message|8.2.0|gpm<br>
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
- `yaml_syntax:` When 'enabled' means PyYAML is installed and yaml can be provided for arguments values types `.json` and `json`.

### User Option Files
- The following Nargs options can be modified with a user file: `pretty_help`, `pretty_msg`, `substitute`, `theme`.
- A '`.nargs-user.json`' or '`.nargs-user.yaml`' user file can be placed in either the application executable directory or the application configuration path as set by path_etc argument if any i.e. --path-etc.
- If both '`.nargs-user.json`' and '`.nargs-user.yaml`' are present then only '`.nargs-user.yaml`' is selected.
- If user option file is located at executable directory then user options overload matching program's options. If user option file is also located at application configuration then options overload any previously set matching options.
- `pretty_help`, `pretty_msg`, and `substitute` are boolean options. `theme` is a dictionary. In order to set `theme`'s keys and values, please read Nargs developer's documentation at section 'get_default_theme'.

### Argument Aliases Types
- Arguments' aliases can have any prefixes from list `['', '+', '-', '--', '/', ':', '_']`. i.e. `arg`, `+arg`, `-arg`, `--arg`, `/arg`, `:arg`, and `_arg`.
- Arguments' aliases accept branch index notation and may accept value(s).
- Each argument has a default alias. Default alias is the first alias on the argument's aliases list as shown in help or in usage.
- One char only aliases may be selected as flags. i.e. `a`, `+a`, `-a`, `--a`, `/a`, `:a`, and `_a`.
- A flag is an argument with at least a one char alias that is selected according to rules defined in Nargs developer's documentation at section 'Concatenated Flags Aliases'.
- A flags set is a group of flags related to a particular argument. Each argument may have a different flags set. Some arguments may not have a flags set depending on arguments definition.
- A flags set starts with 'at symbol' and contains at least one char. i.e. `@chuv` where 'c' is cmd, 'h' is 'help', 'u' is 'usage' and 'v' is 'version'.
- A flag may be repeated in a flags set depending on argument's definition. Flags order may not matter.
- Only the latest flag of a flags set may accept a value and may have branch index notation.
- A flag set may be concatenated to a command-line argument. i.e.: '`prog.py --usage@hip`'.
- 'at symbol' may be repeated to nest multiple flags sets. i.e.: '`prog.py @u@hip`' is the same as '`prog.py --usage --hint --info --path`'.
- When nesting multiple flags sets by using multiple 'at symbol' then the nested flags set is always related to the last flag used. i.e.: for '`prog.py @u@hip`' then flags set '`@hip`' is related to flag '`u`'.
- A flag does not accept explicit notation. A flags set does accept explicit notation.
- To know which argument is related to a flag, end-user can use the usage argument. i.e.: '`prog.py @u?`', or '`prog.py @u@h?`', or '`prog.py @u@hiu`'.

### Argument Aliases States
- Required: --mount, -m
- Optional:  **[**--mount, -m **]**
- Asterisk symbol means that nested arguments are available: `*`  **[**--mount, -m **]** or `*` --mount, -m
- When a required argument is omitted and argument accepts either no value(s), optional value(s), or required value(s) with default value(s) set then required argument is added implicitly and the selected alias set is the default alias.
- When a required argument with required value(s) is omitted and argument has not default value(s) set then an error is thrown.
- Omitted required argument process is repeated recursively and argument's required children may be added implicitly.
- An optional argument may still be required in-code by developer. Nargs only represents a small subset of arguments' logical rules.

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
- Arguments may be duplicated in multiple branches.
- Each argument's branch has its own subset of child arguments.
- Arguments may have multiple occurences per branch.
- Arguments branches and occurences described:
&nbsp;&nbsp;&nbsp;&nbsp;--parent<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`--self_1 (branch 1 occurence 1) --self (branch 1 occurence 2)`<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--child (relates only to branch 1<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`--self_2 (branch 2 occurence 1) --self (branch 2 occurence 2)`<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--child (relates only to branch 2)<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`--self_ (branch 3 occurence 1) --self (branch 3 occurence 2)`<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--child (relates only to branch 3)<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--sibling<br>

### Arguments Navigation
- Implicit navigation uses only aliases and values.
- Explicit navigation uses explicit notation with command-line symbols `+`, `=`, and `-`.
- Explicit navigation searches for aliases only in children arguments.
- Explicit navigation can reach any argument described in arguments tree vocabulary.
- Implicit navigation searches aliases in children' arguments, parents' arguments and parents' children.
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

### Arguments' Logical Properties
- An argument logical properties can be shown with usage argument. i.e.: '`prog.py --arg --usage --properties`'
- '`allow_parent_fork`' property is a boolean that describes if argument's parent may have fork(s) when argument is present.
- '`allow_siblings`' property is a boolean that describes if argument's siblings may be present when argument is present.
- '`fork`' property is a boolean that describes if argument's fork are allowed. To fork means to divide into two or more branches.
- '`need_child`' property is a boolean that describes if at least one argument's child must be provided when argument is present.
- '`repeat`' property is a string set with one option from '`append, error, replace`'. Property defines multiple argument's occurences behavior.
- '`repeat=append`' means multiple argument's occurences are allowed and for each occurence the same argument is kept but argument's '`_count`' internal property is incremented and new argument's values are appended to argument's values list.
- '`repeat=error`' means only one argument's occurence is allowed otherwise Nargs throws an error.
- '`repeat=replace`' means multiple argument's occurences are allowed and for each occurence a new argument is created and the previous argument is replaced and all the previous argument's children are removed. Argument's '`_count`' internal property is not incremented and new argument's values start a new argument's values list.
- '`required`' property is a boolean that describes if argument's must be present when argument's parent is present. '`required`' property has also been described in 'Argument Aliases States'.
- '`xor_groups`' property is a list of integers where each integer represents a group. Argument's siblings arguments with the same '`xor`' group can't be present at the same time on the command-line with any other argument from that group. It is the definition of '`xor`' which means '`exclusive or`'. Group scope is at the siblings level on argument's branch, it means that the same group name is not related if it is located on argument's parents or argument's children or if on same argument but on a different branch.

### Arguments Branch Index Notation
- Argument's branch index notation allows selecting a specific argument's occurence.
- Branch index notation consists in adding to argument's alias an underscore and an index number starting at one.
- Branch index notation's index is the argument occurence number.
- If only underscore is provided it means create a branch i.e.: '`prog --arg-one_`'
- Argument with '`fork`' property set to '`True`' allows to have an index greater than 1.
- Branch index notation examples: '`prog --help_1 --export_1`' or '`prog --arg_1 --arg_2`' or '`prog --arg_1 = --arg_2`' or '`prog --arg_ --arg_ --arg_`'.
- Argument's branches and argument's occurences per branch are not the same.
- Argument with '`repeat`' property set to either '`append`', or '`replace`' allows to have muliple occurences of an argument per branch.
- Argument's multiple occurences examples: '`prog --arg --arg`' or '`prog --arg_1 --arg_1`'.
- Explicit notation and branch index notation allows to select accurately an argument's branch in the arguments tree.

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
- Last flag on a flags set can also accepts values i.e. @chu: *`value`*

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
-  **[**--mount, -m **]**
- --mount, -m  *`<str:PATH> 1... (=mycustompath)`*
-  **[**--mount, -m  **[** *`<str:PATH> ...5 (=mycustompath)`* **]**  **]**
- --mount, -m  *`<str:{option1,option2,option3}> 2 (=option1, option2)`*

### Arguments Syntax Pitfall
- For value '`+4`' in command '`--arg +4`', '`+4`' is parsed as an explicit notation. In order to set '`+4`' as a value use '`--arg=+4`'.
- For alias '`+4`' in command '`--arg +4`', '`+4`' is parsed as an explicit notation. In order to set '`+4`' as an alias use explicit notation before argument '`--arg = +4`'
- For value '`@value`' in command '`--arg @value`', '`@value`' is parsed as a flags set. In order to set '`@value`' as a value use '`--arg=@value`'.
- For alias '`-value`' in command '`--arg -value`', '`-value`' is parsed as an alias. In order to set '`-value`' as a value use '`--arg=-value`'.
- Question mark alias '`?`' from usage may be misinterpreted by Bash as wildcard operator. If that happens end-user may want to use any other aliases provided for usage argument.
- Note: Basic overview of Nargs arguments parsing sequence: 'explicit notation' else 'alias notation' else 'flags notation' else 'value' else 'unknown input'. If 'alias notation' then 'known alias' else 'unknown argument' else 'value' else 'unknown input'. If 'flags notation' then flags set chars are tested as arguments (see Nargs /dev/get_args.py for detailed implementation).

