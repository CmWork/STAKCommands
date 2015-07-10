# ModifyPropertyValueCommand

Modify property values of the target (child) command.

<font size="2">File Reference: stc_testmethodology.xml</font>

<text>Properties</text>

### CurlyBraceSubstitution: "Substitution characters for { } characters" (input:string)

Optional two characters used to use in place of {} to work around a known problem with the GUI's parsing of {}.

* default - 
### VariableDelimiter: "Variable Delimiter" (input:string)

Variable Delimiter holds exactly two (different) characters that identify the start and end of a variable expression.

* default - []
### PropertyExpressionList: "Property Expressions" (input:string)

List of expressions to be evaluated and replace the values of their corresponding properties.

* default - 
### ErrorMsg: "Error Message" (output:string)

Holds the last error message recorded by the command.

* default - 
