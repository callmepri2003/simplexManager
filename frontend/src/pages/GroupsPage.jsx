import { useEffect, useState } from "react";
import GroupsCard from "../components/GroupsPage/GroupsCard";
import { AllGroups } from "../services/api";

export default function GroupsPage() {
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchGroups() {
      try {
        const { data } = await AllGroups();
        setGroups(data);
      } catch (err) {
        setError(err.response?.data || "Error fetching groups");
      } finally {
        setLoading(false);
      }
    }

    fetchGroups();
  }, []);

  if (loading) return <p>Loading groups...</p>;
  if (error) return <p>Error: {JSON.stringify(error)}</p>;

  return (
    <>
      {groups.map((g) => (
        <GroupsCard key={g.id} {...g} />
      ))}
    </>
  );
}
