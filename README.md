# Albany KDC site

A static page (no build step needed on Vercel). `index.html` is the finished page; `assets/` has the images.

## Deploy on Vercel

**Option 1: command line**
1. Install Node.js, then run `npm i -g vercel`.
2. In this folder, run `vercel` and answer the prompts (framework: Other, no build command, output directory: `.`).
3. Run `vercel --prod` to publish. Vercel prints your live link.

**Option 2: GitHub**
1. Put this folder in a GitHub repository.
2. In Vercel, choose Add New > Project, import the repository, set Framework Preset to Other, leave Build Command empty, and deploy.

## Change the schedule, locations or info

1. Edit `src/data.json`. Times look like `"2:05 PM"`. Activities listed with `"internal": true` stay hidden from parents.
2. Run `python3 src/build.py` (add your live address to also set share previews, for example `python3 src/build.py https://albany-kdc.vercel.app`).
3. The build stops and names the problem if a time, location or group is wrong.
4. Redeploy (`vercel --prod`, or push to GitHub).

## Testing event-day features

Add `#t1400` to the page link to pretend it is 2:00 PM on October 25 (24-hour HHMM). The Now / Next card and live marker only appear on October 25, 2026.

## Links into the page

`#schedule`, `#maps`, `#info`, an activity id such as `#a6`, or an area id such as `#gym`.
