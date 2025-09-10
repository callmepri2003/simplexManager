import { useEffect, useState } from "react";
import GroupsCard from "../components/GroupsPage/GroupsCard";
import { AllGroups } from "../services/api";
import styled from "styled-components";

export default function GroupsPage() {
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const GroupsContainer = styled.div`

  `

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
      <div className="row">
        {groups.map((g) => (
          <div className="groupsCardContainerIndividual col-lg-3 col-md-4 col-sm-12">
            <GroupsCard key={g.id} {...g} />
          </div>
        ))}
      </div>
        
    </>
  );
}
