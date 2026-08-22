### First post

AI Agent for CI Fail Diagnosis
I'm trying to build an agent that finds the reason why CI run failed.

For that I am curious to know about how practitioners think when a CI run fails.

When a CI build fails and there are multiple potential causes, what’s the very first thing you inspect? Also, what’s your immediate mental checklist or set of suspicions when a pipeline turns red?
how do you usually determine whether it’s a genuine code issue versus just a flaky failure?
And at last how do you determine that I'm pretty much sure what's happening and there's not much value of additional searching.
Would love to hear how you all approach CI triage!

You're currently banned from this community and can't comment on posts.
Sorry, this post has been removed by the moderators of r/QualityAssurance.
Try posting to a community that's a better fit
r/cicd
This is a sub for Engineers, DevOps, Testers, PMs, and everyone else to discuss CI/CD best practices, tools, etc.
r/Everything_QA
Literally everything related to QA / Software Testing. QA Chat, Articles, Videos, Interviews, Training and so much more!
Repost to another community


1



4
Go to comments

Share
u/Meshyai avatar
Meshyai
•
Ad

Concept image to a usable 3D model, without opening a modeling app.
Sign Up
meshy.ai
Thumbnail image: Concept image to a usable 3D model, without opening a modeling app.
Sort by:

Best

Search Comments
Expand comment search
Comments Section
u/Useful_Calendar_6274 avatar
Useful_Calendar_6274
•
7d ago
You don't even need to know that. AI is really capable for a lot of things and it's just starting to trickle down even among tech workers. You can just point it to the pipeline leave it running and it knows what to do, spawn subagents and everything. It's just a matter of if you really want to spend unknown tokens on that.



1



Share

TocinoLips
•
7d ago
i usually start with the fisrt real error in the logs, then chjeck recent code changes. after that, rerun the same test unchanged, I start suspecting flakiness



### Second post 
r/azuredevops
•
7d ago
Elegant_Quantity_583

CI fail diagnosis
I'm trying understand in how practitioners think why their CI run fails

For that I am curious to know about how practitioners think when a CI run fails.

When a CI build fails and there are multiple potential causes, what’s the very first thing you inspect? Also, what’s your immediate mental checklist or set of suspicions when a pipeline turns red?
how do you usually determine whether it’s a genuine code issue versus just a flaky failure?
And at last how do you determine that I'm pretty much sure what's happening and there's not much value of additional searching.
Would love to hear how you all approach CI triage!

Repost to another community


0



5
Go to comments

Repost

Share

Promote Post
4.3K views
See More Insights
Join the conversation

Sort by:

Best

Search Comments
Expand comment search
Comments Section
u/mrhinsh avatar
mrhinsh
•
7d ago
This exact question was ask d yesterday https://www.reddit.com/r/azuredevops/s/7mBNKSJ5jG



2



Reply

Award

Share

asksstupidstuff
•
7d ago
Mostly i read the Error Message.

One by one for multiples



6



Reply

Award

Share

Rare_Significance_63
•
7d ago
+1



1



Reply

Award

Share

konkon_322
•
7d ago
Ctrl + F > error. And start reading from bottom xd



2



Reply

Award

Share

u/mikedensem avatar
mikedensem
•
6d ago
Look for anything you don’t control directly - such as an external Nuget package host.



1



Reply

Award

Share

Often you can find the issue by just looking in the gui for the error message. Your pipeline should be able to run locally (or its not a CI) in almost identical form to your build server.

So rerun and validate the pipeline locally, and check for errors.

If it passes locally then it's likely environmental. Pull the logs and have a look.

To be honest these days I give Claude the URL to the failed build and ask it to diagnose in the first instance. I have a skill that gets it to pull the logs, check for errors, run locally and isolate the issue. 🤷‍♂️

It can be significantly time-consuming, especially with round trips, to diagnose, fix, and verify pipelines. It's grunt work... And that's what your LLM is for.



### Third post
I_Agents
•
5d ago
Elegant_Quantity_583

What hidden states should an AI agent track when diagnosing CI failures?
Discussion
Hi, if a CI run fails, there can be multiple explanations, so over the past few days I've been researching what the agent needs to have that helps me diagnose the failing Continuous Integration run.

The agent first makes assumptions -----> searches for evidence -----> updates probability of each assumption ------->

At the end, the agent takes an action like

if very high confidence, then:
Ask the user to change the exact thing or to something specific.
If medium, then:
hold, ask for more search evidence if the value of information is greater,
If the low cost of being wrong is too high, then:
simply escalate to human

I have mapped out some hidden states. Here 'they are; they are not mutually exclusive, as a failing CI can be because of many reasons.

H_flaky → Basically, the test/system itself can behave nondeterministically

H_fault_revealing → The failure is actually revealing a real bug/regression

H_dependency_fault → something is wrong with a dependency

H_environment_fault → something in the execution environment is causing the failure

H_config_error → some CI/build/runtime configuration is wrong

H_shared_root_cause → Multiple failures may actually be coming from the same underlying cause

Each hypothesis has a probability that gets updated with evidence.

Can you spot any weaknesses in here ?
What hidden states did I not include?
Are these hidden states actionable?

I'd your honest opinion..

Not getting comments? Repost to another community
r/cicd
This is a sub for Engineers, DevOps, Testers, PMs, and everyone else to discuss CI/CD best practices, tools, etc.
r/devsecops
A community for DevSecOps practitioners. Not a place to try and sell something.
Repost to another community


2



2
Go to comments

Repost

Share

Promote Post
357 views
See More Insights
Join the conversation

Sort by:

Best

Search Comments
Expand comment search
Comments Section
u/Apprehensive-Run7844 avatar
Apprehensive-Run7844
•
5d ago
The shared root cause one feels like it belongs in a different layer than the others, more of a relationship between failures than a standalone cause.



### Fourth post

Go to LLMDevs
r/LLMDevs
•
5d ago
Elegant_Quantity_583

Building a CI-diagnosis agent — sanity check on the hidden states it tracks
Discussion
Shipping an agent that diagnoses why a CI run failed instead of leaving that to the human. Flow: hypothesize possible causes → search for evidence with tools → update probability per hypothesis → act based on confidence (recommend a specific fix if very confident, keep digging if medium confidence and it's worth it, hand off to a human if getting it wrong is expensive).

Hypotheses tracked right now (can overlap):

H_flaky — flaky test/system

H_fault_revealing — real bug

H_dependency_fault

H_environment_fault

H_config_error

H_shared_root_cause — one cause behind multiple failures

If you've built anything in this diagnostic-agent space: what's missing from this list, and does anything on it seem like it wouldn't actually be actionable once the agent is confident about it?

Repost to another community


2



7
Go to comments

Repost

Share

Promote Post
633 views
See More Insights
Join the conversation

Sort by:

Best

Search Comments
Expand comment search
Comments Section
u/CautionIAmAGeek avatar
CautionIAmAGeek
•
4h ago
H_flaky is worth tracking, but a flaky test is usually two states wearing one label: nondeterminism in the test (timing, shared fixtures, ordering) and nondeterminism around it (network, clock, seeded data). Collapsing them is how an agent ends up "fixing" a real bug by adding a wait. A cheap discriminator that works: rerun the same commit in isolation N times, then rerun it inside the full suite, and compare the two failure rates before you let the agent conclude anything. The other thing worth modeling is evidence per attempt (UI state, network calls, console) rather than a single confidence score, since a verdict you can inspect is the one people act on.



1



Reply

Award

Share

u/UWorldOfficial avatar
u/UWorldOfficial
•
Ad

Access up-to-date clinical articles that enhance your understanding and prepare you to make informed decisions swiftly.
medical.uworld.com
Thumbnail image: Access up-to-date clinical articles that enhance your understanding and prepare you to make informed decisions swiftly.
Designer_Piece7723
•
5d ago
I built something similar for our internal pipelines last year and the thing that tripped us up was not tracking "H_timing_race" separately, we kept having these failures that would disappear on retry but weren't flaky in the classic sense, they were actual race conditions in the test setup that only appeared under certain load patterns

also your H_environment_fault might be too broad, we split ours into image/container issues vs infra provisioning failures because the fix paths are completely different, one needs a rebuild and the other needs a cloud team ticket

what we added later was H_human_error which sounds dumb but turned out to be like 15% of our failures, someone pushed to the wrong branch or force-pushed over commits and the CI just did what it was told, the agent would spin forever looking for bugs that didn't exist

one thing I'm curious about, how does your agent handle when multiple hypotheses are correct simultaneously, like a real bug that only triggers because of a config error, we had some ugly cases where fixing just one thing would make the pipeline green but not actually solve the root problem



2



Reply

Award

Share

u/Elegant_Quantity_583 avatar
Elegant_Quantity_583
OP
•
4d ago
Thanks, your question opened my eyes; I spent the whole morning trying to figure out its answer, and now I have a different approach.

It's about first determining if it was a silly human mistake.

I have now divided the work into 2 agents:

First agent:
Finds if the CI run failure was caused by a silly human mistake like pushing to the wrong branch, etc.

Second agent:
Gets activated once the first agent confirms that it's not a silly problem.

However, two failures might not always have occurred at the same time, and some failures might be genuinely mutually exclusive. For instance, Hypothesis 1 and Hypothesis 2 can occur at the same time, but Hypothesis 1 and Hypothesis 3 cannot.

I shifted the goal from listing every possible edge case to constructing a set of individual hypotheses and joint hypotheses, while dropping those that are impossible or have a very low joint probability.

For some hypotheses, this assumes:
P(A and B) ≈ P(A) * P(B), while P(A ∩ B) is negligible or artificially assumed to be zero to create a baseline.

Now it has these hypotheses:

Hypothesis	Independent Belief
H_flaky_test	
H_timing_race	
H_fault_revealing	
H_dependency_fault	
H_config_error	
H_container_image_fault	
H_infra_provisioning_fault	
Kept edges (the only two co-occurrence relationships worth modeling explicitly):

Edge	Status
H_flaky_test — H_fault_revealing	Confirmed, cite Haben et al. 2023 (Section 9): ~1/3 of regression faults had flaky histories — real, measured, keep
H_timing_race — H_fault_revealing	Plausible, not yet confirmed. A race condition can itself be a genuine concurrency bug rather than a test artifact — reasoned by analogy from the row above, not independently measured.
Additional Notes:

H_container_image_fault × H_infra_provisioning_fault: These were split apart precisely because they have different owners/fixes (Section 12); no cited reason to expect them to co-occur more than chance. Treat as independent.

H_dependency_fault × H_config_error: Plausible on paper (a bad lockfile setting could look like either), but I found no CI-specific source establishing that these co-occur more than by chance.

Now the second job is to find the real cause. Do you find anything bad about this structure ?



2



Reply

Award

Share

6

u/Innowise_ avatar
Innowise_
•
5d ago
One thing we'd track separately is confidence in the diagnosis vs confidence that the agent has enough evidence. A failed test plus a matching log can make one hypothesis look very strong, but if the agent never checked the deploy diff or environment state, that confidence can be misleading. We'd only let it act automatically when both are high.



1



Reply

Award

Share

u/Elegant_Quantity_583 avatar
Elegant_Quantity_583
OP
•
4d ago
Good catch, and heads up in case you didn't see it I posted an update below where I split this into two agents (one just checks for silly human mistakes like a wrong-branch push, the second only activates once that's ruled out).

Your confidence-vs-evidence distinction is making me second-guess that split, though. Agent one could be confident it found a "silly mistake" without having checked enough to actually rule out a real bug underneath it—like a bad push that happens to coincide with an unrelated regression. Right now agent one has no signal for "I'm confident, but did I check enough?" before it decides not to hand off to agent two.

Would you track that evidence-completeness check as part of each agent, or as a separate gate that has to pass before either agent is allowed to act on its own confidence?

Could you please challenge me on this?



1



Reply

Award

Share

7

eddzsh
•
3d ago
Profile Badge for the Achievement Top 1% Commenter Top 1% Commenter
The confidence vs evidence completeness split is the right next cut.

One practical way to implement the gate: keep a required evidence checklist per hypothesis (log match, deploy diff, env fingerprint, last green commit). Confidence can only go high after every item on that checklist is filled or explicitly marked N/A with a reason. That stops agent one from short circuiting on a wrong branch push that happens to sit next to a real regression.

Also worth a separate H_stale_cache (CI caches, package caches, docker layer caches). It is not flaky and not a code bug, and the fix path is purge and rerun, not a patch.


### Fifth post
r/LLMDevs
•
1d ago
No-Cheetah-4745

How do you evaluate an AI agent that gives fuzzy, probabilistic outputs?
Discussion
I'm new to building AI agents and working on a CI-review agent: it takes a failing CI run and tries to find the root cause.

I want to start with a baseline version, then iterate on it — but I need a way to measure whether a new version is actually outperforming the old one.

Right now the agent maintains several hypotheses about the failure, assigns each a probability, and updates those probabilities as it gathers more information. Depending on its confidence, it either outputs a summary of the likely root cause, or escalates to a human developer if uncertainty is too high.

Two questions:

How do you evaluate an agent like this, where the output isn't a single "correct" answer but a probability distribution over hypotheses?

How do you get a labeled dataset of CI failures with known root causes, so I can score the agent's probability estimates against ground truth instead of just eyeballing whether the output "feels right"?

Repost to another community


3



13
Go to comments

Repost

Share

Promote Post
1.3K views
See More Insights
Join the conversation

Sort by:

Best

Search Comments
Expand comment search
Comments Section
u/Physical_Economy_340 avatar
Physical_Economy_340
•
1d ago
measure the ranking, not the probabilities. score top-k hit rate: is the real root cause inside the agent's top 1 or top 3 hypotheses, because that's what maps to 'did the summary name the right cause.' then score escalation as a classifier on its own: when it didn't escalate, how often was top-1 actually right, and when it did, was top-1 wrong. pick the confidence threshold off that curve so it trades wasted dev time against wrong auto-answers. and label ground truth at file or line granularity, a whole fix commit is too coarse, a wrong-but-plausible hypothesis will still 'match' it.



2



Reply

Award

Share

u/No-Cheetah-4745 avatar
No-Cheetah-4745
OP
•
1d ago
Thanks a lot for your pushback, now I'll ponder about this.
and I am thinking, when it comes to calculation of posterior, I look for the P(evidence | reality) , should I calculate it based on comparable evidence. like if I have a build log, should I look for other build logs that are comparable ?



1



Reply

Award

Share

23

u/Reasonable_Royal_621 avatar
Reasonable_Royal_621
•
1d ago
top-1 hit rate isn’t the interesting part here. whether the probability you assign to each hypothesis is actually calibrated is. those are two very different failure modes and most evals only check the first one.
use proper scoring rules instead of eyeballing it: log loss or Brier score against the true root cause, plus a calibration check. when the agent says 70% confidence, does it actually land on the right cause ~70% of the time? if it’s systematically over or under confident, your escalation threshold is wrong no matter how good top-1 looks.
and since escalation is baked into the design, plain accuracy doesn’t tell you much either. what you actually want is risk-coverage: “when the agent auto-resolves 80% of failures and punts the rest, what’s the error rate on that 80%?” plot that across thresholds and you can actually compare versions instead of eyeballing one operating point.
for labels, real CI failures rarely come with clean ground truth. mine your own history (failed build, then whatever commit or PR actually fixed it, filtering out flaky reruns), pull public GH Actions/Jenkins failures where the fix is confirmed in the PR discussion, or fault inject known failure types into a test repo for guaranteed labels (less realistic, but 100% clean).
one thing that’ll bite you later if you skip it now: lock down a fixed root cause taxonomy (dependency, compilation, test logic, env, flaky, regression, infra) before you iterate much further. otherwise your hypothesis space drifts between versions and the scores stop being comparable.
underlying thing across all of this: prediction score isn’t the same as decision correctness. calibration and escalation policy are two separate things to optimize, and conflating them is where most agent evals quietly go wrong.



2



Reply

Award

Share

u/No-Cheetah-4745 avatar
No-Cheetah-4745
OP
•
1d ago
•
Edited 1d ago
Thanks a lot for your pushback, now I'll ponder about this.
and I am thinking, when it comes to calculation of posterior, I look for the P(evidence | reality) , should I calculate it based on comparable evidence. like if I have a build log, should I look for other build logs that are comparable ?



1



Reply

Award

Share

16

u/weed_cutter avatar
weed_cutter
•
17h ago
Confidence is different than a probability spread. Just throwing that out here.

I can say I believe Trump has a 15% chance of being elected a 3rd term. ... And what is my confidence in that number I pulled out of my ass? 2%.

... The agent is assigning probabilities .... how it arrives at those may be independent or dependent but hopefully they all add up to 100%.

An agent can say "100% chance that there's a 10% chance of X .... as for Y and Z, fuck'd if I know"



1



Reply

Award

Share

GroundTiny9814
•
1d ago
eddzsh
•
1d ago
Profile Badge for the Achievement Top 1% Commenter Top 1% Commenter
Physical_Economy's top-k framing is right. One more split worth scoring on its own: the abstain path.

When the agent escalates, was top-1 wrong often enough that a human should have been pulled in. When it does not escalate, was top-1 right. That curve picks the confidence threshold better than calibrating the raw probabilities.

For labels, mine postmortems and reverted fixes at file or line grain, not whole green commits. A plausible wrong hypothesis will still match a big fix commit and lie to your eval.



1



Reply

Award

Share

Positive-Buddy-1258
•
23h ago
Fix commits as ground truth break down here: infra/env failures where the fix was a config change or a runner restart don't leave a meaningful diff to compare against. If you include those in your eval set, they look like "high uncertainty, correct escalation," but the agent didn't actually reason about root cause, it just punted. That silently inflates your escalation recall.

Keep a separate bucket for cases where there's no code-level ground truth and track them independently. Otherwise threshold tuning is working on the wrong signal.



1



Reply

Award

Share

leading-a-swarm
•
23h ago
Score the escalation decision separately from the root cause. Being wrong and being confidently wrong are different failures. We keep a frozen set of past failures with known causes, then measure top-1 hit rate plus calibration: of the cases it called 80%, was it right 80% of the time. Calibration moved our iterations more.



1



Reply

Award

Share

u/weed_cutter avatar
weed_cutter
•
17h ago
Probably an assortment of methods but ... one particular eval is obvious.

Group its likelihoods and analyze the actual distribution.

When it said there was a 50-60% chance of Monkey-based Fucky Wuckies .... how many of those cases actually turned out to be that? ... 30%? .... okay it's overzealous on that estimation. ... Turn that knob down.



1



Reply

Award

Share

u/Reasonable_Royal_621 avatar
Reasonable_Royal_621
•
11h ago
For #1, use a proper scoring rule like Brier score or log loss against ground truth, not accuracy. That way it actually rewards calibration, being confidently right, and punishes confidently wrong worse than “unsure and wrong.” Which matters since your escalate/no-escalate call depends on the model actually knowing when it doesn’t know.
I’d track three things separately instead of one score:
Calibration: when it says 70% confident, is it right ~70% of the time? Most agents are quietly overconfident here and a plain accuracy number won’t show it.

Discrimination: when it does commit, is the probability actually concentrated on the right hypothesis, or just spread out?

Escalation quality: treat “should I escalate” as its own little classifier and check precision/recall on that separately. Otherwise it’s too easy to game root-cause accuracy by just escalating more.

For #2, no shortcut here, but a few things that work:
Mine your own CI history if you have any, the fix commit / PR that resolved a past failure is basically free ground truth.

Grab public repos with CI + fix commits on GitHub, same idea, just needs a human pass since “the fix” isn’t always “the actual root cause.”

Synthetic injection (break things in known ways, flaky test, bad env var, dep bump) is the fastest way to get a cheap benchmark for iterating quickly, since you know the ground truth because you caused it.

I’d start with synthetic for fast iteration, then use the real mined data as your “does this actually work” holdout before shipping. Synthetic-only tends to make an agent good at exactly the bugs you thought to inject and blind to everything else.
Also worth watching: does its confidence move in the right direction as it gathers evidence, not just where it lands at the end. An agent that jumps to 90% on turn one and never budges is a different (worse) agent than one that converges properly, even if the final number looks the same.



1



Reply

Award

Share

### Sixth post
mlscaling
•
1d ago
No-Cheetah-4745

How do you evaluate an AI agent that gives fuzzy, probabilistic outputs?
I'm new to building AI agents and working on a CI-review agent: it takes a failing CI run and tries to find the root cause.

I want to start with a baseline version, then iterate on it — but I need a way to measure whether a new version is actually outperforming the old one.

Right now the agent maintains several hypotheses about the failure, assigns each a probability, and updates those probabilities as it gathers more information. Depending on its confidence, it either outputs a summary of the likely root cause, or escalates to a human developer if uncertainty is too high.

Two questions:

How do you evaluate an agent like this, where the output isn't a single "correct" answer but a probability distribution over hypotheses?

How do you get a labeled dataset of CI failures with known root causes, so I can score the agent's probability estimates against ground truth instead of just eyeballing whether the output "feels right"?

Not getting comments? Repost to another community

r/AIQuality
Join AI Quality, the go-to community for AI developers seeking to enhance the reliability and quality of their AI applications. Explore tools, share insights, and accelerate your development process with peer support and expert advice.

r/LLMDevs
A space for Enthusiasts, Developers and Researchers to discuss LLMs and their applications.
Repost to another community


2



2
Go to comments

Repost

Share

Promote Post
689 views
See More Insights
Join the conversation

Sort by:

Best

Search Comments
Expand comment search
Comments Section
Ty4Readin
•
1d ago
These are pretty basic questions that can be answered with simple machine learning theory and best practices.

You choose a loss function that works for this scenario. The most common and easily applicable would be the logloss cost function which I suggest you spend some time learning about as it is fundamentally the most important loss for classification problems like this.

You create it yourself somehow. Putting together a labelled dataset is probably the most important and most proprietary step to developing any useful model. You can scrape open source repos and manually inspect CI failures as one example of how to collect a dataset like this.



1



Reply

Award

Share

u/SettingAccording8986 avatar
SettingAccording8986
•
9h ago
Build yourself a controlled synthetic benchmark using fault injection, write a script to mess with versions in lockfiles, change ports in configs, break syntax in mocks , and feed those logs to the agent

Evaluating its real-world performance is better done with a cost matrix: the cost of a wrong diagnosis vs the developer time wasted when the agent pings them for no reason


