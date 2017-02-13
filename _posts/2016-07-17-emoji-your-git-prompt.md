---
layout: post
title: fill your git prompt with emoji
date:   2016-07-17 15:31:00 -0700
categories: blog
---

every programmer should consider it a duty to put emoji everywhere they can be rendered. i use [git-prompt.sh][git-prompt] to track my repo status, but by default it's a bit drab. luckily, it's pretty easy to spruce up.

[here's the emoji version.][git-prompt-emoji]

to install (note: only tested with bash, and will override existing `$PROMPT_COMMAND`):

{% highlight bash %}
curl -o ~/.git-prompt.sh https://gist.githubusercontent.com/zachwalton/c601a8057d1bf80aac1dc1215f7d9e45/raw/99862b8e30ac3d41662dffa927e5054ba4e72b51/git-prompt.sh
cat <<EOF | tee -a ~/.bash_profile
# load git prompt
. ~/.git-prompt.sh

export GIT_PS1_SHOWDIRTYSTATE=true
export GIT_PS1_SHOWUNTRACKEDFILES=true
export GIT_PS1_SHOWUPSTREAM=true

export PROMPT_COMMAND='__git_ps1'

EOF
{% endhighlight %}

your prompt should now look like this in git working directories:

![emoji prompt](/images/prompt.jpg)

key:

* 🚽 : unstaged (dirty)
* ⁉️ : untracked
* ✅ : staged
* 📬 : ahead of upstream
* 📪 : behind upstream
* 🆗 : synced upstream

enjoy!

[git-prompt]: https://github.com/git/git/blob/master/contrib/completion/git-prompt.sh
[git-prompt-emoji]: https://gist.github.com/zachwalton/c601a8057d1bf80aac1dc1215f7d9e45
