import { useEffect, useState } from "react";
import GroupsCard from "../components/GroupsPage/GroupsCard";
import { useGetAllGroups } from "../services/api";
import styled from "styled-components";

export default function GroupsPage() {

  const [groups, loading, error] = useGetAllGroups();

  if (loading) return <p>Loading groups...</p>;
  if (error) return <p>Error: {JSON.stringify(error)}</p>;
  
  return (
    <>
      <div className="row">
        {groups.map((g) => (
          <div key={g.id} className="groupsCardContainerIndividual col-lg-3 col-md-6 col-sm-12"
          style={{
            display: "flex",
            justifyContent:"center",
          }}>
            <GroupsCard key={g.id} {...g} />
          </div>
        ))}
      </div>
        
    </>
  );
}
