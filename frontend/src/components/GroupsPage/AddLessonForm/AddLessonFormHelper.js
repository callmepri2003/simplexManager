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
      resources: []
    };

    const resultNewLesson = await newLesson(lessonData);
    
    const uploadPromises = formData.multipleFiles.map((file) => {
      const bulkFormData = new FormData();
      bulkFormData.append('file', file);
      bulkFormData.append('lesson', resultNewLesson.data.id);
      bulkFormData.append('name', file.name);
      return newResources(bulkFormData);
    });

    const results = await Promise.all(uploadPromises);
    
    lessonData.resources = results.map(result => result.data);
    
    setFormData({ 
      date: '',
      files: []
    });

    console.log(lessonData.resources);

    setUpdatedLessons(prev => [...prev, lessonData]);
  } catch (error) {
    console.error('Error creating lesson:', error);
  } finally {
    setIsSubmitting(false);
  }
};