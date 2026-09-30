import pytest

from app.filters.fraud import FraudDetectionFilter
from app.filters.normalization import NormalizationFilter
from app.filters.persistence import PersistenceFilter
from app.filters.totals import CalculateTotalFilter
from app.filters.validation import ValidationFilter
from app.models import (
    DraftItem,
    FraudReviewRequired,
    ProcessingContext,
)
from app.pipeline import Pipeline
from app.repository import InMemoryProcessedOrderRepository


def build_extended_pipeline(
    threshold: float,
) -> tuple[Pipeline, InMemoryProcessedOrderRepository]:
    repository = InMemoryProcessedOrderRepository()

    pipeline = Pipeline(
        [
            ValidationFilter(),
            NormalizationFilter(),
            CalculateTotalFilter(),
            FraudDetectionFilter(review_threshold=threshold),
            PersistenceFilter(repository),
        ]
    )

    return pipeline, repository


def test_fraud_filter_can_be_inserted_without_changing_existing_filters() -> None:
    pipeline, repository = build_extended_pipeline(threshold=100.0)

    context = ProcessingContext(
        customer_id=" c001 ",
        items=[
            DraftItem(
                product_id=" p001 ",
                quantity=2,
                unit_price=25.5,
            )
        ],
    )

    result = pipeline.execute(context)

    assert result.status == "PROCESSED"
    assert result.trace == [
        "validate",
        "normalize",
        "calculate_total",
        "fraud_detection",
        "persist",
    ]
    assert repository.find_by_id(result.order_id) is not None


def test_fraud_filter_can_stop_pipeline_before_persistence() -> None:
    pipeline, repository = build_extended_pipeline(threshold=100.0)

    context = ProcessingContext(
        customer_id="C001",
        items=[
            DraftItem(
                product_id="P001",
                quantity=2,
                unit_price=75.0,
            )
        ],
    )

    with pytest.raises(FraudReviewRequired):
        pipeline.execute(context)

    assert context.total == 150.0
    assert context.trace == [
        "validate",
        "normalize",
        "calculate_total",
    ]
    assert context.order_id is None
    assert repository._orders == {}
