export default function AddLessonDateField({ 
  formData, 
  handleInputChange,
  setFormData
}){
  return  (
    <div className="mb-3">
      <label htmlFor="lesson-date" className="form-label fw-medium text-muted">
        Lesson Date
      </label>
      <input
        id="lesson-date"
        type="datetime-local"
        className="form-control"
        value={formData.date}
        onChange={(e) => handleInputChange('date', e.target.value, setFormData)}
        data-cy="newLessonFormDateInput"
        required
      />
    </div>
  )
}