import { useEffect, useState } from "react";
import GroupsCard from "../components/GroupsPage/GroupsCard";
import { useGetAllGroups } from "../services/api";
import Loading from '../components/Loading'

export default function GroupsPage() {

  const [groups, loading, error] = useGetAllGroups();

  console.log(error);
  console.log(loading);
  
  return (
    <>
      <div className="row">
        {loading ? 
        (
          <>
            
            <Loading/>

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
