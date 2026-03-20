import { useEffect, useState } from "react";
import { getUsers } from "../services/api";
import Table from "../components/Table";
import Loader from "../components/Loader";

export default function Users() {

  const [users, setUsers] = useState(null);

  useEffect(() => {
    getUsers()
      .then(res => setUsers(res.data))
      .catch(() => setUsers([]));
  }, []);

  if (!users) return <Loader />;

  return (
    <div>
      <h1>Users</h1>
      <Table data={users} />
    </div>
  );
}