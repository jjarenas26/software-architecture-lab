from app.models import ProcessingContext


class NormalizationFilter:
    name = "normalize"

    def process(self, context: ProcessingContext) -> ProcessingContext:
        context.customer_id = context.customer_id.strip().upper()

        for item in context.items:
            item.product_id = item.product_id.strip().upper()

        context.trace.append(self.name)
        return context
