class DomainError(Exception):
    pass


class AIProviderError(DomainError):
    pass


class AgentFormatError(DomainError):
    pass
