type Props = {
  loading: boolean;
  onSync: () => void;
  onProcess: () => void;
};

export default function ActionBar({ loading, onSync, onProcess }: Props) {
  return (
    <div className="flex gap-2">
      <button
        onClick={onSync}
        disabled={loading}
        className="text-sm px-4 py-2 rounded-lg border border-gray-200 text-gray-600 hover:bg-gray-50 disabled:opacity-50 transition-all"
      >
        {loading ? "Syncing..." : "↻ Sync"}
      </button>
      <button
        onClick={onProcess}
        disabled={loading}
        className="text-sm px-4 py-2 rounded-lg bg-gray-800 text-white hover:bg-gray-700 disabled:opacity-50 transition-all"
      >
        {loading ? "Processing..." : " Process"}
      </button>
    </div>
  );
}