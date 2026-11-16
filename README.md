# Point-in-time earnings-call encoders: avoid look-ahead with a cutoff-aware count

## Named object
The object is `identifiers/calls.csv.gz` in the repository for *Point-in-Time Encoders for Earnings Calls* by Alessio Brini: https://github.com/Alessiobrini/point-in-time-encoders-for-earnings-calls . The repo says this file holds the identifiers of every call used to rebuild the corpus from WRDS, while the transcript text itself is not redistributed.

Use that file as the empirical anchor, not “earnings calls in general.” In RELAI terms: **Examine** the identifiers file, then **eXplain** what changes when a cutoff date is enforced.

## Stake
The stake is a standard backtest failure: if you train or retrieve with the full archive, you leak future transcripts into an earlier point in time. In an earnings-call setting, that leakage can move the apparent quality of retrieval, downstream question answering, and even forecasting comparisons. For economists, the issue is not cosmetic. A point-in-time panel is the difference between a believable evidence set and a wrong-number backtest.

## Naive path
The obvious mistake is to say: “the archive contains 412,248 calls, so that is the sample available on 2019-12-31.” That number is wrong. It uses the full archive instead of the cutoff-restricted archive, so it silently imports future calls into the earlier sample.

That is the failure mode the tutorial script checks. It prints the full count, the cutoff count, and the gap. **Probe** the gap before you trust any retrieval score.

## Technique
The technique is a small but important point-in-time audit:

1. Download the call-identifiers file from the paper’s GitHub repository.
2. Infer the most plausible date column from the headers.
3. Parse that column into datetimes.
4. Count how many calls are available on a chosen cutoff date.
5. Compare that number with the full archive count.

That is enough to expose the wrong-number path before you ever fit a model.

The RELAI sequence is deliberate:

- **Examine** the named object and its schema.
- **eXplain** the stake in one sentence: the wrong count contaminates a backtest.
- **Probe** fragility by changing the cutoff date.
- **Link to economics** by treating the archive as an information set dated by the call.
- **Output prediction** before you run the script: the cutoff count should be smaller than 412,248.
- **Recreate** with `python tutorial.py`.
- **Extend** by swapping the cutoff from a year-end date to an event-window date around an earnings season or Fed shock.

Primary sources:
- Brini, *Point-in-Time Encoders for Earnings Calls* (arXiv:2611.14325): https://arxiv.org/abs/2611.14325
- Repository with code and call identifiers: https://github.com/Alessiobrini/point-in-time-encoders-for-earnings-calls

## You will get this wrong
Economists usually miss one of four things on the first pass:

- They count the full archive and call it a historical sample.
- They forget that the choice of transcript version can change over time.
- They assume a retrieval gain is automatically a forecasting gain.
- They treat the point-in-time issue as a software detail instead of an identification problem.

If the cutoff count does not move when you change the date, your parser is wrong. If the full archive and cutoff count are the same, your sample filter is wrong.

## Controversy
The controversy is not whether look-ahead bias exists; it does. The argument is about how far point-in-time discipline should go and what it buys you. One camp wants vintaged encoders, vintaged corpora, and strict date filters everywhere. The other camp argues that many reported gains are mostly retrieval engineering, not new economic signal, and that the extra machinery is only worth it when the research design is genuinely time-stamped.

That disagreement is healthy. It is the right place to be skeptical, because a better-looking embedding can still be the wrong number if it saw tomorrow’s text.

## Recreate
Run the tutorial script to print the archive count, infer the date column, and compute the cutoff-restricted count.

```bash
python tutorial.py
```

The script uses the raw GitHub URL in code, so you do not need to hand-download anything.
