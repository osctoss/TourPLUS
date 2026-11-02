class DomainError(Exception):
    """Base exception for TourPlus AI domain logic."""
    pass


class FinancialCalculationError(DomainError):
    """Raised when an invalid budget or ledger operation occurs."""
    pass


class ClinicianGuidanceRequiredError(DomainError):
    """Raised when an action requires explicit clinician clearance."""
    pass
