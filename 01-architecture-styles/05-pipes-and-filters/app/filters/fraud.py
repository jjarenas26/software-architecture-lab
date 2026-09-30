from app.models import FraudReviewRequired, ProcessingContext


class FraudDetectionFilter:
    name = "fraud_detection"

    def __init__(self, review_threshold: float) -> None:
        self.review_threshold = review_threshold

    def process(self, context: ProcessingContext) -> ProcessingContext:
        if context.total > self.review_threshold:
            raise FraudReviewRequired(
                f"order total {context.total:.2f} requires fraud review"
            )

        context.trace.append(self.name)
        return context
