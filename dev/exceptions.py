#!/usr/bin/env python3
class EndUserError(Exception):
    def __init__(self, errors):
        self.errors=errors
        if not isinstance(errors, dict):
            raise Exception("EndUserError errors argument must be a dict.")
        
        if "attributes" not in errors:
            errors["attributes"]=dict()

        if "cmd_line" not in errors:
            errors["cmd_line"]=None

        if "node_usage" not in errors:
            errors["node_usage"]=None

        if "show_usage" not in errors:
            errors["show_usage"]=False

        if "stack_trace" not in errors:
            errors["stack_trace"]=None

        if "show_stack" not in errors:
            errors["show_stack"]=False

        if "error_type" not in errors or errors["error_type"] is None:
            raise Exception("EndUserError 'error_type' attribute not found in errors dict.")

        if "message" not in errors:
            raise Exception("EndUserError 'message' attribute not found in errors dict.")

        self.full_message=None
        if isinstance(errors["message"], list):
            self.full_message="\n".join(errors["message"])
        elif isinstance(errors["message"], str):
            self.full_message=errors["message"]
        else:
            raise Exception("EndUserError 'message' attribute must be of type {} or {}.".format(str, list))

        if "prefix" in errors and errors["prefix"] is not None:
            if "cmd_line" in errors and errors["cmd_line"] is not None:
                self.full_message="{}: '{}' {}".format(
                    errors["prefix"],
                    errors["cmd_line"],
                    self.full_message,
                )
            else:
                self.full_message="{}: {}".format(
                    errors["prefix"],
                    self.full_message,
                )

        else:
            errors["prefix"]=None

        self.full_message=self.full_message.format(**errors["attributes"])

        super().__init__(self.full_message)


class DeveloperError(Exception):
    pass

class ErrorTypes():
    def __init__(self):
        self.ArgumentChildIsNeeded = "ArgumentChildIsNeeded"
        self.ArgumentNoValuesAllowed = "ArgumentNoValuesAllowed"
        self.AllowParentForkError = "AllowParentForkError"
        self.AllowSiblingsError = "AllowSiblingsError"
        self.BuiltinVersionNotProvided = "BuiltinVersionNotProvided"
        self.ClosingQuotationError = "ClosingQuotationError"
        self.CmdElementTypeError = "CmdElementTypeError"
        self.CmdQueryValuesMisMatch = "CmdQueryValuesMisMatch"
        self.ExplicitNotationEndError = "ExplicitNotationEndError"
        self.ExplicitNotationOutOfBound = "ExplicitNotationOutOfBound"
        self.JsonSyntaxError = "JsonSyntaxError"
        self.FileNotFound = "FileNotFound"
        self.LoadDictionaryError = "LoadDictionaryError"
        self.MaxValuesNumReached = "MaxValuesNumReached"
        self.MetadataKeyNotFound = "MetadataKeyNotFound"
        self.MinValuesNumNotReached = "MinValuesNumNotReached"
        self.NeedValueError = "NeedValueError"
        self.PathNotADirectory = "PathNotADirectory"
        self.PathNotAFile = "PathNotAFile"
        self.PathNotFound = "PathNotFound"
        self.OptionQueryError="OptionQueryError"
        self.OptionCmdError="OptionCmdError"
        self.OptionCmdError="OptionCmdError"
        self.QuestionMarkError="QuestionMarkError"
        self.QueryAttributeNotFound="QueryAttributeNotFound"
        self.QueryRecursionError="QueryRecursionError"
        self.QueryValueTypeError="QueryValueTypeError"
        self.RepeatError = "RepeatError"
        self.RequiredArgumentMissing = "RequiredArgumentMissing"
        self.RootArgumentNotFound="RootArgumentNotFound"
        self.UnknownArgument = "UnknownArgument"
        self.UsageFromValueError = "UsageFromValueError"
        self.UsageLevelValueError = "UsageLevelValueError"
        self.ValueNotFound = "ValueNotFound"
        self.ValuesNotAllowed = "ValuesNotAllowed"
        self.ValueTypeError = "ValueTypeError"
        self.XorError = "XorError"
        self.YamlSyntaxError = "YamlSyntaxError"

        
