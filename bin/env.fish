if not contains "$HOME/môn mới/bin" $PATH
    # Prepending path in case a system-installed binary needs to be overridden
    set -x PATH "$HOME/môn mới/bin" $PATH
end
