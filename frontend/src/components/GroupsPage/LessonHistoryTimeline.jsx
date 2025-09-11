import LessonCard from "./LessonCard";

export default function LessonHistoryTimeline({ lessons }){
  
  return <div className="col-md-5">
    <div className="p-4 border rounded-4 shadow-sm d-flex flex-column" style={{ maxHeight: "600px", overflowY: "auto" }}>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h4 className="fw-semibold mb-0">Lesson History</h4>
        <button className="btn btn-sm btn-primary rounded-pill">
          + Add Lesson
        </button>
      </div>

      <div className="d-flex flex-column gap-4">
        {lessons.data?.lessons.map((lesson) => (
          <div key={lesson.id} className="d-flex mb-4">
            <LessonCard lesson={lesson}/>
          </div>
        ))}

      </div>
    </div>
  </div>
}