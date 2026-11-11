import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api";
import ScanResult from "../components/ScanResult";
import { ErrorBox, Spinner } from "../components/ui";

export default function ScanDetail() {
  const { id } = useParams();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  useEffect(() => { setData(null); api.scan(id).then(setData).catch((e) => setError(e.message)); }, [id]);
  return (
    <div>
      <p><Link to="/history">Back to scan history</Link></p>
      <ErrorBox error={error} />
      {!data && !error && <Spinner label="Loading scan" />}
      {data && <ScanResult key={data.scan_id} data={data} />}
    </div>
  );
}
