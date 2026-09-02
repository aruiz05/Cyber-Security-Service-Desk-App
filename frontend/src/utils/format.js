const timezonePattern = /(?:Z|[+-]\d{2}:?\d{2})$/i;
const isoDateTimePattern = /^\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?$/;

export function normalizeUtcTimestamp(value) {
  if (!value) {
    return null;
  }

  if (value instanceof Date) {
    return value;
  }

  const timestamp = String(value).trim();

  if (!timestamp) {
    return null;
  }

  if (timezonePattern.test(timestamp)) {
    return timestamp;
  }

  if (isoDateTimePattern.test(timestamp)) {
    return `${timestamp}Z`;
  }

  return timestamp;
}

export function formatDateTime(value, fallback = "Not available") {
  const normalizedTimestamp = normalizeUtcTimestamp(value);

  if (!normalizedTimestamp) {
    return fallback;
  }

  const date = new Date(normalizedTimestamp);

  if (Number.isNaN(date.getTime())) {
    return fallback;
  }

  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(date);
}
