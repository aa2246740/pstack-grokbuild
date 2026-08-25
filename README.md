# pstack

i'm [poteto](https://x.com/poteto). i'm not a president or ceo, but i've worked with millions of lines of code at Meta, Netflix, and Cursor. i'm also on the react core team where i help build and maintain react compiler.

there's a growing sense that ai writes too much slop code. i agree. i don't want to ship like a team of twenty slop artists. throughput without quality is not a goal i aspire to. if you want to go fast, go deep first. 

this is pstack for [Grok Build](https://github.com/xai-org/grok-build). the 22 playbooks and 21 principles are [poteto's](https://x.com/poteto), from [official pstack](https://github.com/cursor/plugins/tree/main/pstack). harness calls use grok-build tools named in [HARNESS.md](./HARNESS.md).

**pstack is my answer.** these are the same skills used to ship high quality code. the goal is not to maximize loc, in fact it's the opposite. pstack helps you write less, but higher quality code.

**pstack gives you fearless parallelism.** when you can go deep on one agent and trust it to write good, verifiable code, you can truly parallelize with confidence. start with `poteto-mode` and trust that they'll apply rigorous engineering principles to their work.

**use the models you have.** every frontier model has its strengths and weaknesses. `/setup-pstack` maps roles onto slugs your `task` tool accepts.

fork it. improve it. make it yours. PRs are welcome! 

## install

```bash
grok plugin install aa2246740/pstack-grokbuild --trust
```

or from a local checkout:

```bash
grok plugin install /path/to/pstack-grokbuild --trust
```

then enable it (`grok plugin enable pstack` or Space in the Plugins tab). harness mapping: [HARNESS.md](./HARNESS.md).
