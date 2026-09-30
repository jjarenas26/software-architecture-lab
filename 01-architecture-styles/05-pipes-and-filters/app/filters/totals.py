from app.models import ProcessingContext


class CalculateTotalFilter:
    name = "calculate_total"

    def process(self, context: ProcessingContext) -> ProcessingContext:
        context.total = round(
            sum(
                item.quantity * item.unit_price
                for item in context.items
            ),
            2,
        )
        context.trace.append(self.name)
        return context
