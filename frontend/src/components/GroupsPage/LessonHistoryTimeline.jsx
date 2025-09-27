import { useState } from "react";
import LessonCard from "./LessonCard";
import NewLessonForm from "./NewLessonForm";
import { newLessonSubmit } from "./LessonHistoryTimelineHelper";

export default function LessonHistoryTimeline({ lessons, all_students, groupId }){
  const [isOpen, setIsOpen] = useState(false);
  const [localLessons, setLocalLessons] = useState(lessons)

  return <div className="col-md-5">
    <div className="p-4 border rounded-4 shadow-sm d-flex flex-column" style={{ maxHeight: "600px", overflowY: "auto" }}>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h4 className="fw-semibold mb-0">Lesson History</h4>
        <button 
        className="btn btn-sm btn-primary rounded-pill"
        onClick={()=>{setIsOpen(!isOpen)}}
        data-cy="addLesson">
          + Add Lesson
        </button>
      </div>

      <div className="d-flex flex-column gap-4">
        <NewLessonForm
          all_students={all_students} 
          onSubmit={(FormData)=>{
            setIsOpen(false);
            newLessonSubmit(FormData, localLessons, setLocalLessons, groupId);
          }}
          onCancel={()=>{console.log('cancelled')}}
          isOpen={isOpen}
          />
        {localLessons?
         localLessons.map((lesson) => (
          <div key={lesson.id} className="d-flex">
            <LessonCard lesson={lesson} all_students={all_students}/>
          </div>
        )):
         <div style={{textAlign: "center", color: "#e1e1e1"}}>
            <p>No lessons for this group.</p>
          </div>}

      </div>
    </div>
  </div>
}