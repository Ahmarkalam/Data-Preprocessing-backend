export default function StatusBanner({ status }) {
  if (!status) return null;

  const isUp = status.toLowerCase().includes("running");

  return (
    <div
      className={`mb-6 rounded-lg px-4 py-3 text-sm font-medium
      ${isUp
        ? "bg-green-50 text-green-700 border border-green-200"
        : "bg-red-50 text-red-700 border border-red-200"}`}
    >
      Backend status: {status}
    </div>
  );
}
