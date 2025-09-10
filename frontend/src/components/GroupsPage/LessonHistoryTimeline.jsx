export default function LessonHistoryTimeline({ lessons }){

  // Method to add a new lesson (simplified placeholder)
  const addLesson = () => {
    const newLesson = {
      id: lessons.length + 1,
      date: new Date().toISOString().split("T")[0], // today
      resources: ["NewLesson-Resource.pdf"],
      attendance: [
        { name: "Alice", present: true, paid: false },
        { name: "Ben", present: true, paid: false },
        { name: "Chloe", present: false, paid: false },
      ],
      notes: "New lesson added via form.",
    };
    setLessons([newLesson, ...lessons]); // prepend newest
  };
  return <div className="col-md-5">
    <div className="p-4 border rounded-4 shadow-sm d-flex flex-column" style={{ maxHeight: "600px", overflowY: "auto" }}>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h4 className="fw-semibold mb-0">Lesson History</h4>
        <button className="btn btn-sm btn-primary rounded-pill" onClick={addLesson}>
          + Add Lesson
        </button>
      </div>

      <div className="d-flex flex-column gap-4">
        {lessons.map((lesson) => (
          <div key={lesson.id} className="d-flex">
            {/* Timeline dot */}
            <div className="d-flex flex-column align-items-center me-3">
              <div className="bg-primary rounded-circle" style={{ width: "12px", height: "12px" }}></div>
              <div className="flex-grow-1 bg-secondary opacity-25" style={{ width: "2px" }}></div>
            </div>

            {/* Lesson Card */}
            <div className="p-3 border rounded-3 shadow-sm bg-light flex-grow-1">
              {/* Date */}
              <h6 className="fw-bold mb-2">
                {new Date(lesson.date).toLocaleDateString("en-GB", {
                  weekday: "long",
                  day: "numeric",
                  month: "short",
                  year: "numeric",
                })}
              </h6>

              {/* Resources */}
              <div className="mb-2">
                <small className="text-muted d-block">Resources</small>
                <div className="d-flex flex-wrap gap-2 mt-1">
                  {lesson.resources.map((res, idx) => (
                    <a
                      key={idx}
                      href="#"
                      className="badge bg-primary bg-opacity-75 text-decoration-none"
                    >
                      {res}
                    </a>
                  ))}
                </div>
              </div>

              {/* Attendance */}
              <div className="mb-2">
                <small className="text-muted d-block">Attendance</small>
                <div className="d-flex flex-wrap gap-2 mt-1">
                  {lesson.attendance.map((s, idx) => (
                    <span
                      key={idx}
                      className={`badge rounded-pill ${
                        s.present ? "bg-success" : "bg-secondary"
                      }`}
                    >
                      {s.name} {s.paid ? "💰" : "❌"}
                    </span>
                  ))}
                </div>
              </div>

              {/* Notes */}
              {lesson.notes && (
                <p className="small text-muted mb-0">{lesson.notes}</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  </div>
}