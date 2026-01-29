const API_KEY = "demo-key-123"; // 🔑 TEMP

export const uploadTabular = async (file) => {
  const formData = new FormData();
  formData.append("file", file); // ✅ correct name

  const res = await fetch("http://127.0.0.1:8000/upload/tabular", {
    method: "POST",
    headers: {
      "x-api-key": API_KEY, // 🔥 THIS WAS MISSING
    },
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json();
    throw err;
  }

  return res.json();
};
