from enum import Enum


class TicketCategory(str, Enum):
    PHISHING = "Phishing"
    SOCIAL_ENGINEERING = "Social Engineering"
    PASSWORD_SECURITY = "Password Security"
    DATA_LOSS_PREVENTION = "Data Loss Prevention"
    VULNERABILITY = "Vulnerability"
    SECURITY_TRAINING = "Security Training"
    SECURITY_AWARENESS = "Security Awareness"
    ACCOUNT_SECURITY = "Account Security"
    OTHER = "Other"


class TicketPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class TicketStatus(str, Enum):
    NEW = "New"
    IN_PROGRESS = "In Progress"
    WAITING_FOR_USER = "Waiting for User"
    RESOLVED = "Resolved"
    CLOSED = "Closed"


class AssignedTeam(str, Enum):
    BUSINESS_AWARENESS = "Business Awareness"
    HUMAN_RISK_MANAGEMENT = "Human Risk Management"
    DATA_PROTECTION = "Data Protection"
    VULNERABILITY_MANAGEMENT = "Vulnerability Management"
    SECURITY_OPERATIONS = "Security Operations"
    IDENTITY_AND_ACCESS_MANAGEMENT = "Identity and Access Management"


class Department(str, Enum):
    FINANCE = "Finance"
    HUMAN_RESOURCES = "Human Resources"
    ENGINEERING = "Engineering"
    IT = "IT"
    SALES = "Sales"
    MARKETING = "Marketing"
    OPERATIONS = "Operations"
    LEGAL = "Legal"
    CUSTOMER_SERVICE = "Customer Service"
    OTHER = "Other"
