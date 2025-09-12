import React, { useState } from 'react';
import {
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Box,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  OutlinedInput,
  Fade,
  IconButton,
  Alert,
} from '@mui/material';
import {
  Add as AddIcon,
  Close as CloseIcon,
  CloudUpload as CloudUploadIcon,
  Event as EventIcon,
  Notes as NotesIcon,
  People as PeopleIcon,
  AttachFile as AttachFileIcon,
} from '@mui/icons-material';

export default function NewLessonForm({ 
  all_students, 
  onSubmit, 
  onCancel, 
  isOpen,
}) {
  const [formData, setFormData] = useState({
    date: new Date().toISOString().split('T')[0],
    notes: '',
    selectedStudents: [],
    resources: []
  });

  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: null
      }));
    }
  };

  const handleStudentSelection = (event) => {
    const value = event.target.value;
    setFormData(prev => ({
      ...prev,
      selectedStudents: typeof value === 'string' ? value.split(',') : value
    }));
  };

  const handleFileUpload = (event) => {
    const files = Array.from(event.target.files);
    const newResources = files.map(file => ({
      name: file.name,
      file: file,
      id: Date.now() + Math.random()
    }));
    
    setFormData(prev => ({
      ...prev,
      resources: [...prev.resources, ...newResources]
    }));
  };

  const removeResource = (resourceId) => {
    setFormData(prev => ({
      ...prev,
      resources: prev.resources.filter(r => r.id !== resourceId)
    }));
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.date) {
      newErrors.date = 'Date is required';
    }
    
    if (formData.selectedStudents.length === 0) {
      newErrors.selectedStudents = 'At least one student must be selected';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    
    try {
      await onSubmit(formData);
      // Reset form after successful submission
      setFormData({
        date: new Date().toISOString().split('T')[0],
        notes: '',
        selectedStudents: [],
        resources: []
      });
    } catch (error) {
      console.error('Error creating lesson:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancel = () => {
    setFormData({
      date: new Date().toISOString().split('T')[0],
      notes: '',
      selectedStudents: [],
      resources: []
    });
    setErrors({});
    onCancel();
  };

  if (!isOpen) return null;

  return (
    <Fade in={isOpen} timeout={300}>
      <Card 
        elevation={2}
        sx={{ 
          mb: 3,
          borderRadius: 3,
        }}
      >
        <CardContent sx={{ p: 3 }}>

          <Box component="form" onSubmit={handleSubmit} noValidate>
            {/* Date Field */}
            <TextField
              fullWidth
              label="Lesson Date"
              type="date"
              value={formData.date}
              onChange={(e) => handleInputChange('date', e.target.value)}
              error={!!errors.date}
              helperText={errors.date}
              sx={{ mb: 3 }}
              InputLabelProps={{
                shrink: true,
              }}
              InputProps={{
                startAdornment: <EventIcon sx={{ mr: 1, color: 'action.active' }} />
              }}
            /> 

            {/* Student Selection */}
            <FormControl fullWidth sx={{ mb: 3 }} error={!!errors.selectedStudents}>
              <InputLabel>Select Students</InputLabel>
              <Select
                multiple
                value={formData.selectedStudents}
                onChange={handleStudentSelection}
                input={<OutlinedInput label="Select Students" />}
                startAdornment={<PeopleIcon sx={{ mr: 1, color: 'action.active' }} />}
                renderValue={(selected) => (
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {selected.map((studentId) => {
                      const student = all_students.find(s => s.id === studentId);
                      return (
                        <Chip 
                          key={studentId} 
                          label={student?.name || studentId}
                          size="small"
                          color="primary"
                          variant="outlined"
                        />
                      );
                    })}
                  </Box>
                )}
              >
                {all_students.map((student) => (
                  <MenuItem key={student.id} value={student.id}>
                    {student.name}
                  </MenuItem>
                ))}
              </Select>
              {errors.selectedStudents && (
                <Typography variant="caption" color="error" sx={{ mt: 1 }}>
                  {errors.selectedStudents}
                </Typography>
              )}
            </FormControl>

            {/* Notes Field */}
            <TextField
              fullWidth
              label="Lesson Notes"
              multiline
              rows={3}
              value={formData.notes}
              onChange={(e) => handleInputChange('notes', e.target.value)}
              placeholder="Add any notes about this lesson..."
              sx={{ mb: 3 }}
              InputProps={{
                startAdornment: <NotesIcon sx={{ mr: 1, color: 'action.active', alignSelf: 'flex-start', mt: 1 }} />
              }}
            />

            {/* File Upload */}
            <Box sx={{ mb: 3 }}>
              <Button
                component="label"
                variant="outlined"
                startIcon={<CloudUploadIcon />}
                sx={{ 
                  mb: 2,
                  borderRadius: 2,
                  textTransform: 'none',
                  '&:hover': {
                    transform: 'translateY(-1px)',
                    boxShadow: 2
                  }
                }}
              >
                Upload Resources
                <input
                  type="file"
                  hidden
                  multiple
                  onChange={handleFileUpload}
                />
              </Button>

              {formData.resources.length > 0 && (
                <Box>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    <AttachFileIcon sx={{ fontSize: 16, mr: 0.5 }} />
                    Attached Files:
                  </Typography>
                  <Box display="flex" flexWrap="wrap" gap={1}>
                    {formData.resources.map((resource) => (
                      <Chip
                        key={resource.id}
                        label={resource.name}
                        onDelete={() => removeResource(resource.id)}
                        color="secondary"
                        variant="outlined"
                        size="small"
                      />
                    ))}
                  </Box>
                </Box>
              )}
            </Box>

            {/* Action Buttons */}
            <Box display="flex" justifyContent="end" gap={2} pt={2}>
              <Button
                variant="outlined"
                onClick={handleCancel}
                disabled={isSubmitting}
                sx={{ 
                  borderRadius: 2,
                  textTransform: 'none',
                  minWidth: 100
                }}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="contained"
                disabled={isSubmitting}
                startIcon={<AddIcon />}
                sx={{ 
                  borderRadius: 2,
                  textTransform: 'none',
                  minWidth: 120,
                  '&:hover': {
                    transform: 'translateY(-1px)',
                    boxShadow: 4
                  }
                }}
              >
                {isSubmitting ? 'Creating...' : 'Create Lesson'}
              </Button>
            </Box>
          </Box>
        </CardContent>
      </Card>
    </Fade>
  );
}