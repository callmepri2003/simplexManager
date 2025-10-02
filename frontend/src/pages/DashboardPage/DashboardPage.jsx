import GroupsCard from "../../components/GroupsPage/GroupsCard";
import Loading from "../../components/Loading"
import { useGetAllGroups } from "../../services/api"
import getClosestLesson from "./getClosestLesson"

export default function DashboardPage(){
  const [groups, loading, error] = useGetAllGroups();

  if(loading) return <Loading/>

  return (<div>
    <h2>Dashboard</h2>
    <GroupsCard {...getClosestLesson(groups)} />
  </div>)
}