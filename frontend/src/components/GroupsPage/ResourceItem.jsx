import { useGetFileUrl } from "../../services/api";

export function ResourceItem({ resource }) {
  const [fileUrl, loading, error] = useGetFileUrl(resource.file);
  if (loading) return <span className="badge bg-secondary">Loading...</span>;
  if (error) return <span className="badge bg-danger">Error</span>;
  return (
    <a href={fileUrl} target="_blank" rel="noopener noreferrer" className="badge bg-info text-decoration-none">
      {resource.name || 'Resource'}
    </a>
  );
}