export default function StepCard({ step, title, description, children }) {
  return (
    <div className="card p-6">
      <div className="flex items-start gap-4">
        <div className="h-8 w-8 flex items-center justify-center rounded-full bg-indigo-600 text-white font-semibold">
          {step}
        </div>

        <div className="flex-1">
          <h3 className="text-lg font-medium">{title}</h3>
          <p className="text-sm text-gray-500 mb-4">
            {description}
          </p>

          {children}
        </div>
      </div>
    </div>
  );
}
