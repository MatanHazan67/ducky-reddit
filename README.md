# ducky-reddit

A single-user command-line helper for my own Reddit account (u/UnluckyDuckyDuck).
It runs locally on my Mac, authenticates with Reddit's script OAuth flow as my own
account only, and is triggered by hand. It has no other users and is not installed
in any subreddit.

It does three things, and nothing else:

| Command | What it does | Endpoint |
|---|---|---|
| `post` | Submits a post I wrote myself (title, body, subreddit, flair) | `POST /api/submit` |
| `history` | Lists my own submissions so I can respect each subreddit's posting cadence | `GET /user/<me>/submitted` |
| `inbox` | Shows my unread comment replies and messages so I can answer people promptly | `GET /message/unread` |

It does **not** read or store data about other users, comment or vote automatically,
monitor keywords, crawl subreddits, or send anything I have not written and reviewed.
Expected volume is under 100 requests per day.

## Setup

```
cp .env.example .env   # fill in client id, secret, username, password
python3 ducky.py history
python3 ducky.py inbox
python3 ducky.py post macapps "Title" --text-file post.md --flair "Promo"
```

## Data handling

- **What is read:** only my own account's data: my submissions (`/user/<me>/submitted`) and my unread inbox (`/message/unread`). No other user's profile, no subreddit listings, no search, no comment trees.
- **What is stored:** a local JSON cache of my own post dates and subreddit names, used to check posting cadence. Inbox items are printed to the terminal and not written to disk.
- **How it is displayed:** terminal output on my own machine, visible only to me. Nothing is republished, aggregated, or shared.
- **Deleted content:** nothing from other users is stored, so there is nothing to purge. If I delete one of my own posts, it drops out of the cache on the next `history` run.
- **Writes:** only `POST /api/submit`, only after an interactive confirmation prompt, only with text I wrote. No automated comments, votes, follows, or messages.
- **Identification:** User-Agent `macos:ducky-reddit:1.0 (by /u/UnluckyDuckyDuck)`, following Reddit's `<platform>:<app ID>:<version> (by /u/<username>)` format. No browser impersonation.
- **Rate limits:** the client reads `x-ratelimit-remaining` and sleeps until `x-ratelimit-reset` when it runs low. Expected load is under 100 requests per day.
- **Not done:** no AI or ML training on Reddit data, no inference about users, no commercial resale, no data leaves the machine.
