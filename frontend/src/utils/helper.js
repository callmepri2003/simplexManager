export function formatDayAndTime(dayOfWeek, timeString) {
  const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
  
  // Parse the time string
  const [hoursStr, minutesStr] = timeString.split(":");
  let hours = parseInt(hoursStr, 10);
  const minutes = parseInt(minutesStr, 10);

  // Determine AM/PM
  const ampm = hours >= 12 ? "PM" : "AM";
  hours = hours % 12 || 12; // convert 0 -> 12, 13 -> 1, etc.

  // Format minutes (e.g., "00" instead of "0")
  const minutesFormatted = minutes.toString().padStart(2, "0");

  return `${days[dayOfWeek]}, ${hours}:${minutesFormatted} ${ampm}`;
}
