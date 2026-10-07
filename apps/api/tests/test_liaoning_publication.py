"""Only synthetic fixture decisions are used; nothing is activated in the real intake."""

import pytest
from test_liaoning_inventory import approve, unit  # noqa: F401
from test_liaoning_inventory import workspace as workspace

from folkverse.liaoning_publication import publish, published_unit_evidence
from folkverse.liaoning_review import apply_reviews, draft


def test_pending_units_cannot_publish(workspace):
    draft(workspace, unit(workspace))
    with pytest.raises(ValueError, match="actually reviewed"):
        publish(workspace, ["intro-zh"])
    assert not published_unit_evidence(workspace)


def test_reviewed_unit_publication_preserves_attribution_and_withdraws_on_edit(workspace):
    original = unit(workspace)
    draft(workspace, original)
    apply_reviews(workspace, approve(workspace))
    publish(workspace, [original.id])
    evidence = published_unit_evidence(workspace)
    assert len(evidence) == 1 and evidence[0].evidence_origin == "reviewed_unit"
    assert evidence[0].text == original.text and evidence[0].reviewer == "Fixture Human"
    assert evidence[0].required_support_ids == [evidence[0].passage_id]
    draft(workspace, original.model_copy(update={"text": "Changed unreviewed wording"}))
    assert not published_unit_evidence(workspace)
