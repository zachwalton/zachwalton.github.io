---
layout: post
title: TCP health checks for postgres
date:   2016-12-08 15:30:00 -0700
#categories: blog
---

We had a need to health check postgres in an environment that didn't have a client available. It's difficult to figure out a way to do this from the [protocol documentation](https://www.postgresql.org/docs/9.6/static/protocol-overview.html#PROTOCOL-MESSAGE-CONCEPTS), and not much fun to derive from [libpq's source code](https://github.com/postgres/postgres/tree/master/src/interfaces/libpq) either.

Usefully for us, haproxy [has a functional protocol-level health check](https://github.com/haproxy/haproxy/blob/master/src/cfgparse.c#L4864-L4923), but it's written in C, which necessitates factoring it out into a client: exactly what we were trying to avoid.

So here is haproxy's postgres health check refactored as a bash one-liner (4-liner?):

{% highlight bash %}
test "$(
  echo -ne "\x00\x00\x00\x17\x00\x03\x00\x00user\x00username\x00\x00" |
  nc -w 3 postgres-server.your-company.com 5432 2>/dev/null | head -c1
)" == "R"
{% endhighlight %}

Breaking this down:

{% highlight bash %}
# Postgres protocol version 3 (as uint32)
PROTOCOL_VERSION="\x00\x03\x00\x00"
# "user" command; specifies user to authenticate as
COMMAND="user"
# Username to authenticate as
USERNAME="username"

# Calculate the packet length
PACKET_SIZE="\x00\x00\x00\x$(printf '%02x' $((
  4 +
  ${#PROTOCOL_VERSION} / 4 +
  ${#COMMAND} +
  1 +
  ${#USERNAME} +
  2
)))"

NC_TIMEOUT=3

POSTGRES_SERVER=postgres-server.your-company.com
POSTGRES_PORT=5432


test "$(
  echo -ne "${PACKET_SIZE}${PROTOCOL_VERSION}${COMMAND}\x00${USERNAME}\x00\x00" |
  nc -w $NC_TIMEOUT $POSTGRES_SERVER $POSTGRES_PORT 2>/dev/null | head -c1
)" == "R"
{% endhighlight %}

And finally as a function:

{% highlight bash %}
function pgping() {
  help_flags=(help -h --help)
  if [[ ${help_flags[*]} =~ "$1" ]] || ([ -z "$1" ] || [ -z "$2" ]); then
    echo "usage:"
    echo
    echo "pgping <server> <port> [<username>]"
    return 0
  fi

  PROTOCOL_VERSION="\x00\x03\x00\x00"
  COMMAND="user"

  NC_TIMEOUT=3

  POSTGRES_SERVER=$1
  POSTGRES_PORT=$2
  if [ ! -z "$3" ]; then
    USERNAME=$3
  else
    USERNAME="username"
  fi

  PACKET_SIZE="\x00\x00\x00\x$(printf '%02x' $((
    4 +
    ${#PROTOCOL_VERSION} / 4 +
    ${#COMMAND} +
    1 +
    ${#USERNAME} +
    2
  )))"

  test "$(
    echo -ne "${PACKET_SIZE}${PROTOCOL_VERSION}${COMMAND}\x00${USERNAME}\x00\x00" |
    nc -w $NC_TIMEOUT $POSTGRES_SERVER $POSTGRES_PORT 2>/dev/null | head -c1
  )" == "R"

  if [ $? -eq 0 ]; then
    echo "health check passed"
    return 0
  else
    echo "health check failed"
    return 1
  fi
}

$ pgping -h
usage:

pgping <server> <port> [<username>]
$ pgping postgres-server.your-company.com 5432
health check passed
$ pgping postgres-server.your-company.com 5432 your_username
health check passed
$ pgping 169.254.0.1 12345
health check failed
{% endhighlight %}

It turns out that at least for protocol version 3, any username will pass this health check; so it should be fine to copy/paste the one-liner, which saves you the trouble of managing a valid username. But for "correctness", you can use your own if desired as illustrated above.
