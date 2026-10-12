# Queue module

The queue serves your script its assets the way the labeling interface serves them to you: it asks
Kili for your next asset to label — or to review — and gets the one the interface would open for
you at that moment, with the same priorities, assignments and workflow step. The asset is then
yours, and nobody else's, until your script submits, skips, approves, sends back or releases it,
however long its work takes. People and scripts can work on the same project at the same time:
they are never handed the same asset, except on a consensus step, where each labels it once.

The queue belongs to the domain client, `kili.client_domain.Kili`, and works as the account of the
API key. Give your bot an account of its own: a member of the project, with the labeler role to
label or the reviewer role to review, assigned to the workflow steps it works on. When that
account cannot work on the queue — not a member, the wrong role, on no step — the queue raises a
`QueueError` that says why.

## A labeling bot

A complete bot that labels the documents of a classification project and stops when its queue is
empty. Documents it cannot classify are skipped with a reason, when the project lets its members
skip; any other failure gives the document back to the queue, then stops the bot.

```python
import os

from kili.client_domain import Kili
from kili.exceptions import QueueError

PROJECT_ID = os.environ["KILI_PROJECT_ID"]
kili = Kili(api_key=os.environ["KILI_BOT_API_KEY"])  # the bot's own account


def classify(text: str) -> str | None:
    """Your model: the document's category, or None when it cannot tell."""
    lowered = text.lower()
    if "invoice" in lowered:
        return "INVOICE"
    if "receipt" in lowered:
        return "RECEIPT"
    return None


labeled = skipped = 0
for asset in kili.queue.iter_to_label(project_id=PROJECT_ID):
    # the asset is the bot's until the end of this iteration, however long it takes
    category = classify(asset.read_content().decode("utf-8"))
    if category is None:
        try:
            asset.skip(reason="The bot could not tell what kind of document this is.")
            skipped += 1
        except QueueError:  # skipping not allowed on this project, or on this asset
            asset.release()  # back to the queue, for a person to label
        continue
    asset.submit(json_response={"CLASSIFICATION_JOB": {"categories": [{"name": category}]}})
    labeled += 1

print(f"Queue empty: {labeled} labeled, {skipped} skipped.")
```

What each line does, as in the labeling interface:

- `iter_to_label` hands the assets over one after another until the queue is empty — once Kili
  has had nothing for the bot five times in five seconds, as the queue page asks again before it
  greys out its button. Each asset is locked to the bot while the loop's body runs, and the lock is
  renewed in the background.
- `asset.content`, `asset.json_content` and `asset.metadata` hold the asset; `read_content()`
  downloads its file. `asset.label` holds the label the interface would open it with: the bot's own,
  when a reviewer sent the asset back for correction, or a model's prediction.
- `submit` creates the bot's label, with the time it held the asset, and moves the asset on in its
  workflow: to its next step, or done.
- `skip` skips the asset with a reason, as the interface's Skip: the asset leaves the queue —
  everyone's — until someone unskips it. It raises a `QueueError` where the interface would not
  skip: the project does not let its members skip, or the asset is on a consensus step or sent
  back for rework.
- `release` gives the asset back: the next member who asks is served it at once. An asset the
  loop's body leaves undecided is released too, and not served again in that loop.
- If the body raises, the asset is given back at once and the exception stops the loop.

## A review bot

```python
for asset in kili.queue.iter_to_review(project_id=PROJECT_ID):
    label = asset.label["json_response"]  # the label under review
    if is_right(label):
        asset.approve()  # approves the label as it is
    elif can_fix(label):
        asset.approve(json_response=fix(label))  # approves it with corrections
    else:
        asset.send_back()  # back to the labelers who made it
```

## One asset at a time

`next_to_label` and `next_to_review` hand over a single asset, or `None` when the queue is empty.
The asset stays yours until you act on it: use it as a context manager to give it back if your
code fails.

```python
asset = kili.queue.next_to_label(project_id=PROJECT_ID)
if asset is not None:
    with asset:  # given back if the block raises, or ends without a decision
        asset.submit(json_response=predict(asset))
```

An asset your code drops without acting on it is given back within 30 seconds, and the assets
still held when Python exits — the script's end, an exception, Ctrl-C — at once. A process killed
outright leaves its locks to expire, within 5 minutes.

`next_to_label` starts afresh each time, as the interface's Start Labeling does: an asset you just
released is the next one you are served again. The loops pass over the assets they gave back.

::: kili.domain_api.queue.QueueNamespace
::: kili.domain_api.queue.QueueAsset
::: kili.exceptions.QueueError
