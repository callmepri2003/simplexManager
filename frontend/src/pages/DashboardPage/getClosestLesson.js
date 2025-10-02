/**
 * Gets the closest lesson (in time) from an array of lessons
 * @param {Array} lessons - Array of lesson objects
 * @param {Date} referenceTime - Optional reference time (defaults to now)
 * @returns {Object|null} The closest lesson or null if array is empty
 */
export default function getClosestLesson(lessons, referenceTime = new Date()) {
  if (!lessons || lessons.length === 0) return null;

  // Helper to convert day_of_week and time_of_day to next occurrence Date
  const getNextOccurrence = (dayOfWeek, timeOfDay, fromDate) => {
    const [hours, minutes, seconds] = timeOfDay.split(':').map(Number);
    
    // Get current day (0 = Monday, 6 = Sunday)
    // Convert JS day (0 = Sunday) to your format (0 = Monday)
    const jsDay = fromDate.getDay();
    const currentDay = jsDay === 0 ? 6 : jsDay - 1;
    const currentTime = fromDate.getTime();
    
    // Calculate days until next occurrence
    let daysUntil = dayOfWeek - currentDay;
    
    // Create target date
    const targetDate = new Date(fromDate);
    targetDate.setDate(fromDate.getDate() + daysUntil);
    targetDate.setHours(hours, minutes, seconds, 0);
    
    // If the target time has already passed today (daysUntil === 0), move to next week
    if (targetDate.getTime() <= currentTime) {
      targetDate.setDate(targetDate.getDate() + 7);
    }
    
    return targetDate;
  };

  let closestLesson = null;
  let smallestDiff = Infinity;

  for (const lesson of lessons) {
    const nextOccurrence = getNextOccurrence(
      lesson.day_of_week,
      lesson.time_of_day,
      referenceTime
    );
    
    const timeDiff = nextOccurrence.getTime() - referenceTime.getTime();
    
    if (timeDiff < smallestDiff) {
      smallestDiff = timeDiff;
      closestLesson = {
        ...lesson,
        nextOccurrence,
        timeUntil: timeDiff
      };
    }
  }

  return closestLesson;
}