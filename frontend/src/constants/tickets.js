export const TICKET_STATUSES = [
  "New",
  "In Progress",
  "Waiting for User",
  "Resolved",
  "Closed",
];

export const TICKET_CATEGORIES = [
  "Phishing",
  "Social Engineering",
  "Password Security",
  "Data Loss Prevention",
  "Vulnerability",
  "Security Training",
  "Security Awareness",
  "Account Security",
  "Other",
];

export const TICKET_PRIORITIES = ["Critical", "High", "Medium", "Low"];

export const ASSIGNED_TEAMS = [
  "Business Awareness",
  "Human Risk Management",
  "Data Protection",
  "Vulnerability Management",
  "Security Operations",
  "Identity and Access Management",
];

export const DEPARTMENTS = [
  "Finance",
  "Human Resources",
  "Engineering",
  "IT",
  "Sales",
  "Marketing",
  "Operations",
  "Legal",
  "Customer Service",
  "Other",
];

export const SORT_OPTIONS = [
  {
    label: "Newest First",
    value: "created_at:desc",
    sort_by: "created_at",
    sort_order: "desc",
  },
  {
    label: "Oldest First",
    value: "created_at:asc",
    sort_by: "created_at",
    sort_order: "asc",
  },
  {
    label: "Ticket Number",
    value: "ticket_number:asc",
    sort_by: "ticket_number",
    sort_order: "asc",
  },
  {
    label: "Priority",
    value: "priority:desc",
    sort_by: "priority",
    sort_order: "desc",
  },
  {
    label: "Status",
    value: "status:asc",
    sort_by: "status",
    sort_order: "asc",
  },
  {
    label: "Category",
    value: "category:asc",
    sort_by: "category",
    sort_order: "asc",
  },
];

export function getSortOption(value) {
  return (
    SORT_OPTIONS.find((option) => option.value === value) || SORT_OPTIONS[0]
  );
}
