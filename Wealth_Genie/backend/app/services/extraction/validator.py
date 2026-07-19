from __future__ import annotations

from pydantic import ValidationError

from app.schemas_ext.financial import UniversalFinancialProfile


class FinancialJsonValidationError(ValueError):
    def __init__(self, validation_error: ValidationError | str):
        if isinstance(validation_error, ValidationError):
            self.validation_error = validation_error
            super().__init__(str(validation_error))
        else:
            self.validation_error = None
            super().__init__(validation_error)


def validate_business_rules(profile: UniversalFinancialProfile) -> None:
    """
    Business validation rules after Pydantic validation.
    """

    for account in profile.accounts:
        if (
            account.statement_period_start
            and account.statement_period_end
            and account.statement_period_start > account.statement_period_end
        ):
            raise FinancialJsonValidationError(
                "Statement period start cannot be after statement period end."
            )


def validate_financial_json(data: dict) -> UniversalFinancialProfile:
    """
    Validate the LLM JSON using Pydantic, then run deterministic business rules.
    """

    try:
        profile = UniversalFinancialProfile.model_validate(data)
    except ValidationError as exc:
        raise FinancialJsonValidationError(exc) from exc

    validate_business_rules(profile)

    return profile