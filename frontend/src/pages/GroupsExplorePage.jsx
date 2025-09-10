import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { RetrieveGroup } from "../services/api";
import LessonHistoryTimeline from "../components/GroupsPage/LessonHistoryTimeline";

export default function GroupsExplorePage() {
  const { id } = useParams();
  const [groupInformation, setGroupInformation] = useState(null);

  // Placeholder lesson history
  const [lessons, setLessons] = useState([
    {
      id: 1,
      date: "2025-09-03",
      resources: ["Lesson1-Notes.pdf", "Practice-Sheet.pdf"],
      attendance: [
        { name: "Alice", present: true, paid: true },
        { name: "Ben", present: false, paid: false },
        { name: "Chloe", present: true, paid: true },
      ],
      notes: "Introduced fractions and practiced with real-life examples.",
    },
    {
      id: 2,
      date: "2025-08-27",
      resources: ["Lesson2-Worksheet.pdf"],
      attendance: [
        { name: "Alice", present: true, paid: true },
        { name: "Ben", present: true, paid: false },
        { name: "Chloe", present: true, paid: true },
      ],
      notes: "Reviewed addition strategies. Ben asked for extra help.",
    },
  ]);

  useEffect(() => {
    async function fetchGroup() {
      try {
        const response = await RetrieveGroup(id);
        setGroupInformation(response.data);
      } catch (error) {
        console.error("Failed to fetch group:", error);
      }
    }

    fetchGroup();
  }, [id]);

  if (!groupInformation) return <div className="text-center p-5">Loading...</div>;

  return (
    <div className="container-fluid p-0">
      {/* Hero Section */}
      <div
        className="position-relative text-white"
        style={{
          backgroundImage: groupInformation.image_base64
            ? `url(data:image/jpeg;base64,${groupInformation.image_base64})`
            : "linear-gradient(135deg, #3f51b5, #5c6bc0)",
          backgroundSize: "cover",
          backgroundPosition: "center",
          minHeight: "280px",
        }}
      >
        <div className="bg-dark bg-opacity-50 w-100 h-100 d-flex flex-column justify-content-center align-items-center p-5">
          <h1 className="fw-bold display-5 mb-2">{groupInformation.course}</h1>
          <h5 className="fw-light">with {groupInformation.tutor}</h5>
          <span className="badge bg-light text-dark rounded-pill mt-2 px-3 py-2 shadow-sm">
            {groupInformation.weekly_time}
          </span>
        </div>
      </div>

      {/* Content Section */}
      <div className="container py-5">
        <div className="row g-5">
          {/* Left side - Key Details */}
          <div className="col-md-7">
            <h2 className="fw-semibold mb-4">Class Details</h2>
            <dl className="row mb-0">
              <dt className="col-sm-4">Lesson Length</dt>
              <dd className="col-sm-8">{groupInformation.lesson_length} hr(s)</dd>

              <dt className="col-sm-4">Associated Product</dt>
              <dd className="col-sm-8">{groupInformation.associated_product}</dd>

              <dt className="col-sm-4">Day of Week</dt>
              <dd className="col-sm-8">{groupInformation.weekly_time}</dd>

              <dt className="col-sm-4">Time of Day</dt>
              <dd className="col-sm-8">{groupInformation.time_of_day}</dd>
            </dl>
          </div>
          <LessonHistoryTimeline lessons={lessons}/>
        </div>
      </div>
    </div>
  );
}
