export default function ResultTable({ data }) {
  if (!data) return null;

  return (
    <div className="card p-6 mt-6">
      <h2 className="text-lg font-medium mb-4">
        Processed Output
      </h2>

      <pre className="bg-gray-900 text-green-400 p-4 rounded text-sm overflow-auto">
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
}
