import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { useGetGroup } from "../../services/api";
import { formatDayAndTime } from "../../utils/helper";
import AddLessonForm from "./AddLessonForm/AddLessonForm";
import DeleteLessonBtn from "./DeleteBtn";

// Lessons Component
export default function LessonsSection({ groupId, lessons }) {
  const [updatedLessons, setUpdatedLessons] = useState(lessons);

  if (!updatedLessons || updatedLessons.length === 0) {
    return (
      <div className="text-center text-muted py-4">
        <AddLessonForm groupId={groupId} setUpdatedLessons={setUpdatedLessons}/>
        <p className="mb-0">No lessons available</p>
      </div>
    );
  }

  const formatLessonDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-AU', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };


  return (
    <div>
      <h2 className="fw-semibold mb-4">Lessons</h2>
      <AddLessonForm groupId={groupId} setUpdatedLessons={setUpdatedLessons}/>
      <div className="d-flex flex-column gap-3">
        {updatedLessons.map((lesson) => (
          <div key={lesson.id} className="card border-0 shadow-sm position-relative">            {/* Delete Button - appears on hover */}
            <DeleteLessonBtn data-cy={`deleteLessonBtn${lesson.id}`} lessonId={lesson.id} setUpdatedLessons={setUpdatedLessons}/>
            <div className="card-body p-4">
              {/* Date Header */}
              <div className="d-flex align-items-center mb-3">
                <div className="bg-primary bg-opacity-10 rounded-circle p-2 me-3">
                  <svg width="20" height="20" fill="currentColor" className="text-primary" viewBox="0 0 16 16">
                    <path d="M3.5 0a.5.5 0 0 1 .5.5V1h8V.5a.5.5 0 0 1 1 0V1h1a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V3a2 2 0 0 1 2-2h1V.5a.5.5 0 0 1 .5-.5zM1 4v10a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V4H1z"/>
                  </svg>
                </div>
                <div>
                  <h5 className="mb-0 fw-medium">{formatLessonDate(lesson.date)}</h5>
                </div>
              </div>

              {/* Notes Section */}
              {lesson.notes && lesson.notes.trim() && (
                <div className="mb-3">
                  <h6 className="text-muted mb-2 fw-medium">Notes</h6>
                  <p className="mb-0 text-secondary">{lesson.notes}</p>
                </div>
              )}

              {/* Resources Section */}
              {lesson.resources && lesson.resources.length > 0 && (
                <div>
                  <h6 className="text-muted mb-2 fw-medium">Resources</h6>
                  <div className="d-flex flex-column gap-2">
                    {lesson.resources.map((resource) => (
                      <a
                        key={resource.id}
                        href={resource.file}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="d-flex align-items-center text-decoration-none p-2 rounded bg-light hover-bg-primary hover-bg-opacity-10 transition-colors"
                        style={{ transition: 'background-color 0.2s ease' }}
                      >
                        <div className="me-2">
                          <svg width="16" height="16" fill="currentColor" className="text-danger" viewBox="0 0 16 16">
                            <path d="M4 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H4zm0 1h8a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1z"/>
                            <path d="M4.603 12.087a.81.81 0 0 1-.438-.42c-.195-.388-.13-.776.08-1.102.198-.307.526-.568.897-.787a7.68 7.68 0 0 1 1.482-.645 19.701 19.701 0 0 0 1.062-.33 2.08 2.08 0 0 0 .51-.19c.319-.23.595-.524.595-.96 0-.436-.275-.72-.686-.604-.436.124-.783.418-.783.418l-.48-.586s.472-.403 1.235-.684C8.692 6.193 9.73 6.756 9.73 8.195c0 1.439-.937 1.732-1.77 2.165-.664.345-1.077.71-1.077 1.643v.242H6.46c0-.02.012-.18.087-.36z"/>
                          </svg>
                        </div>
                        <span className="text-dark fw-medium">{resource.name}</span>
                        <div className="ms-auto">
                          <svg width="14" height="14" fill="currentColor" className="text-muted" viewBox="0 0 16 16">
                            <path fillRule="evenodd" d="M8.636 3.5a.5.5 0 0 0-.5-.5H1.5A1.5 1.5 0 0 0 0 4.5v10A1.5 1.5 0 0 0 1.5 16h10a1.5 1.5 0 0 0 1.5-1.5V7.864a.5.5 0 0 0-1 0V14.5a.5.5 0 0 1-.5.5h-10a.5.5 0 0 1-.5-.5v-10a.5.5 0 0 1 .5-.5h6.636a.5.5 0 0 0 .5-.5z"/>
                            <path fillRule="evenodd" d="M16 .5a.5.5 0 0 0-.5-.5h-5a.5.5 0 0 0 0 1h3.793L6.146 9.146a.5.5 0 1 0 .708.708L15 1.707V5.5a.5.5 0 0 0 1 0v-5z"/>
                          </svg>
                        </div>
                      </a>
                    ))}
                  </div>
                </div>
              )}

              {/* Empty state when no notes or resources */}
              {(!lesson.notes || !lesson.notes.trim()) && (!lesson.resources || lesson.resources.length === 0) && (
                <div className="text-muted text-center py-2">
                  <small>No additional content for this lesson</small>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}