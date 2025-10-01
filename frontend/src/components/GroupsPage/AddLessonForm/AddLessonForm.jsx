import { useState } from "react";
import Loading from "../../Loading";
import {handleInputChange, handleSubmit, setMultipleFiles} from './AddLessonFormHelper'
import AddLessonDateField from "./AddLessonDateField";
import { FileUploadField } from "./AddLessonUploadFile";

export default function AddLessonForm({ groupId, onCancel, setUpdatedLessons }) {
  const [formData, setFormData] = useState({
    date: '',
    multipleFiles: []
  });

  const [isSubmitting, setIsSubmitting] = useState(false);

  const isFormValid = formData.date.trim() !== '';

  return (
    <div className="card border-0 shadow-sm mb-4">
      <div className="card-body p-4">
        <div className="d-flex align-items-center mb-4">
          <div className="bg-success bg-opacity-10 rounded-circle p-2 me-3">
            <svg width="20" height="20" fill="currentColor" className="text-success" viewBox="0 0 16 16">
              <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>
              <path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z"/>
            </svg>
          </div>
          <h5 className="mb-0 fw-medium">Add New Lesson</h5>
        </div>

        <form onSubmit={(e)=>{handleSubmit(e, groupId, formData, setFormData, setIsSubmitting, setUpdatedLessons)}}>
          <AddLessonDateField 
            formData={formData} 
            handleInputChange={handleInputChange}
            setFormData={setFormData}
          />
          {/* Multiple Files Upload */}
          <FileUploadField
            files={formData.multipleFiles}
            onChange={setMultipleFiles}
            multiple={true}
            label="Multiple Files Upload"
            helperText="Upload as many files as you want"
          />

          {/* Form Actions */}
          <div className="d-flex gap-2 justify-content-end">
            <button
              type="button"
              className="btn btn-outline-secondary"
              onClick={onCancel}
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={!isFormValid || isSubmitting}
              data-cy="newLessonSubmit"
            >
              {isSubmitting ? (
                <>
                  <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  <Loading/>
                </>
              ) : (
                'Create Lesson'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}