# --------------MongoDB Connection Configuration----------

# Name of the database to use.
name = "METU"

# Port of the connection.
port = 27017

#  Host url for the connection.
host_url = "mongodb+srv://onlineReader:<password>@metu.foimezd.mongodb.net/?retryWrites=true&w=majority"

# Alias of the connection.
alias = "default"

# Password for the account.
password = "qQptnG6nRLpM30yu"

# Connection host.
host = host_url.replace("<password>", password)
