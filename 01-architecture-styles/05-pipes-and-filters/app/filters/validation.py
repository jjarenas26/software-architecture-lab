from app.models import ProcessingContext, ValidationError


class ValidationFilter:
    name = "validate"

    def process(self, context: ProcessingContext) -> ProcessingContext:
        if not context.customer_id.strip():
            raise ValidationError("customer_id cannot be empty")

        if not context.items:
            raise ValidationError("order must contain at least one item")

        for item in context.items:
            if not item.product_id.strip():
                raise ValidationError("product_id cannot be empty")
            if item.quantity <= 0:
                raise ValidationError("quantity must be greater than zero")
            if item.unit_price < 0:
                raise ValidationError("unit_price cannot be negative")

        context.trace.append(self.name)
        return context
