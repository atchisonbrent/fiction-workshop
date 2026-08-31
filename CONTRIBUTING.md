# Contributing

Contributions to the workshop tooling and documentation are welcome when they
preserve the repository's publication boundary.

## Content boundary

Only submit material you have the right to distribute here.

Do not commit:

- derivative fiction based on a third party's characters, setting, terminology,
  or protected story world;
- copied or closely paraphrased passages from books, scripts, games, or other
  source works;
- confidential or unreleased manuscripts without the author's explicit consent;
- credentials, secret-bearing URLs, personal data, or local machine paths;
- model-provider plumbing, private review-session identifiers, or raw agent logs.

Original fiction belongs under `stories/<slug>/` and must include a per-story
`LICENSE.md` identifying its copyright owner and terms. The root MIT license does
not automatically apply to story content.

## Development checks

Before submitting a change:

```text
python3 -m unittest discover -s tests -v
python3 .hermes/skills/story-development/scripts/validate_story.py stories/<slug>
```

Run the validator for every story you changed. Do not edit an existing released
tree under `release-contracts/<id>/`; create a child release instead.

## Scope

Keep reusable procedure in the project-local skill and story facts in the story
directory. Re-gate before adding a database, retrieval service, publishing
pipeline, custom UI, unattended publication, or shared canon across story slugs.
