import { useEffect, useState } from "react";
import GroupsCard from "../components/GroupsPage/GroupsCard";
import { useGetAllGroups } from "../services/api";
import { Skeleton } from "@mui/material";

export default function GroupsPage() {

  const [groups, loading, error] = useGetAllGroups();

  if (error) return <p>Error: {JSON.stringify(error)}</p>;
  
  return (
    <>
      <div className="row">
        {loading ? 
        (
          <>
            
            <div className="groupsCardContainerIndividual col-lg-3 col-md-6 col-sm-12"
              style={{
                display: "flex",
                justifyContent:"center",
              }}>
              <Skeleton variant="rounded" width={310} height={450} />
            </div>
            <div className="groupsCardContainerIndividual col-lg-3 col-md-6 col-sm-12"
              style={{
                display: "flex",
                justifyContent:"center",
              }}>
              <Skeleton variant="rounded" width={310} height={450} />
            </div>
            <div className="groupsCardContainerIndividual col-lg-3 col-md-6 col-sm-12"
              style={{
                display: "flex",
                justifyContent:"center",
              }}>
              <Skeleton variant="rounded" width={310} height={450} />
            </div>

          </>
        ) :
        (
          groups.map((g) => (
            <div key={g.id} className="groupsCardContainerIndividual col-lg-3 col-md-6 col-sm-12"
            style={{
              display: "flex",
              justifyContent:"center",
            }}>
              <GroupsCard key={g.id} {...g} />
            </div>
          ))
        )}
      </div>
        
    </>
  );
}
