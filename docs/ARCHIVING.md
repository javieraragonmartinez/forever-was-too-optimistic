# Archiving and release procedure

The release is frozen only after all commands in `RELEASE.md` pass from a
clean checkout. The DOI `10.5281/zenodo.21460623` is reserved and remains
pending publication until the deposited files and their SHA-256 values have
been compared with this release.

A public archive should contain the source, the 43-page PDF, the elementary
certificate, the generator, independent verifier, JSON v2 artifact, schema,
manifest, citation metadata, licenses, tests, CI workflow and documentation.

The ZIP should be produced from the canonical Git commit with `git archive`,
not by manually compressing a working directory. The resulting ZIP receives
its own external SHA-256, which is intentionally not stored inside itself.
