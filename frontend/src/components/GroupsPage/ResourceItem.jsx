export function ResourceItem({ resource }) {

  return (
    <a href={resource.file} target="_blank" rel="noopener noreferrer" className="badge bg-info text-decoration-none">
      {resource.name || 'Resource'}
    </a>
  );
}