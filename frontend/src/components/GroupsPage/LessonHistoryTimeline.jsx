import { useState } from "react";
import LessonCard from "./LessonCard";
import NewLessonForm from "./NewLessonForm";
import { newLesson, postBulkAttendances } from "../../services/api";

export default function LessonHistoryTimeline({ lessons, all_students, groupId }){
  const [isOpen, setIsOpen] = useState(false);
  
  const newLessonSubmit = (formData)=>{
    console.log(formData);
    const lessonData = {
      "group": groupId,
      "notes": formData.notes
    }
    newLesson(lessonData).then((lesson)=>{
      const lessonAttendanceData = []
      formData.selectedStudents.forEach((student)=>{
        lessonAttendanceData.push({
          "lesson": lesson.data.id,
          "tutoringStudent": student
        })
      })
      postBulkAttendances(lessonAttendanceData)
    });

    
  }
  return <div className="col-md-5">
    <div className="p-4 border rounded-4 shadow-sm d-flex flex-column" style={{ maxHeight: "600px", overflowY: "auto" }}>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h4 className="fw-semibold mb-0">Lesson History</h4>
        <button 
        className="btn btn-sm btn-primary rounded-pill"
        onClick={()=>{setIsOpen(!isOpen)}}>
          + Add Lesson
        </button>
      </div>

      <div className="d-flex flex-column gap-4">
        <NewLessonForm
          all_students={all_students} 
          onSubmit={newLessonSubmit} 
          onCancel={()=>{console.log('cancelled')}}
          isOpen={isOpen}
          />
        {lessons.map((lesson) => (
          <div key={lesson.id} className="d-flex">
            <LessonCard lesson={lesson} all_students={all_students}/>
          </div>
        ))}

      </div>
    </div>
  </div>
}