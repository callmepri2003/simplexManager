import { useState } from "react";
import { newLesson } from "../../../services/api";


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
      date: formData.date
    };
    
    const result = await newLesson(lessonData);
    
    // Reset form after successful submission
    setFormData({ date: '' });
    setUpdatedLessons(prev => [...prev, lessonData]);
  } catch (error) {
    console.error('Error creating lesson:', error);
  } finally {
    setIsSubmitting(false);
  }
};

export const setMultipleFiles = (multipleFiles) => {
  setFormData(prev => ({
    ...prev,
    multipleFiles
  }));
}