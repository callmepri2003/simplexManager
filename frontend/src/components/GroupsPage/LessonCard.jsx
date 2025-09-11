import { useState } from "react";

export default function LessonCard({ lesson }) {

  const [changed, setChanged] = useState(false);

  const standardiseAttendanceData = (all_students, attendances) => {
    const newAttendanceData = {};

    all_students.forEach(student => {
      const isPresent = attendances.some(a => {
        return a.student_info.display_name === student.display_name;
      });
      newAttendanceData[student.id] = {...student}
      newAttendanceData[student.id].present = isPresent;
    });
    return newAttendanceData;
  };

  const [attendanceData, setAttendanceData] = useState(
    standardiseAttendanceData(lesson.all_students, lesson.attendances)
  );

  const toggleAttendance = (display_name) => {
    const newAttendanceData = { ...attendanceData };

    Object.values(attendanceData).forEach(student => {
      if (student.display_name === display_name) {
        newAttendanceData[student.id].present = !newAttendanceData[student.id].present;
      }else{
      }
    });
    setAttendanceData(newAttendanceData);
  };


  return (
    <div style={{width:"100%"}} key={lesson.id} className="d-flex mb-4">
      {/* Timeline dot */}
      <div className="d-flex flex-column align-items-center me-3">
        <div
          className="bg-primary rounded-circle"
          style={{ width: "12px", height: "12px" }}
        ></div>
        <div
          className="flex-grow-1 bg-secondary opacity-25"
          style={{ width: "2px" }}
        ></div>
      </div>

      {/* Lesson Card */}
      <div
        className="p-3 border rounded-3 shadow-sm bg-light flex-grow-1 position-relative">
        {/* Date */}
        <h6 className="fw-bold mb-2">
          {lesson.date
            ? new Date(lesson.date).toLocaleDateString("en-GB", {
                weekday: "long",
                day: "numeric",
                month: "short",
                year: "numeric",
              })
            : "No date"}
        </h6>

        {/* Resources */}
        {lesson.resources && lesson.resources.length > 0 && (
          <div className="mb-2">
            <small className="text-muted d-block">Resources</small>
            <div className="d-flex flex-wrap gap-2 mt-1">
              {lesson.resources.map((res, idx) => (
                <a
                  key={idx}
                  href={res.file_url || "#"}
                  className="badge bg-primary bg-opacity-75 text-decoration-none"
                >
                  {res.file_url
                    ? res.file_url.split("/").pop().split(".")[0]
                    : `Resource ${idx + 1}`}
                </a>
              ))}
            </div>
          </div>
        )}

        {/* Attendance */}
        <div className="mb-3">
          <small className="text-muted d-block mb-2">Attendance</small>
          <div className="d-flex flex-wrap gap-2">
            {console.log(attendanceData)}
            {Object.values(attendanceData).map((attendance) => {
              return <span
                data-cy={`student${attendance.id}`}
                key={attendance.id}
                className={`badge rounded-pill px-3 py-2 shadow-sm ${
                  attendance.present ? "bg-success" : "bg-primary"
                }`}
                style={{ cursor: "pointer", transition: "0.2s" }}
                onClick={() => toggleAttendance(attendance.display_name)}
              >
                {attendance.display_name}
              </span>
              })}

          </div>
        </div>

        {/* Notes */}
        {lesson.notes && (
          <p className="small text-muted mb-0">{lesson.notes}</p>
        )}

        {/* Save Button (appears only if changes were made) */}
        {changed && (
          <div className="d-flex justify-content-end mt-3">
            <button
              className="btn btn-success btn-sm shadow-sm"
              onClick={handleSubmit}
            >
              Save Attendance
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
