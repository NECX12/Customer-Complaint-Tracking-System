export default function LoadingSpinner({ text = 'Loading...' }: { text?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-4">
      <div className="relative">
        <div className="w-10 h-10 rounded-full border-2 border-gray-700" />
        <div className="absolute inset-0 w-10 h-10 rounded-full border-2 border-transparent border-t-blue-500 animate-spin" />
      </div>
      <p className="text-sm text-gray-500 font-medium">{text}</p>
    </div>
  );
}
