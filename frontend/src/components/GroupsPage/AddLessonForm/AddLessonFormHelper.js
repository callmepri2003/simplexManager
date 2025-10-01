import { useState } from "react";
import { newLesson, newResources } from "../../../services/api";


export const handleInputChange = (field, value, setFormData) => {
  setFormData(prev => ({
    ...prev,
    [field]: value
  }));
};

export const handleSubmit = async (e, groupId, formData, setFormData, setIsSubmitting, setUpdatedLessons) => {
  e.preventDefault();
  
  if (!formData.date) {
    return;
  }
  setIsSubmitting(true);
  
  try {
    const lessonData = {
      group: groupId,
      date: formData.date,
      files: formData.multipleFiles
    };

    // send FormData
    const resultNewLesson = await newLesson(lessonData);
    

    formData.multipleFiles.forEach((file, idx) => {
      const bulkFormData = new FormData();
      bulkFormData.append(`file`, file);
      bulkFormData.append(`lesson`, resultNewLesson.data.id);
      bulkFormData.append(`name`, file.name);
      newResources(bulkFormData);
    });

    
    // Reset form after successful submission
    setFormData({ 
      date: '',
      files: []
     });
    setUpdatedLessons(prev => [...prev, lessonData]);
  } catch (error) {
    console.error('Error creating lesson:', error);
  } finally {
    setIsSubmitting(false);
  }
};