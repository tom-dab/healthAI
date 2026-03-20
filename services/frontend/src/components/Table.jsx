export default function Table({ data }) {

  if (!data || !data.length) return <p>No data</p>;

  const keys = Object.keys(data[0]);

  return (
    <table style={{
      width: "100%",
      borderCollapse: "collapse",
      background: "#fff"
    }}>
      <thead>
        <tr>
          {keys.map(k => (
            <th key={k} style={{ borderBottom: "1px solid #ccc", padding: "10px" }}>
              {k}
            </th>
          ))}
        </tr>
      </thead>

      <tbody>
        {data.map((row, i) => (
          <tr key={i}>
            {keys.map(k => (
              <td key={k} style={{ padding: "10px" }}>
                {row[k]}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}