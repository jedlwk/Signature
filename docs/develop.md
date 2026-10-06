# Develop

How to test and change Signature.

## Contents
- Run the tests
- Release
- Change the voice

## Run the tests

```bash
python3 -m unittest discover -s tests -v
```

The tests check that my approved writing stays clean and AI-flavoured text gets flagged. They also
check that the docs pass the checker and that the skill follows Anthropic's authoring rules. Static
checks cover the plugin itself: the manifests agree, the hook points at a real script and the commands
are well formed. GitHub Actions runs all of it on every push.

## Release

Pushing a tag such as `v2.2.0` attaches a zip of the skill to a release, ready to upload to Claude.ai.

## Change the voice

To change the voice, edit the matching file in `references/` and keep `SKILL.md` short. Then bump
`version` in `.claude-plugin/plugin.json`, add a line to the changelog, and run
`/plugin marketplace update signature`. When I correct the same thing twice, it goes into the guide.
The [evals](../evals/README.md) show whether the change helped.
