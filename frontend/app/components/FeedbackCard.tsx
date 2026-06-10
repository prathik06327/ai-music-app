type FeedbackCardProps = {
  feedback: string;
};

export default function FeedbackCard({ feedback }: FeedbackCardProps) {
  return (
    <div className="bg-white p-5 rounded-lg shadow-sm border border-gray-200 text-gray-800 mt-4">
      <h3 className="text-xl font-semibold mb-3 text-indigo-700">AI Performance Review</h3>
      <p className="text-sm leading-6 whitespace-pre-line">{feedback}</p>
    </div>
  );
}
