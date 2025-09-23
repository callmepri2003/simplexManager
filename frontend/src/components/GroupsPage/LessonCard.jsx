import { useState } from "react";
import { postBulkAttendances } from "../../services/api";
import { ResourceItem } from "./ResourceItem";

export default function LessonCard({ lesson, all_students }) {

  const [changed, setChanged] = useState(false);

  const standardiseAttendanceData = (all_students, attendances) => {
    const newAttendanceData = {};
    all_students.forEach(student => {
      const isPresent = attendances.some(a => {
        return a.tutoringStudent === student.id;
      });
      newAttendanceData[student.id] = {...student}
      newAttendanceData[student.id].tutoringStudent = student.id;
      newAttendanceData[student.id].present = isPresent;
    });
    return newAttendanceData;
  };

  const [attendanceData, setAttendanceData] = useState(
    standardiseAttendanceData(all_students, lesson.attendances)
  );

  const toggleAttendance = (id) => {
    const newAttendanceData = { ...attendanceData };
    Object.values(attendanceData).forEach(student => {
      if (student.id == id) {
        newAttendanceData[student.id].present = !newAttendanceData[student.id].present;
      }
    });
    setAttendanceData(newAttendanceData);
    setChanged(true)
  };

  const handleSubmit = (lessonId) => {
    // POST (Bulk)

    const processedAttendanceData = [];
    Object.values(attendanceData).forEach((attendanceRecord)=>{
      attendanceRecord.lesson = lesson.id
      processedAttendanceData.push(attendanceRecord)
    })

    try {
      const result = postBulkAttendances(processedAttendanceData).then((result)=>{
        console.log("Saved:", result);
      });
      
    } catch (error) {
      console.error("Error saving:", error);
    }


  }
  
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
              {lesson.resources.map((resource) => {
                return <ResourceItem key={resource.id} resource={resource} />
              })}
            </div>
          </div>
        )}

        {/* Attendance */}
        <div className="mb-3">
          <small className="text-muted d-block mb-2">Attendance</small>
          <div className="d-flex flex-wrap gap-2">
            {Object.values(attendanceData).map((attendance) => {
              return <span
                data-cy={`student${attendance.id}`}
                key={attendance.id}
                id={attendance.id}
                present={attendance.present ? "true" : undefined}
                tutoringstudent = {attendance.tutoringStudent}
                className={`nametag lsn-${lesson.id} badge rounded-pill px-3 py-2 shadow-sm ${
                  attendance.present ? "bg-success" : "bg-primary"
                }`}
                style={{ cursor: "pointer", transition: "0.2s" }}
                onClick={() => toggleAttendance(attendance.id)}
              >
                {attendance.name}
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
              onClick={()=>handleSubmit(`lsn-${lesson.id}`)}
            >
              Save Attendance
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
