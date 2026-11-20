# AGENTS.md

## Review and merge

- Small, modular code: one job per file; no source file over ~800 lines / 50 KB; new features in new modules.
- Small PRs: one area, about 500 changed lines or fewer (tests and pure moves excluded). Split bigger work into parts ("Part of #N"). Never widen a PR during review. Push after every commit. Bug fixes come with a failing-first test.
- Reviewer: Check Norris (`checknorrisbot[bot]`, status `checknorris`, green only at 5/5). It reviews ~10 quiet minutes after the last push (never push empty commits to trigger it). Commands: `@checknorrisbot review`, `@checknorrisbot re-review`, `@checknorrisbot rescore`.
- Findings (reply in the thread, mention first, one reply per thread):
  - real P0/P1: fix with a test, `@checknorrisbot Fixed in <sha> (<what changed>)`;
  - false positive: explain citing code;
  - minor P2: fix if small, else `@checknorrisbot Deferred to #N: <why minor>` into one `follow-up` issue per PR (`Follow-ups from #<PR>: <title>`). Answer every P2 before pushing again.
- Merge without asking when, on the current head commit, `checknorris` is green, every review thread is resolved and all checks are green: `gh pr merge <n> --merge --match-head-commit <sha>`. Never force-push shared branches, never `--delete-branch`.

## The Robots automation (ignore unless you are running inside a The Robots task)

hub-merge: on
hub-merge-requires: checknorris
