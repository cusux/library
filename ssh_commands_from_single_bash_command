# Executing SSH commands from a single Bash command
Some use cases need a single Bash command to perform multiple commands over an SSH connection on a remote instance.
This can be the case with, for example, Jenkins jobs.

A valid approach is to pass the multi-line remote command as a single string, using multiple layers of bash variable interpolation as follows:
```bash
ssh user@server "$( cat <<'EOT'
echo "These commands will be run on: $( uname -a )"
echo "They are executed by: $( whoami )"
EOT
)"
```
The solution above fixes this problem in the following manner:
 1. `ssh user@server` is parsed by bash, and is interpreted to be the `ssh` command, followed by an argument `user@server` to be passed to the `ssh` command.
 2. `"` begins an interpolated string, which when completed, will comprise an argument to be passed to the `ssh` command, which in this case will be interpreted by `ssh` to be the remote command to execute as `user@server`.
 3. `$(` begins a command to be executed, with the output being captured by the surrounding interpolated string.
 4. `cat` is a command to output the contents of whatever file follows. The output of `cat` will be passed back into the capturing interpolated string.
 5. `<<` begins a bash *heredoc*.
 6. `'EOT'` specifies that the name of the *heredoc* is EOT. The single quotes `'` surrounding `EOT` specifies that the *heredoc* should be parsed as a *nowdoc*, which is a special form of *heredoc* in which the contents do not get interpolated by bash, but rather passed on in literal format.
 7. Any content that is encountered between `<<'EOT'` and `<newline>EOT<newline>` will be appended to the *nowdoc* output
 8. `EOT` terminates the *nowdoc*, resulting in a *nowdoc* temporary file being created and passed back to the calling `cat` command. `cat` outputs the *nowdoc* and passes the output back to the capturing interpolated string.
 9. `)` concludes the command to be executed.
10. `"` concludes the capturing interpolated string. The contents of the interpolated string will be passed back to ssh as a single command line argument, which `ssh` will interpret as the remote command to execute as `user@server`.

If you need to avoid using external tools like `cat`, and don't mind having two statements instead of one, use the read built-in with a *heredoc* to generate the SSH command:
```bash
IFS='' read -r -d '' SSH_COMMAND <<'EOT'
echo "These commands will be run on: $( uname -a )"
echo "They are executed by: $( whoami )"
EOT
ssh user@server "${SSH_COMMAND}"
```
