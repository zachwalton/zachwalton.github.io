---
layout: post
title: why is httpd using so much memory, ffs?
date:   2015-10-27 12:31:00 -0700
categories: blog
---

let's find out.

first, take a look at the memory mappings consuming the most memory (PID 8833 is an httpd.worker instance):

{% highlight bash %}
$ grep Rss /proc/8833/smaps | sort -k2 -n | tail -1
Rss:              121752 kB
$ grep 121752 /proc/8833/smaps -B 5
...
7f3fa8000000-7f3faf6e7000 rw-p 00000000 00:00 0
...
{% endhighlight %}

generate a core file:

{% highlight bash %}
$ gcore 8833
Saved corefile core.8833
{% endhighlight %}

convert the beginning of the range to decimal, get the length of the range:

{% highlight bash %}
START_RANGE = 7f3fa8000000 == 139911378239488
END_RANGE = 7f3faf6e7000 == 139911502917632
DIFFERENCE = 124678144
OUTPUT_FORMAT = s # string
UNIT = b # bytes
{% endhighlight %}

dump that section of memory as a string:

{% highlight bash %}
$ gdb /opt/geo/httpd/sbin/httpd.worker core.8833 -ex "x/${DIFFERENCE}${OUTPUT_FORMAT}${UNIT} ${START_RANGE}" | grep -v \"\" | tee gdb.out
$ gdb /opt/geo/httpd/sbin/httpd.worker core.8833 -ex "x/124678144sb 139911378239488" | grep -v \"\" | tee gdb.out
{% endhighlight %}

inspect. in my case, it was an inefficient database query running in cron (via an HTTP endpoint) that was stacking up on prior queries, resulting in a slow (but substantial) memory leak.

{% highlight bash %}
$ grep SELECT gdb.out | wc -l
6927
{% endhighlight %}

