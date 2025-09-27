import { newLesson, newResources, postBulkAttendances } from "../../services/api";

export const newLessonSubmit = (formData, lessons, setLessons, groupId)=>{
  try{
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
      const fileFormData = new FormData();
      const frontendFileObj = {}

      formData.resources.forEach((resource) => {
        console.log(resource.name);
        fileFormData.append("name", resource.name);
        frontendFileObj.name = resource.name;
        fileFormData.append("file", resource.file);
        frontendFileObj.file = resource.file;
        frontendFileObj.id = Math.random();
        frontendFileObj.lesson = lesson.id;
        console.log(frontendFileObj);
      });
      fileFormData.append("lesson", lesson.data.id);
      let newLessonData = lesson.data;
      newLessonData.resources.push(frontendFileObj);
      setLessons((prev) => [...prev, newLessonData]);
      newResources(fileFormData);
      
    });
  } catch (err) {
    console.error("Error creating new lesson:", err);
  }
    
}