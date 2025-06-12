#!/usr/bin/awk -f
# Usage: $0 SRC.json > DST.json
# Update JSON document from SRC to stdout overwriting properties from environment variables
# if an env var with same name is set and not empty


BEGIN {
    FS = "[[:space:]]*:[[:space:]]*"
    RS = "[[:space:]]*[{,}]\n*"
    ORS = ""
    OFS = ": "
    printf "{\n"
}

{
    if (match($0, /^[[:space:]]*["'][A-Z0-9a-z_]+["'][[:space:]]*:/)) {

        if (recount > 0) {
            # omit tailing comma on last record by printing the separator before the record #
            print ",\n"
        }

        property = variable = $1

        # clean up property name#
        gsub(/^[[:space:]]*["']|["'][[:space:]]*$/, "", variable)

        value = ENVIRON[variable]

        if (value) {
            # replace with environment variable if set
            gsub(/"/, "\\\"", value)
            value = sprintf("\"%s\"", value)

        } else {
            # value is all fields but the first (ex. there was a : in the value)
            sub($1 FS, "")
            value = $0
        }

        # property still have the original quoting and spacing
        print property, value

        recount++
    }
}

END {
    printf "\n}\n"
}
